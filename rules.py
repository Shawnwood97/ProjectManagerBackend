from flask import Response


def password_checker(test_str):
  payload = {
      'success': True,
      'message': None
  }

  if(len(test_str) < 8):
    payload['success'] = False
    payload['message'] = Response(
        "Password is not long enough!", mimetype="text/plain", status=400)
  return payload


def username_checker(test_str):
  payload = {
      'success': True,
      'message': None
  }

  if(len(test_str) < 5):
    payload['success'] = False
    payload['message'] = Response(
        "Username is not long enough!", mimetype="text/plain", status=400)
  return payload


def role_checker(num):
  payload = {
      'success': True,
      'message': None
  }

  if(num != 1 and num != 2):
    payload['success'] = False
    payload['message'] = Response(
        "Invalid role_id", mimetype="text/plain", status=400)
  return payload


def invite_checker(num):
  payload = {
      'success': True,
      'message': None
  }

  if(num != 0 and num != 1):
    payload['success'] = False
    payload['message'] = Response(
        "Invalid accept_invite value passed!", mimetype="text/plain", status=400)
  return payload
