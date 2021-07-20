from flask import request, Response
import dbh
import json
from datetime import datetime
import rules


def create_task():
  # get required data from user, run it through our input handler, check for errors.
  # if no errors store the data key from the return in the parsed_args variable.
  arg_scheme = [
      {
          'required': True,
          'name': 'title',
          'type': str
      },
      {
          'required': True,
          'name': 'description',
          'type': str
      },
      {
          'required': True,
          'name': 'lane_id',
          'type': int
      },
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

  user_result = dbh.run_query("SELECT s.user_id FROM sessions s INNER JOIN project_rols pr ON s.user_id = pr.user_id WHERE s.token = ? AND pr.role_id = 2", [
                              parsed_args['login_token'], ])

  # error check
  if(user_result['success'] == False):
    return user_result['error']
