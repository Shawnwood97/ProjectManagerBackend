from flask import Flask, request, Response
import json
import traceback
import sys
import mariadb
import users
import login
import project
import projectinvite
import projecttasks

app = Flask(__name__)

#! =========== /API/USERS ENDPOINT ============


@app.post('/api/users')
def call_create_user():
  return users.create_user()


@app.get('/api/users')
def call_list_user():
  return users.list_user()


@app.patch('/api/users')
def call_update_user():
  return users.update_user()


@app.delete('/api/users')
def call_delete_user():
  return users.delete_user()

#! =========== /API/USERS/PASSWORD ENDPOINT ============


@app.patch('/api/users/password')
def call_change_password():
  return users.change_password()

#! =========== /API/LOGIN ENDPOINT ============


@app.post('/api/login')
def call_login_user():
  return login.login_user()


@app.delete('/api/login')
def call_logout_user():
  return login.logout_user()

#! =========== /API/PROJECT ENDPOINT ============


@app.post('/api/project')
def call_create_project():
  return project.create_project()


@app.delete('/api/project')
def call_delete_project():
  return project.delete_project()


@app.get('/api/project')
def call_get_project():
  return project.get_project()


@app.patch('/api/project')
def call_update_project():
  return project.update_project()


#! =========== /API/PROJECTS/OWNED ENDPOINT ============


@app.get('/api/projects/owned')
def call_list_owned_projects():
  return project.list_owned_projects()

#! =========== /API/PROJECTS/ACCEPTED ENDPOINT ============


@app.get('/api/projects/accepted')
def call_list_accepted_projects():
  return project.list_accepted_projects()

#! =========== /API/PROJECT/INVITE ENDPOINT ============


@app.post('/api/project/invite')
def call_invite_user():
  return projectinvite.invite_user()


@app.get('/api/project/invite')
def call_list_pending_invites():
  return projectinvite.list_pending_invites()


@app.patch('/api/project/invite')
def call_invite_response():
  return projectinvite.invite_response()

#! =========== /API/TASK ENDPOINT ============


@app.post('/api/tasks')
def call_create_task():
  return projecttasks.create_task()


@app.patch('/api/tasks')
def call_update_task():
  return projecttasks.update_task()


@app.delete('/api/tasks')
def call_delete_task():
  return projecttasks.delete_task()


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
