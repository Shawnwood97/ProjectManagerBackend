from flask import request, Response
import dbh
import json
from datetime import datetime


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
  result = dbh.run_query("SELECT p.id, p.title, p.owner_id, p.created_at FROM projects p INNER JOIN project_roles pr ON p.id = pr.project_id INNER JOIN sessions s ON pr.user_id = s.user_id WHERE pr.accepted = 1 AND s.token = ?", [
                         parsed_args['login_token'], ])

  # error check
  if(result['success'] == False):
    return result['error']

  # we shouldn't need an auth error here, if the login token is invalid has no accepted projects, we will just return an empty list.
  user_json = json.dumps(result['data'], default=str)
  return Response(user_json, mimetype='application/json', status=200)
