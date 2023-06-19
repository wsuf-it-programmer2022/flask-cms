from flask import Blueprint, render_template, request, redirect, url_for, flash
from os import environ
import requests
from oauthlib.oauth2 import WebApplicationClient
import json
from python_cms.models.user import UserModel
from flask_login import login_user, logout_user

auth_blueprint = Blueprint('auth', __name__)

GOOGLE_CLIENT_ID = environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = environ.get('GOOGLE_CLIENT_SECRET')

GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration")

client = WebApplicationClient(GOOGLE_CLIENT_ID)


@auth_blueprint.route('/login')
def login():
  google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
  authorization_endpoint = google_provider_cfg["authorization_endpoint"]
  request_uri = client.prepare_request_uri(
      authorization_endpoint,
      redirect_uri=request.host_url + "authorize",
      scope=["openid", "email", "profile"])

  print(request_uri)

  return redirect(request_uri)


@auth_blueprint.route('/authorize')
def authorize():
  code = request.args.get("code")
  google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
  token_endpoint = google_provider_cfg["token_endpoint"]
  token_url, headers, body = client.prepare_token_request(
      token_endpoint,
      authorization_response=request.url,
      redirect_url=request.base_url,
      code=code)
  token_response = requests.post(token_url,
                                 headers=headers,
                                 data=body,
                                 auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET))

  print(token_response.json())

  client.parse_request_body_response(json.dumps(token_response.json()))

  # now we have the token, we can get the user info
  userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
  uri, headers, body = client.add_token(userinfo_endpoint)
  userinfo_response = requests.get(uri, headers=headers)

  print(userinfo_response.json())

  if userinfo_response.json().get("email_verified"):
    unique_id = userinfo_response.json()["sub"]
    users_email = userinfo_response.json()["email"]
    picture = userinfo_response.json()["picture"]
    users_name = userinfo_response.json()["name"]
    user = UserModel(id=unique_id,
                     name=users_name,
                     email=users_email,
                     picture=picture)

    # if the user doesn't exist, create a new one
    if not UserModel.get(unique_id):
      user.save()

    # begin user session by logging in the user
    login_user(user)

    return redirect(url_for('pages.index'))

  return "User email not available or not verified by Google.", 400


@auth_blueprint.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('pages.index'))
