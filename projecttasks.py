from flask import request, Response
import dbh
import json
from datetime import datetime
import rules
import traceback


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

  user_result = dbh.run_query("SELECT s.user_id, pl.project_id FROM sessions s INNER JOIN project_roles pr ON s.user_id = pr.user_id INNER JOIN project_lanes pl ON pr.project_id = pl.project_id INNER JOIN user_roles ur ON pr.role_id = ur.id WHERE s.token = ? AND pl.id = ? AND ur.can_edit = 1", [
                              parsed_args['login_token'], parsed_args['lane_id']])

  # error check
  if(user_result['success'] == False):
    return user_result['error']

  if(len(user_result['data']) != 1):
    return Response("Authorization Error", mimetype="text/plain", status=403)

  result = dbh.run_query("INSERT INTO project_tasks (title, description, lane_id) VALUES (?,?,?)", [
                         parsed_args['title'], parsed_args['description'], parsed_args['lane_id']])

  # error check
  if(result['success'] == False):
    return result['error']

  # if the data key of the result variable is greater than 0(lastrowid), return data back to the user
  if(result['data'] > 0):
    task_order_result = dbh.run_query(
        "SELECT task_order FROM project_lanes WHERE id = ?", [parsed_args['lane_id'], ])
    if(task_order_result['success'] == False):
      return task_order_result['error']

    task_order = json.loads(
        task_order_result['data'][0]['task_order'])

    task_order.append(result['data'])

    lane_result = dbh.run_query(
        "UPDATE project_lanes SET task_order = ? WHERE id = ?", [json.dumps(task_order), parsed_args['lane_id']])

    if(lane_result['success'] == False):
      return lane_result['error']

    new_lane_json = json.dumps(
        {
            'id': result['data'],
            'project_id': user_result['data'][0]['project_id'],
            'lane_id': parsed_args['lane_id'],
            'title': parsed_args['title'],
            'description': parsed_args['description'],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        default=str
    )
    return Response(new_lane_json, mimetype="application/json", status=201)


def update_task():
  # get required data from user, run it through our input handler, check for errors.
  # if no errors store the data key from the return in the parsed_args variable.
  arg_scheme = [
      {
          'required': False,
          'name': 'title',
          'type': str
      },
      {
          'required': False,
          'name': 'description',
          'type': str
      },
      {
          'required': False,
          'name': 'lane_id',
          'type': int
      },
      {
          'required': True,
          'name': 'task_id',
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

  # this select query will validate the user has edit permissions, #todo may be able to move this into the update statement.
  user_result = dbh.run_query("SELECT s.user_id, pl.project_id FROM sessions s INNER JOIN project_roles pr ON s.user_id = pr.user_id INNER JOIN project_lanes pl ON pr.project_id = pl.project_id INNER JOIN project_tasks pt ON pl.id = pt.lane_id INNER JOIN user_roles ur ON pr.role_id = ur.id WHERE s.token = ? AND pt.id = ? AND ur.can_edit = 1", [
                              parsed_args['login_token'], parsed_args['task_id']])

  # error check
  if(user_result['success'] == False):
    return user_result['error']

  # if length of data key is 0, auth error, this will ensure we error on bad login token and bad project_id
  if(len(user_result['data']) == 0):
    return Response("Authorization Error!", mimetype="text/plain", status=403)

  # base update sql statement
  sql = "UPDATE project_tasks pt SET"
  # empty params list to append valid args to.
  params = []

  # if args from above != None or an empty string, add to sql statement and append arg to params
  if(parsed_args.get('title') != None and parsed_args.get('title') != ''):
    sql += " pt.title = ?,"
    params.append(parsed_args['title'])
  if(parsed_args.get('description') != None and parsed_args.get('description') != ''):
    sql += " pt.description = ?,"
    params.append(parsed_args['description'])
  if(parsed_args.get('lane_id') != None and parsed_args.get('lane_id') != ''):
    sql += " pt.lane_id = ?,"
    params.append(parsed_args['lane_id'])

  # if params has a length that is not 0, append login_token arg to params.
  # remove the trailing comma from the above sql blocks
  # add WHERE clause to sql statement.
  # else, error.
  if(len(params) != 0):
    params.append(parsed_args['task_id'])
    sql = sql[:-1]
    sql += " WHERE pt.id = ?"
  else:
    return Response("Unknown Error", mimetype="text/plain", status=400)

  # run query and store the result(rowcount) in result variable
  result = dbh.run_query(sql, params)

  # error check
  if(result['success'] == False):
    return result['error']

  # after success from above, get all project data for the endpoint to return.
  updated_task_info = dbh.run_query(
      'SELECT pt.id, pt.lane_id, pt.title, pt.description, pt.created_at FROM project_tasks pt WHERE pt.id = ?', [parsed_args['task_id'], ])

  # error check for above statement.
  if(updated_task_info['success'] == False):
    return updated_task_info['error']

  # if length of the data key equals 1, create the json dump for the data key at index 0 (so it's a dict not a list.)
  # else error response, for getting project after update, since we know the update would have happened already.
  if(len(updated_task_info['data']) == 1):
    task_info_json = json.dumps(
        updated_task_info['data'][0], default=str)
    return Response(task_info_json, mimetype="application/json", status=201)
  else:
    traceback.print_exc()
    return Response("Error getting task after update!", mimetype="text/plain", status=404)


def delete_task():
    # get required data from user, run it through our input handler, check for errors.
  # if no errors store the data key from the return in the parsed_args variable.
  arg_scheme = [
      {
          'required': True,
          'name': 'task_id',
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
  result = dbh.run_query("DELETE pt FROM project_tasks pt INNER JOIN project_lanes pl ON pt.lane_id = pl.id INNER JOIN project_roles pr ON pr.project_id = pl.project_id INNER JOIN user_roles ur ON pr.role_id = ur.id INNER JOIN sessions s ON pr.user_id = s.user_id WHERE s.token = ? AND pt.id = ? AND ur.can_edit = 1", [
      parsed_args['login_token'], parsed_args['task_id']])

  # error check
  if(result['success'] == False):
    return result['error']

  # if data key from the above query = 1 (rowcount) return response (no content), else auth error.
  if(result['data'] == 1):
    return Response(status=204)
  else:
    return Response("Authentication Error", mimetype="text/plain", status=403)
