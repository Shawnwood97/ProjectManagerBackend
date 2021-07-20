from flask import request, Response
import dbh
import json
from datetime import datetime
import rules


def create_lane():
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
          'name': 'project_id',
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

  # select query to validate the user is allowed to create a lane in the project based on INNER JOIN with sesison table, project_roles table and user_roles table.
  user_result = dbh.run_query("SELECT s.user_id FROM sessions s INNER JOIN project_roles pr ON s.user_id = pr.user_id INNER JOIN user_roles ur ON pr.role_id = ur.id WHERE s.token = ? AND pr.id = ? AND ur.can_edit = 1", [
                              parsed_args['login_token'], parsed_args['project_id']])

  # error check
  if(user_result['success'] == False):
    return user_result['error']

  # if length of the data key is not 1, auth error. Should be 1 because the return from the query should be 1 list with user_id as the content.
  if(len(user_result['data']) != 1):
    return Response("Authorization Error", mimetype="text/plain", status=403)

  # if we get passed the above conditional, the user has permission, so we insert the data into the project_lanes table.
  result = dbh.run_query("INSERT INTO project_lanes (title, project_id) VALUES (?,?)", [
                         parsed_args['title'], parsed_args['project_id']])

  # error check insert query
  if(result['success'] == False):
    return result['error']

  # if the data key of the result variable is greater than 0(lastrowid), return data back to the user
  if(result['data'] > 0):
    new_lane_json = json.dumps(
        {
            'id': user_result['data'],
            'project_id': parsed_args['project_id'],
            'title': parsed_args['title'],
        },
        default=str
    )
    return Response(new_lane_json, mimetype="application/json", status=201)

# def list_lanes():
#   # get required data from user, run it through our input handler, check for errors.
#   # if no errors store the data key from the return in the parsed_args variable.
#   arg_scheme = [
#       {
#           'required': True,
#           'name': 'project_id',
#           'type': int
#       },
#       {
#           'required': True,
#           'name': 'login_token',
#           'type': str
#       }
#   ]
#   parsed_args = dbh.input_handler(request.json, arg_scheme)

#   if(parsed_args['success'] == False):
#     return parsed_args['error']
#   else:
#     parsed_args = parsed_args['data']

#   # select query to validate the user is allowed to see lanes in a project.
#   user_result = dbh.run_query("SELECT pl.id, pl.title, ur.can_edit, pl.created_at FROM sessions s INNER JOIN project_roles pr ON s.user_id = pr.user_id INNER JOIN user_roles ur ON pr.role_id = ur.id WHERE s.token = ? AND pr.project_id = ?", [
#                               parsed_args['login_token'], parsed_args['project_id']])

#   # error check
#   if(user_result['success'] == False):
#     return user_result['error']
