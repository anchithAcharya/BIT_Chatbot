import json
import requests

from common import root


# Staff authentication
def login(id, password):
	response = requests.post(url=f"{root}/staff/login/", data={'id': id, 'password': password})
	dict = json.loads(response.text)
	return dict, response.status_code, response.cookies

def logout(token):
	response = requests.post(headers={'Authorization': 'Token ' + token}, url=f"{root}/staff/logout/")
	dict = json.loads(response.text)
	return dict, response.status_code

def forgot_password(id):
	response = requests.post(url=f"{root}/staff/forgot_password/", data={'id': id})
	dict = json.loads(response.text)
	return dict, response.status_code

def reset_password(password_reset_token, new_password):
	response = requests.post(url=f"{root}/staff/password_reset/", params={'token': password_reset_token}, data={'password': new_password})
	dict = json.loads(response.text)
	return dict, response.status_code
