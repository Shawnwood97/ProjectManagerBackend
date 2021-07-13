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
