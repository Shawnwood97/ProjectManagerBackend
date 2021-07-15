from flask import request, Response
import dbh
import json
import traceback
from datetime import datetime
import secrets
import hashlib
import rules

# Keeping it simple with account creation, just a simple email, username, password

# TODO we probably want to have the ability to find users based on project_id as well.


def create_user():
  arg_scheme = [
      {
          'required': True,
          'name': 'email',
          'type': str
      },
      {
          'required': True,
          'name': 'username',
          'rule': rules.username_checker,
          'type': str
      },
      {
          'required': True,
          'name': 'password',
          'rule': rules.password_checker,
          'type': str
      }
  ]
  parsed_args = dbh.input_handler(request.json, arg_scheme)

  if(parsed_args['success'] == False):
    return parsed_args['error']
  else:
    parsed_args = parsed_args['data']

  # create a salt for the password, add it to the beginning of the password, and hash it.
  salt = dbh.create_salt()
  parsed_args['password'] = salt + parsed_args['password']
  parsed_args['password'] = hashlib.sha512(
      parsed_args['password'].encode()).hexdigest()

  # params we will pass to the prepared statement.
  params = [parsed_args['email'], parsed_args['username'],
            parsed_args['password'], salt]

  # make sure value was passed since all are required.
  for param in params:
    if(param == "" or param == None):
      return Response("Missing required information!", mimetype="text/plain", status=422)

  # set sesult to the return of the run_query function
  result = dbh.run_query(
      "INSERT INTO users (email, username, password, salt) VALUES (?,?,?,?)", params)

  if(result['success'] == False):
    return result['error']

  # create a 45 Byte login_token and store it in a variable for use later.
  login_token = secrets.token_urlsafe(45)

  # insert user_id from the result return above, and the login token into the sessions table
  # will return the lastrowid to result_token['data']
  result_token = dbh.run_query("INSERT INTO sessions (user_id, token) VALUES (?,?)", [
                               result['data'], login_token])

  if(result_token['success'] == False):
    return result_token['error']

  # json dump for our response.
  new_user_json = json.dumps(
      {
          'id': result['data'],
          'email': parsed_args['email'],
          'username': parsed_args['username'],
          'login_token': login_token
      },
      default=str)
  # created reponse with data from above.
  return Response(new_user_json, mimetype="application/json", status=201)


def list_user():
  # only allow a single user_id to be passed, and it is mandatory.
  arg_scheme = [
      {
          'required': True,
          'name': 'user_id',
          'type': int
      }
  ]
  parsed_args = dbh.input_handler(request.args, arg_scheme)

  if(parsed_args['success'] == False):
    return parsed_args['error']
  else:
    parsed_args = parsed_args['data']

  result = dbh.run_query('SELECT id, u.username, u.email, u.status, u.avatar, u.created_at FROM users u WHERE u.id = ?', [
                         parsed_args['user_id'], ])

  # error check on above query
  if(result['success'] == False):
    return result['error']

  # if data key has data in it, len will == 1, since we only allow passing a single user_id and returning a single user
  # used index 0 in json dumps to return a dict of the 1 user, rather than a list of dicts, since it is just 1 user.
  if(len(result['data']) == 1):
    user_json = json.dumps(result['data'][0], default=str)
    return Response(user_json, mimetype='application/json', status=200)
  else:
    return Response("User not found!", mimetype="text/plain", status=404)


def update_user():
  # get required and optional data from user.
  arg_scheme = [
      {
          'required': True,
          'name': 'login_token',
          'type': str
      },
      {
          'required': False,
          'name': 'email',
          'type': str
      },
      {
          'required': False,
          'name': 'username',
          'rule': rules.username_checker,
          'type': str
      },
      {
          'required': False,
          'name': 'status',
          'type': str
      },
      {
          'required': False,
          'name': 'avatar',
          'type': str
      },
  ]
  # pass data through input_handler function from dbh file.
  parsed_args = dbh.input_handler(request.json, arg_scheme)

  # if helper function returns non successful, return error Response.
  # else set parsed args to the data key from parsed args for more readable code.
  if(parsed_args['success'] == False):
    return parsed_args['error']
  else:
    parsed_args = parsed_args['data']

  # base update sql statement
  sql = "UPDATE users u INNER JOIN sessions s ON u.id = s.user_id SET"
  # empty params list to append valid args to.
  params = []

  # if any args from above != None or an empty string, add to sql statement and append arg to params
  if(parsed_args.get('email') != None and parsed_args.get('email') != ''):
    sql += " u.email = ?,"
    params.append(parsed_args['email'])
  if(parsed_args.get('username') != None and parsed_args.get('username') != ''):
    sql += " u.username = ?,"
    params.append(parsed_args['username'])
  if(parsed_args.get('status') != None and parsed_args.get('status') != ''):
    sql += " u.status = ?,"
    params.append(parsed_args['status'])
  if(parsed_args.get('avatar') != None and parsed_args.get('avatar') != ''):
    sql += " u.avatar = ?,"
    params.append(parsed_args['avatar'])

  # if params has a length that is not 0, append login_token arg to params.
  # remove the trailing comma from the above sql blocks
  # add WHERE clause to sql statement.
  # else, auth error.
  if(len(params) != 0):
    params.append(parsed_args['login_token'])
    sql = sql[:-1]
    sql += " WHERE s.token = ?"
  else:
    return Response("Authorization Error!", mimetype="text/plain", status=403)

  # run the full query from above through run_query function and store it in the result variable
  # so we can do the error check below.
  result = dbh.run_query(sql, params)

  # check result variable to see if not successful.
  if(result['success'] == False):
    return result['error']

  # after success from above, get all user data for the endpoint to return.
  # TODO look back at this later and see how many other endpoints we use this in, maybe a helper function will make this more clean.
  updated_user_info = dbh.run_query(
      'SELECT u.id, u.email, u.username, u.status, u.avatar FROM users u INNER JOIN sessions s ON u.id = s.user_id WHERE s.token = ?', [parsed_args['login_token'], ])

  # error check for above statement.
  if(updated_user_info['success'] == False):
    return updated_user_info['error']

  # if length of the data key equals 1, create the json dump for the data key at index 0 (so it's a dict not a list.)
  # else error response, for getting users after update, since we know the update would have happened.
  if(len(updated_user_info['data']) == 1):
    user_info_json = json.dumps(updated_user_info['data'][0], default=str)
    return Response(user_info_json, mimetype="application/json", status=201)
  else:
    traceback.print_exc()
    return Response("Error getting user after update!", mimetype="text/plain", status=404)


def change_password():
  # TODO come back later and switch all current tokens to inactive on a password change for security.
  # get all required inputs for changing a password.
  arg_scheme = [
      {
          'required': True,
          'name': 'login_token',
          'type': str
      },
      {
          'required': True,
          'name': 'current_password',
          'type': str
      },
      {
          'required': True,
          'name': 'new_password',
          'rule': rules.password_checker,
          'type': str
      },
  ]
  parsed_args = dbh.input_handler(request.json, arg_scheme)

  if(parsed_args['success'] == False):
    return parsed_args['error']
  else:
    parsed_args = parsed_args['data']

  # select query for getting users salt and current password, based on token.
  result = dbh.run_query('SELECT u.salt, u.password FROM users u INNER JOIN `sessions` s ON u.id = s.user_id WHERE s.token = ?',
                         [parsed_args['login_token'], ])

  if(result['success'] == False):
    return result['error']

  # in this case, if run_query reutrns an empty data list, the login_token was invalid, therefor authorization error.
  if(result['data'] == []):
    return Response("Authorization Error", mimetype="text/plain", status=403)

  # add the salt to the password the user passed, and hash it.
  parsed_args['current_password'] = result['data'][0]['salt'] + \
      parsed_args['current_password']
  parsed_args['current_password'] = hashlib.sha512(
      parsed_args['current_password'].encode()).hexdigest()

  # if salted, hashed password is the same as the one we pulled from the database, salt and hash and update the database
  # with the new password.
  # else, authorization error.
  if(parsed_args['current_password'] == result['data'][0]['password']):
    parsed_args['new_password'] = result['data'][0]['salt'] + \
        parsed_args['new_password']
    parsed_args['new_password'] = hashlib.sha512(
        parsed_args['new_password'].encode()).hexdigest()

    result = dbh.run_query('UPDATE users u INNER JOIN `sessions` s ON u.id = s.user_id SET u.password = ? WHERE s.token = ?', [
        parsed_args['new_password'], parsed_args['login_token']])
  else:
    return Response("Authorization Error", mimetype="text/plain", status=403)

  # error check result variable from above.
  if(result['success'] == False):
    return result['error']

  # if data key is equal to 1(rowcount) return status 204 (no content)
  if(result['data'] == 1):
    return Response(status=204)


def delete_user():
  # get all required inputs for deleting a user.
  arg_scheme = [
      {
          'required': True,
          'name': 'login_token',
          'type': str
      },
      {
          'required': True,
          'name': 'password',
          'type': str
      }
  ]
  parsed_args = dbh.input_handler(request.json, arg_scheme)

  if(parsed_args['success'] == False):
    return parsed_args['error']
  else:
    parsed_args = parsed_args['data']

  # get email from the user based on the passed login_token, for getting the salt using the get_salt helper from dbh file.
  result = dbh.run_query("SELECT u.email FROM users u INNER JOIN `sessions` s ON u.id = s.user_id WHERE s.token = ?", [
                         parsed_args['login_token'], ])

  # error check result from above
  if(result['success'] == False):
    return result['error']

  # if length of data key from result variable is 1, get the salt using the email, add the salt to the passed password and hash it.
  # else, authorization error.
  if(len(result['data']) == 1):
    salt = dbh.get_salt(result['data'][0]['email'])
    parsed_args['password'] = salt + parsed_args['password']
    parsed_args['password'] = hashlib.sha512(
        parsed_args['password'].encode()).hexdigest()
  else:
    return Response("Authorization Error!", mimetype="text/plain", status=403)

  # Delete user from users table and set result variable to the return, which will have a data key that will be 1(rowcount) if successful.
  result = dbh.run_query(
      "DELETE u FROM users u INNER JOIN `sessions` s ON u.id = s.user_id WHERE u.password = ? AND s.token = ?", [parsed_args['password'], parsed_args['login_token']])

  # error check result variabble.
  if(result['success'] == False):
    return result['error']

  # if data key has a value of 1, return Response status 204 (no content)
  if(result['data'] == 1):
    return Response(status=204)
  else:
    return Response("Authentication Error!", mimetype="text/plain", status=403)
