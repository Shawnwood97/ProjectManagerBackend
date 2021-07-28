from flask import request, Response
import dbh
import json
from datetime import datetime
import rules
import traceback


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
  user_result = dbh.run_query("SELECT s.user_id FROM sessions s INNER JOIN project_roles pr ON s.user_id = pr.user_id INNER JOIN user_roles ur ON pr.role_id = ur.id WHERE s.token = ? AND pr.project_id = ? AND ur.can_edit = 1", [
                              parsed_args['login_token'], parsed_args['project_id']])

  # error check
  if(user_result['success'] == False):
    return user_result['error']

  # if length of the data key is not 1, auth error. Should be 1 because the return from the query should be 1 list with user_id as the content.
  if(len(user_result['data']) != 1):
    traceback.print_exc()
    return Response("Authorization Error", mimetype="text/plain", status=403)

  # if we get passed the above conditional, the user has permission, so we insert the data into the project_lanes table.
  result = dbh.run_query("INSERT INTO project_lanes (title, project_id) VALUES (?,?)", [
                         parsed_args['title'], parsed_args['project_id']])
  print(result['data'])
  # error check insert query
  if(result['success'] == False):
    return result['error']

  # if the data key of the result variable is greater than 0(lastrowid), return data back to the user
  if(result['data'] > 0):
    new_lane_json = json.dumps(
        {
            'id': result['data'],
            'project_id': parsed_args['project_id'],
            'title': parsed_args['title'],
            'tasks': [],
            'task_order': '[]',
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        default=str
    )
    return Response(new_lane_json, mimetype="application/json", status=201)


def update_lane():
  # get required data from user, run it through our input handler, check for errors.
  # if no errors store the data key from the return in the parsed_args variable.
  arg_scheme = [
      {
          'required': True,
          'name': 'login_token',
          'type': str
      },
      {
          'required': True,
          'name': 'lane_id',
          'type': int
      },
      {
          'required': False,
          'name': 'title',
          'type': str
      },
      {
          'required': False,
          'name': 'old_index',
          'type': int
      },
      {
          'required': False,
          'name': 'new_index',
          'type': int
      },
  ]
  parsed_args = dbh.input_handler(request.json, arg_scheme)

  if(parsed_args['success'] == False):
    return parsed_args['error']
  else:
    parsed_args = parsed_args['data']

  # this select query will validate the user has edit permissions, #todo may be able to move this into the update statement.
  user_result = dbh.run_query("SELECT s.user_id, pl.project_id FROM sessions s INNER JOIN project_roles pr ON s.user_id = pr.user_id INNER JOIN project_lanes pl ON pr.project_id = pl.project_id INNER JOIN user_roles ur ON pr.role_id = ur.id WHERE s.token = ? AND pl.id = ? AND ur.can_edit = 1", [
                              parsed_args['login_token'], parsed_args['lane_id']])

  # error check
  if(user_result['success'] == False):
    return user_result['error']

  # if length of data key is 0, auth error, this will ensure we error on bad login token and bad project_id
  if(len(user_result['data']) == 0):
    return Response("Authorization Error!", mimetype="text/plain", status=403)

  # base update sql statement
  sql = "UPDATE project_lanes pl SET"
  # empty params list to append valid args to.
  params = []

  # if args from above != None or an empty string, add to sql statement and append arg to params
  # TODO only title for now, will add others at some point
  if(parsed_args.get('title') != None and parsed_args.get('title') != ''):
    sql += " pl.title = ?,"
    params.append(parsed_args['title'])

  # if params has a length that is not 0, append login_token arg to params.
  # remove the trailing comma from the above sql blocks
  # add WHERE clause to sql statement.
  # else, error.
    if(len(params) != 0):
      params.append(parsed_args['lane_id'])
      sql = sql[:-1]
      sql += " WHERE pl.id = ?"

      # run query and store the result(rowcount) in result variable
      result = dbh.run_query(sql, params)

  # error check
      if(result['success'] == False):
        return result['error']
    else:
      return Response("Unknown Error", mimetype="text/plain", status=400)

  if(parsed_args['old_index'] != None and parsed_args['new_index'] != None):
    lanes_result = dbh.run_query(
        "SELECT p.lane_order FROM projects p WHERE p.id = ?", [user_result['data'][0]['project_id'], ])
    if(lanes_result['success'] == False):
      return lanes_result['error']

    lanes_order = json.loads(lanes_result['data'][0]['lane_order'])

    lanes_order.pop(parsed_args['old_index'])

    lanes_order.insert(parsed_args['new_index'], parsed_args['lane_id'])

    lanes_order_json = json.dumps(lanes_order)

    lanes_order_result = dbh.run_query("UPDATE projects p SET p.lane_order = ? WHERE p.id = ?", [
        lanes_order_json, user_result['data'][0]['project_id']])

    if(lanes_order_result['success'] == False):
      return lanes_order_result['error']

  # after success from above, get all project data for the endpoint to return.
  updated_lane_info = dbh.run_query(
      'SELECT pl.id, pl.title, pl.created_at, p.lane_order FROM project_lanes pl INNER JOIN projects p ON pl.project_id = p.id WHERE pl.id = ?', [parsed_args['lane_id'], ])

  # error check for above statement.
  if(updated_lane_info['success'] == False):
    return updated_lane_info['error']

  # if length of the data key equals 1, create the json dump for the data key at index 0 (so it's a dict not a list.)
  # else error response, for getting project after update, since we know the update would have happened already.
  if(len(updated_lane_info['data']) == 1):
    lane_info_json = json.dumps(
        updated_lane_info['data'][0], default=str)
    return Response(lane_info_json, mimetype="application/json", status=201)
  else:
    traceback.print_exc()
    return Response("Error getting lane after update!", mimetype="text/plain", status=404)


def delete_lane():
  # get required data from user, run it through our input handler, check for errors.
  # if no errors store the data key from the return in the parsed_args variable.
  arg_scheme = [
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

  # query to delete a task, with validation
  result = dbh.run_query("DELETE pl FROM project_lanes pl INNER JOIN project_roles pr ON pr.project_id = pl.project_id INNER JOIN user_roles ur ON pr.role_id = ur.id INNER JOIN sessions s ON pr.user_id = s.user_id WHERE s.token = ? AND pl.id = ? AND ur.can_edit = 1", [
      parsed_args['login_token'], parsed_args['lane_id']])

  # error check
  if(result['success'] == False):
    return result['error']

  # if data key from the above query = 1 (rowcount) return response (no content), else auth error.
  if(result['data'] == 1):
    return Response(status=204)
  else:
    return Response("Authentication Error", mimetype="text/plain", status=403)
