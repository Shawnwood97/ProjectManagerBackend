from flask import Flask, request, Response
import json
import traceback
import sys
import mariadb
import users

app = Flask(__name__)


@app.post('/api/users')
def call_create_user():
  return users.create_user()


@app.get('/api/users')
def call_list_user():
  return users.list_user()


@app.patch('/api/users')
def call_update_user():
  return users.update_user()


@app.patch('/api/users/password')
def call_change_password():
  return users.change_password()


if(len(sys.argv) > 1):
  mode = sys.argv[1]
else:
  print("No mode argument, please pass a mode argument when invoking the file!")
  exit()

if(mode == "prod"):
  import bjoern  # type: ignore
  bjoern.run(app, "0.0.0.0", 5015)
elif(mode == "test"):
  from flask_cors import CORS
  CORS(app)
  app.run(debug=True)
else:
  print("Invalid mode, please select either 'prod' or 'test'")
  exit()
