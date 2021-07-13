from flask import request, Response
import dbh
import json
import traceback
from datetime import datetime
import secrets
import hashlib

# Keeping it simple with account creation, just a simple email, username, password


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

  # create a salt for the password, add it to the beginning of the password, and hash it.
  salt = dbh.create_salt()
  parsed_args['password'] = salt + parsed_args['password']
  parsed_args['password'] = hashlib.sha512(
      parsed_args['password'].encode()).hexdigest()

  # query to insert the data into the users table
  sql = "INSERT INTO users (email, username, password, salt) VALUES (?,?,?,?)"

  # params we will pass to the prepared statement.
  params = [parsed_args['email'], parsed_args['username'],
            parsed_args['password'], salt]

  # make sure value was passed since all are required.
  for param in params:
    if(param == "" or param == None):
      return Response("Missing required information!", mimetype="text/plain", status=422)

  # set sesult to the return of the run_query function
  result = dbh.run_query(sql, params)

  if(result['success'] == False):
    return result['error']
