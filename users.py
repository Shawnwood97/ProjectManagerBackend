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

  if(result['success'] == False):
    return result['error']

  # if data key has data in it, len will == 1, since we only allow passing a single user_id and returning a single user
  # used index 0 in json dumps to return a dict of the 1 user, rather than a list of dicts, since it is just 1 user.
  if(len(result['data']) == 1):
    user_json = json.dumps(result['data'][0], default=str)
    return Response(user_json, mimetype='application/json', status=200)
  else:
    return Response("User not found!", mimetype="text/plain", status=404)


# def update_user():
#   arg_scheme = [
#       {
#           'required': True,
#           'name': 'login_token',
#           'type': str
#       },
#       {
#           'required': False,
#           'name': 'email',
#           'type': str
#       },
#       {
#           'required': False,
#           'name': 'username',
#           'rule': rules.username_checker,
#           'type': str
#       },
#       {
#           'required': False,
#           'name': 'status',
#           'type': str
#       },
#       {
#           'required': False,
#           'name': 'avatar',
#           'type': str
#       },
#   ]
#   parsed_args = dbh.input_handler(request.json, arg_scheme)

#   if(parsed_args['success'] == False):
#     return parsed_args['error']
#   else:
#     parsed_args = parsed_args['data']


def change_password():
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

  if(result['success'] == False):
    return result['error']

  if(result['data'] == 1):
    return Response(status=204)
