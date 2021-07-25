import mariadb
import dbconn
import traceback
from flask import Response
import string
import random
import re


def loop_items(cursor, rows):
  # Takes column headers from cursor.description, and rows returned from the query, and creates a zip object with them, pairing each header index with
  # the same index from row as tuples, then we do data conversion to a dictionary by wrapping the result of zip() in dict() and append it to result, which
  # starts as a empty list.
  headers = [i[0] for i in cursor.description]
  result = []
  for row in rows:
    result.append(dict(zip(headers, row)))
  return result


def run_query(sql, params=[]):
  # This function will run all of the queries, keeping it DRY, params starts as an empty list because we don't always need them.
  # sql argument will be the sql statement
  # params is for the prepared statements variables, must be passed in order, as a list.

  # setting defaults for the result
  result = {
      'success': True,
      'error': None,
      'data': None
  }
  conn = dbconn.open_connection()
  cursor = dbconn.create_cursor(conn)
  # try block with a conditional inside to check what kind of statement we are passing based on how it starts.
  try:
    cursor.execute(sql, params)
    if(sql.startswith('SELECT')):
      sel_data = cursor.fetchall()
      # set the data key inside result to the result of the loop_items function from above.
      # this will be the data from the fetchall above and stictes the column names to them as keys in a dictionary.
      # we don't set success or error here because the defaults from above are correct.
      result['data'] = loop_items(cursor, sel_data)
    elif(sql.startswith('INSERT')):
      conn.commit()
      # Set data key in result to the lastrowid, this will be primary key from the table.
      result['data'] = cursor.lastrowid
    elif(sql.startswith('UPDATE') or sql.startswith('DELETE')):
      # we want rowcount from update and delete statements, so they share an elif block.
      conn.commit()
      result['data'] = cursor.rowcount
    else:
      # else for error catching if the sql statement does not start with SELECT, INSERT, UPDATE or DELETE
      result['success'] = False
      result['error'] = Response(
          "Error: Method Not Allowed!", mimetype="text/plain", status=405)
  # MariaDB exceptions with a catchAll as the last exception
  # they all set the success key to False, and the error key to the Response.
  except mariadb.InternalError:
    result['success'] = False
    result['error'] = Response(
        "Internal Server Error, Please try again later!", mimetype="text/plain", status=500)
    traceback.print_exc()
  except mariadb.IntegrityError:
    result['success'] = False
    result['error'] = Response(
        "Error: Possible duplicate data or foreign key conflict!", mimetype="text/plain", status=409)
    traceback.print_exc()
  except mariadb.DataError:
    result['success'] = False
    result['error'] = Response(
        "Internal Server Error, Please try again later!", mimetype="text/plain", status=500)
    traceback.print_exc()
  except:
    result['success'] = False
    result['error'] = Response(
        "Internal Server Error, Please try again later!", mimetype="text/plain", status=500)
    traceback.print_exc()

  dbconn.close_all(conn, cursor)

  return result


def input_handler(endpoint_args, u_inputs=[]):
  '''
  u_inputs should be a list of dicts for each input, which can be optional or required.
  endpoint_args will be either request.args or request.json

  # ? this is how we pass the inputs for each endpoint.
  [
    {
      required: True,
      name: var_name,
      type: str
    },
    {
      required: True,
      name: var_name,
      type: int
    }
  ]
  '''
  # payload will be the result we return
  payload = {
      'success': True,
      'error': None,
      'data': {}
  }
  for u_input in u_inputs:
    # u_input will be a dictionry
    try:
      if(u_input.get('rule') != None and endpoint_args.get(u_input['name']) != None):
        result = u_input['rule'](endpoint_args[u_input['name']])

        if(result['success'] == False):
          payload['success'] = False
          payload['error'] = result['message']
          return payload

      # if the user input is required, we add a key value pair inside the data dictionary in payload. key will be the value from name, and value will be
      # the the value of name as a key in endpoint_args, wrapped in the type value.
      # ie: loginToken: str(request.json['loginToken'])
      if(u_input['required'] == True):
        payload['data'][u_input['name']] = u_input['type'](
            endpoint_args[u_input['name']])
      else:
        # if user input is not required, and the user did pass data we do the same as above, we dont use .get in the setting of the key
        # because we know there was some data passed.
        if(endpoint_args.get(u_input['name']) != None and endpoint_args.get(u_input['name']) != ''):
          payload['data'][u_input['name']] = u_input['type'](
              endpoint_args[u_input['name']])
        else:
          payload['data'][u_input['name']] = None
    # exceptions that set the success key to False and the response to f strings to be more specific about what went wrong.
    except ValueError:
      traceback.print_exc()
      payload['success'] = False
      payload['error'] = Response(
          f"Error: {u_input['name']} is invalid!", mimetype="text/plain", status=422)
    except KeyError:
      traceback.print_exc()
      payload['success'] = False
      payload['error'] = Response(
          f"Required field {u_input['name']} is empty!", mimetype="text/plain", status=422)
    except:
      traceback.print_exc()
      payload['success'] = False
      payload['error'] = Response(
          f"Error: Unknown data error with {u_input['name']}", mimetype="text/plain", status=400)

  return payload


# Create salt function for returning a salt to later insert into the DB on user registration.
# usees string lib and random lib to create a random 10 char string of letters and numbers.
def create_salt():
  letters_and_digits = string.ascii_letters + string.digits
  salt = ''.join(random.choice(letters_and_digits) for i in range(10))
  return salt


# function that takes username or email of the user as their "identity" and returns their salt from the DB for adding to the password before hashing.
def get_salt(identity):
  payload = {
      'success': True,
      'error': None,
      'data': {}
  }
  result = run_query("SELECT u.salt FROM users u WHERE u.username = ? OR u.email = ?", [
      identity, identity])

  if(len(result['data']) == 1):
    payload['data'] = result['data']
  else:
    payload['success'] = False
    payload['error'] = Response(
        "Authorization Error!", mimetype="text/plain", status=403)
  return payload
