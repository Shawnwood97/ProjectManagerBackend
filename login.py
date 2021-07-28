from flask import request, Response
import dbh
import json
import traceback
import secrets
import hashlib


def login_user():
  # get required and optional data from user, technically email OR username is required, but the error for that is handled by a conditional else below.
  arg_scheme = [
      {
          'required': False,
          'name': 'email',
          'type': str
      },
      {
          'required': False,
          'name': 'username',
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

  # base SQL select we will use for verification.
  sql = "SELECT id from users"

  # empty params list for appending either username or email to, depending on which the user gave us.
  params = []

  # if user passes username or email, use that as the WHERE clause, AND is here for handling the password from below as well.
  # set identity variable from either conditional to the data passed by the user so we can pass it to our get_salt helper function.
  if(parsed_args['username'] != None and parsed_args['username'] != ''):
    sql += " WHERE username = ? AND"
    params.append(parsed_args['username'])
    identity = parsed_args['username']
  elif(parsed_args['email'] != None and parsed_args['email'] != ''):
    sql += " WHERE email = ? AND"
    params.append(parsed_args['email'])
    identity = parsed_args['email']
  else:
    return Response("Missing required information!", mimetype="text/plain", status=422)

  # after we have email or username, add password to sql query, will come after AND from above
  sql += " password = ?"

  # set salt to the return of the get_salt helper, passing the identity variable from above as an argument.
  # then set the password key to the salt + value from the password key
  # then hash that and set it to the password key.
  result = dbh.get_salt(identity)

  # error check.
  if(result['success'] == False):
    return result['error']

  parsed_args['password'] = result['data'][0]['salt'] + parsed_args['password']
  parsed_args['password'] = hashlib.sha512(
      parsed_args['password'].encode()).hexdigest()

  # append the password to the params list
  params.append(parsed_args['password'])

  # run the query and store the return in a variable.
  result = dbh.run_query(sql, params)

  # error check
  if(result['success'] == False):
    return result['error']
 # if the length of the data key in result is equal to 1, create the login token and insert it.
  if(len(result['data']) == 1):
    # create and store 45 Byte token in variable
    login_token = secrets.token_urlsafe(45)

    # run insert statement for creating the session and store it in a variable.
    result = dbh.run_query("INSERT INTO sessions (token, user_id) VALUES (?,?)", [
                           login_token, result['data'][0]["id"]])

    # error check.
    if(result['success'] == False):
      return result['error']
  # auth error if the data dictionary has 0, or too many objects inside. Should never be more, should be 1 or 0.
  else:
    return Response("Invalid Authentication", mimetype="text/plain", status=403)

  # Select statement for returning data.
  login_info = dbh.run_query(
      "SELECT u.id, u.username, u.email, u.status, u.avatar FROM users u INNER JOIN sessions s ON u.id = s.user_id WHERE s.token = ?", [login_token, ])

  if(login_info['success'] == False):
    return login_info['error']

  # if login info data list has a length of 1, create the json return, else error.
  if(len(login_info['data']) == 1):
    # add login token into the first index in the data dict for API return purposes.
    login_info['data'][0].update({'login_token': login_token})
    updated_login_json = json.dumps(login_info['data'][0], default=str)
    return Response(updated_login_json, mimetype="application/json", status=201)
  else:
    # error here will only happen if INSERT happened and SELECT failed.
    return Response("Error getting user info after insert!", mimetype="text/plain", status=404)


def logout_user():
  # Get required data, run it through input handler with endpoint argument check for errors and
  # store the data key in parsed_args variable for later.
  arg_scheme = [
      {
          'required': True,
          'name': 'login_token',
          'type': str
      }
  ]
  parsed_args = dbh.input_handler(request.json, arg_scheme)

  if(parsed_args['success'] == False):
    return parsed_args['error']
  else:
    parsed_args = parsed_args['data']

  # TODO come back and make this an update and set the session end column to the current time.
  # run the query and store the result(rowcount) in a variable
  result = dbh.run_query('DELETE s from sessions s WHERE s.token = ?', [
                         parsed_args['login_token'], ])

  # error check
  if(result['success'] == False):
    return result['error']

  # if rowcount returned is 1, return no content response, else error.
  if(result['data'] == 1):
    return Response(status=204)
  else:
    return Response("Error logging out", mimetype="text/plain", status=403)
