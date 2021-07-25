from flask import request, Response
import dbh
import json
from datetime import datetime
import traceback


def create_project():
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
          'name': 'title',
          'type': str
      }
  ]
  parsed_args = dbh.input_handler(request.json, arg_scheme)

  if(parsed_args['success'] == False):
    return parsed_args['error']
  else:
    parsed_args = parsed_args['data']

  # verify the user has a valid login_token and get the users id back for storing as the owner_id.
  user_result = dbh.run_query("SELECT u.id FROM users u INNER JOIN sessions s ON u.id = s.user_id WHERE s.token = ?", [
                              parsed_args['login_token'], ])

  # error check
  if(user_result['success'] == False):
    return user_result['error']

  # auth error if user_result's data key has no length (didn't return anything)
  if(len(user_result['data']) != 1):
    return Response("Authentication Error", mimetype="text/plain", status=403)

  # run insert statement for creating a project, inserting projects title and owner_id and store the return (lastrowid) in result variable.
  result = dbh.run_query("INSERT INTO projects (title, owner_id) VALUES (?,?)", [
                         parsed_args['title'], user_result['data'][0]['id']])

  # error check
  if(result['success'] == False):
    return result['error']

  # insert statement to create a role for the owner.
  role_result = dbh.run_query("INSERT INTO project_roles (project_id, user_id, role_id, accepted) VALUES (?,?,?,?)", [
                              result['data'], user_result['data'][0]['id'], 3, 1])

  # error check
  if(role_result['success'] == False):
    return role_result['error']

  if(result['data'] > 0):
    new_project_json = json.dumps(
        {
            'id': result['data'],
            'owner_id': user_result['data'][0]['id'],
            'title': parsed_args['title'],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        default=str
    )
    return Response(new_project_json, mimetype="application/json", status=201)


def delete_project():
  # Get required data, run it through input handler with endpoint argument check for errors and
  # store the data key in parsed_args variable for later.
  arg_scheme = [
      {
          'required': True,
          'name': 'login_token',
          'type': str
      },
      {
          'required': True,
          'name': 'project_id',
          'type': int
      }
  ]
  parsed_args = dbh.input_handler(request.json, arg_scheme)

  if(parsed_args['success'] == False):
    return parsed_args['error']
  else:
    parsed_args = parsed_args['data']

  # delete statement to delete a project if the user has a valid login token and passed a valid OWNED project id.
  result = dbh.run_query("DELETE p FROM projects p INNER JOIN sessions s ON p.owner_id = s.user_id WHERE p.id = ? AND s.token = ?", [
                         parsed_args['project_id'], parsed_args['login_token']])

  # error check
  if(result['success'] == False):
    return result['error']

  # if rowcount returned is 1, return no content response, else error.
  if(result['data'] == 1):
    return Response(status=204)
  else:
    return Response("Authentication Error", mimetype="text/plain", status=403)


def list_owned_projects():
  # Get required data, run it through input handler with endpoint argument check for errors and
  # store the data key in parsed_args variable for later.
  arg_scheme = [
      {
          'required': True,
          'name': 'login_token',
          'type': str
      }
  ]
  parsed_args = dbh.input_handler(request.args, arg_scheme)

  if(parsed_args['success'] == False):
    return parsed_args['error']
  else:
    parsed_args = parsed_args['data']

  # store return of this select query in the result variable, we will return, will either be validated owners projects or an empty list.
  result = dbh.run_query("SELECT p.id, p.title, p.owner_id, p.created_at FROM projects p INNER JOIN sessions s ON p.owner_id = s.user_id WHERE s.token = ?", [
                         parsed_args['login_token'], ])

  # error check
  if(result['success'] == False):
    return result['error']

  # we shouldn't need an auth error here, if the login token is invalid or owns no projects, we will just return an empty list.
  user_json = json.dumps(result['data'], default=str)
  return Response(user_json, mimetype='application/json', status=200)


def list_accepted_projects():
  # Get required data, run it through input handler with endpoint argument check for errors and
  # store the data key in parsed_args variable for later.
  arg_scheme = [
      {
          'required': True,
          'name': 'login_token',
          'type': str
      }
  ]
  parsed_args = dbh.input_handler(request.args, arg_scheme)

  if(parsed_args['success'] == False):
    return parsed_args['error']
  else:
    parsed_args = parsed_args['data']

  # store return of this select query in the result variable, will be either list of projects the user has accepted access to
  #  or an empty list.
  result = dbh.run_query("SELECT p.id AS project_id, p.title, p.owner_id, p.created_at FROM projects p INNER JOIN project_roles pr ON p.id = pr.project_id INNER JOIN sessions s ON pr.user_id = s.user_id WHERE pr.accepted = 1 AND s.token = ? and p.owner_id != s.user_id", [
                         parsed_args['login_token'], ])

  # error check
  if(result['success'] == False):
    return result['error']

  # we shouldn't need an auth error here, if the login token is invalid has no accepted projects, we will just return an empty list.
  user_json = json.dumps(result['data'], default=str)
  return Response(user_json, mimetype='application/json', status=200)


def get_project():
  # get required data from user, run it through our input handler, check for errors.
  # if no errors store the data key from the return in the parsed_args variable.
  arg_scheme = [
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
  parsed_args = dbh.input_handler(request.args, arg_scheme)

  if(parsed_args['success'] == False):
    return parsed_args['error']
  else:
    parsed_args = parsed_args['data']

  # select query to validate the user is allowed to see lanes in a project.
  user_result = dbh.run_query("SELECT ur.can_edit FROM sessions s INNER JOIN project_roles pr ON s.user_id = pr.user_id INNER JOIN user_roles ur ON pr.role_id = ur.id WHERE s.token = ? AND pr.project_id = ?", [
                              parsed_args['login_token'], parsed_args['project_id']])

  # error check
  if(user_result['success'] == False):
    return user_result['error']

  if(len(user_result['data']) != 1):
    return Response("Authorization Error", mimetype="text/plain", status=403)

  project_result = dbh.run_query("SELECT p.id, p.title, p.owner_id, p.created_at FROM projects p WHERE p.id = ?", [
                                 parsed_args['project_id'], ])

  if(project_result['success'] == False):
    return project_result['error']

  lanes_result = dbh.run_query("SELECT pl.id, pl.title, pl.task_order, pl.created_at FROM project_lanes pl WHERE pl.project_id = ?", [
                               parsed_args['project_id'], ])

  if(lanes_result['success'] == False):
    return lanes_result['error']

  tasks_result = dbh.run_query(
      "SELECT pt.id, pt.title, pt.description, pt.lane_id, pt.accent_hex, pt.created_at FROM project_tasks pt INNER JOIN project_lanes pl ON pt.lane_id = pl.id WHERE pl.project_id = ?", [parsed_args['project_id'], ])

  if(tasks_result['success'] == False):
    return tasks_result['error']

  for lane in lanes_result['data']:
    lane['tasks'] = []
    for task in tasks_result['data']:
      if(task['lane_id'] == lane['id']):
        lane['tasks'].append(task)

  project_json = json.dumps(
      {
          'id': project_result['data'][0]['id'],
          'can_edit': user_result['data'][0]['can_edit'],
          'title': project_result['data'][0]['title'],
          'owner': project_result['data'][0]['owner_id'],
          'created_at': project_result['data'][0]['created_at'],
          'lanes': lanes_result['data']
      },
      default=str
  )
  return Response(project_json, mimetype="application/json", status=200)


def update_project():
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
          'name': 'project_id',
          'type': int
      },
      {
          'required': False,
          'name': 'title',
          'type': str
      }
  ]
  parsed_args = dbh.input_handler(request.json, arg_scheme)

  if(parsed_args['success'] == False):
    return parsed_args['error']
  else:
    parsed_args = parsed_args['data']

  # this select query will validate the user has edit permissions, #todo may be able to move this into the update statement.
  user_result = dbh.run_query("SELECT s.user_id FROM sessions s INNER JOIN project_roles pr ON s.user_id = pr.user_id INNER JOIN user_roles ur ON pr.role_id = ur.id WHERE s.token = ? AND pr.project_id = ? AND ur.can_edit = 1", [
                              parsed_args['login_token'], parsed_args['project_id']])

  # error check
  if(user_result['success'] == False):
    return user_result['error']

  # if length of data key is 0, auth error, this will ensure we error on bad login token and bad project_id
  if(len(user_result['data']) == 0):
    return Response("Authorization Error!", mimetype="text/plain", status=403)

  # base update sql statement
  sql = "UPDATE projects p SET"
  # empty params list to append valid args to.
  params = []

  # if args from above != None or an empty string, add to sql statement and append arg to params
  # TODO only title for now, will add others at some point
  if(parsed_args.get('title') != None and parsed_args.get('title') != ''):
    sql += " p.title = ?,"
    params.append(parsed_args['title'])

  # if params has a length that is not 0, append login_token arg to params.
  # remove the trailing comma from the above sql blocks
  # add WHERE clause to sql statement.
  # else, error.
  if(len(params) != 0):
    params.append(parsed_args['project_id'])
    sql = sql[:-1]
    sql += " WHERE p.id = ?"
  else:
    return Response("Unknown Error", mimetype="text/plain", status=400)

  # run query and store the result(rowcount) in result variable
  result = dbh.run_query(sql, params)

  # error check
  if(result['success'] == False):
    return result['error']

  # after success from above, get all project data for the endpoint to return.
  updated_project_info = dbh.run_query(
      'SELECT p.id, p.title, p.owner_id, p.created_at FROM projects p WHERE p.id = ?', [parsed_args['project_id'], ])

  # error check for above statement.
  if(updated_project_info['success'] == False):
    return updated_project_info['error']

  # if length of the data key equals 1, create the json dump for the data key at index 0 (so it's a dict not a list.)
  # else error response, for getting project after update, since we know the update would have happened already.
  if(len(updated_project_info['data']) == 1):
    project_info_json = json.dumps(
        updated_project_info['data'][0], default=str)
    return Response(project_info_json, mimetype="application/json", status=201)
  else:
    traceback.print_exc()
    return Response("Error getting project after update!", mimetype="text/plain", status=404)
