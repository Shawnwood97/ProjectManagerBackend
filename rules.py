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
