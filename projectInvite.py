from flask import request, Response
import dbh
import json
from datetime import datetime
import rules


def invite_user():
  # get required and optional data from user, technically email OR username is required, but the error for that is handled by a conditional else below.
  # if no errors store the data key from the return in the parsed_args variable.
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
          'name': 'project_id',
          'type': int
      },
      {
          'required': True,
          'name': 'login_token',
          'type': str
      },
      {
          'required': True,
          'name': 'role_id',
          'rule': rules.role_checker,
          'type': int
      }
  ]
  parsed_args = dbh.input_handler(request.json, arg_scheme)

  if(parsed_args['success'] == False):
    return parsed_args['error']
  else:
    parsed_args = parsed_args['data']

  # validate the user, and validate that they own the project before any of the inviting logic happens.
  result = dbh.run_query('SELECT u.id FROM users u INNER JOIN `sessions` s ON u.id = s.user_id INNER JOIN projects p ON s.user_id = p.owner_id WHERE s.token = ? AND p.id = ?',
                         [parsed_args['login_token'], parsed_args['project_id']])

  if(result['success'] == False):
    return result['error']

  # in this case, if run_query reutrns an empty data list, the login_token or project id was invalid, therefor authorization error.
  if(result['data'] == []):
    return Response("Authorization Error", mimetype="text/plain", status=403)

  # base SQL select we will use to get the invited user's id from their username or email address.
  user_sql = "SELECT id from users"

  # empty params list for appending either username or email to, depending on which the user gave us.
  params = []

  # if user passes username or email, use that as the WHERE clause.
  if(parsed_args.get('username') != None and parsed_args.get('username') != ''):
    user_sql += " WHERE username = ?"
    params.append(parsed_args['username'])
  elif(parsed_args.get('email') != None and parsed_args.get('email') != ''):
    user_sql += " WHERE email = ?"
    params.append(parsed_args['email'])
  else:
    return Response("Missing required information!", mimetype="text/plain", status=422)

  # this variable will store the user_id in the data key when the query is successful
  user_info = dbh.run_query(user_sql, params)

  # error check
  if(user_info['success'] == False):
    return user_info['error']

  # if length of the data key is not 1, no user had the passed email or username.
  if(len(user_info['data']) != 1):
    return Response("User doesn't exist.", mimetype="text/plain", status=404)

  # validation to check if the user already has a pending request for the project_id.
  check_dupe_info = dbh.run_query("SELECT pr.user_id FROM project_roles pr INNER JOIN projects p ON pr.project_id = p.id WHERE pr.accepted = 0 AND pr.user_id = ?", [
                                  user_info['data'][0]['id'], ])

  # error check
  if(check_dupe_info['success'] == False):
    return check_dupe_info['error']

  # if the select statement returned anything to the data key, then the user already has a pending invite for the passed project_id
  if(len(check_dupe_info['data']) > 0):
    return Response("User has an unaccepted invite to this project already.", mimetype="text/plain", status=404)

  # if everything above works, INSERT info into the project_roles table.
  result = dbh.run_query("INSERT INTO project_roles (project_id, user_id, role_id) VALUES (?,?,?)", [
                         parsed_args['project_id'], user_info['data'][0]['id'], parsed_args['role_id']])

  # error check
  if(result['success'] == False):
    return result['error']

  # maybe not needed, but defensive, if data_key (lastrowid) is greater than 0, dump and return json to user.
  if(result['data'] > 0):
    new_invite_json = json.dumps(
        {
            'id': result['data'],
            'project_id': parsed_args['project_id'],
            'user_id': user_info['data'][0]['id'],
            'role_id': parsed_args['role_id'],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        default=str
    )
    return Response(new_invite_json, mimetype="application/json", status=201)


def list_pending_invites():
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

  # store return of this select query in the result variable, will be either list of projects the user has been invited to access, but has
  # not accepted or declined or an empty list.
  result = dbh.run_query("SELECT p.id, p.title, p.owner_id, p.created_at FROM projects p INNER JOIN project_roles pr ON p.id = pr.project_id INNER JOIN sessions s ON pr.user_id = s.user_id WHERE pr.accepted = 0 AND s.token = ?", [
                         parsed_args['login_token'], ])

  # error check
  if(result['success'] == False):
    return result['error']

  # we shouldn't need an auth error here, if the login token is invalid user has no pending invites, we will just return an empty list.
  user_json = json.dumps(result['data'], default=str)
  return Response(user_json, mimetype='application/json', status=200)


def invite_response():
  # Get required data, run it through input handler with endpoint argument check for errors and
  # store the data key in parsed_args variable for later.
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
      },
      {
          'required': True,
          'name': 'accept_invite',
          'rule': rules.invite_checker,
          'type': int
      }
  ]
  parsed_args = dbh.input_handler(request.json, arg_scheme)

  if(parsed_args['success'] == False):
    return parsed_args['error']
  else:
    parsed_args = parsed_args['data']

  # we run our full select that we will use for the return here because we need the pr.id since we allow duplicate rows for the same user_id
  # this seemed to be the best way to always be able to target the same invite.
  # Validated with login token on the project roles user_id, as well only selects a row that has an accepted column of 0(pending)
  # based on our logic from sending the invite, there can only be 1 row for each project and user combination that has an accepted
  # row of 0.
  project_inv_info = dbh.run_query("SELECT pr.id, pr.project_id, pr.user_id, pr.role_id, pr.accepted, pr.created_at FROM project_roles pr INNER JOIN sessions s ON pr.user_id = s.user_id WHERE s.token = ? AND pr.project_id = ? AND pr.accepted = 0", [
                                   parsed_args['login_token'], parsed_args['project_id']])

  # error check
  if(project_inv_info['success'] == False):
    return project_inv_info['error']

  # if length of data key is 0, auth error, this will ensure we error on bad login token and bad project_id
  if(len(project_inv_info['data']) == 0):
    return Response("Authorization Error!", mimetype="text/plain", status=403)

  # base update statement, no inner join because we already completed our verification with the above select
  sql = "UPDATE project_roles pr SET"

  # if accept_invite is 1(true) set the accepted column in the row to 1(accepted) and concat the sql
  # if accept_invite is 0(false) set the accepted column in the row to 2(declined) and concat the sql
  # if the accepted column is 0, that means it is pending.
  if(parsed_args['accept_invite'] == 1):
    sql += " pr.accepted = 1"
    project_inv_info['data'][0]['accepted'] = 1
  elif(parsed_args['accept_invite'] == 0):
    sql += " pr.accepted = 2"
    project_inv_info['data'][0]['accepted'] = 2

  # concat the WHERE clause, we just use the pr.id and id key from our select since we already did validation
  sql += " WHERE pr.id = ?"

  result = dbh.run_query(sql, [project_inv_info['data'][0]['id'], ])

  # error check
  if(result['success'] == False):
    return result['error']

  # if update returned a rowcount, dump json and respond with it.
  # cant imagine any other errors being able to happen, meaning we likely dont need this if.
  if(result['data'] > 0):
    updated_project_role_json = json.dumps(
        project_inv_info['data'][0], default=str)
    return Response(updated_project_role_json, mimetype="application/json", status=201)
