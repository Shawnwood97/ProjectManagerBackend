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
