import json
import requests

from common import root


# Student authentication
def login(id, password):
	response = requests.post(url=f"{root}/student/login/", data={'id': id, 'password': password})
	dict = json.loads(response.text)
	return dict, response.status_code, response.cookies

def logout(token):
	response = requests.post(headers={'Authorization': 'Token ' + token}, url=f"{root}/student/logout/")
	dict = json.loads(response.text)
	return dict, response.status_code

def change_password(id):
	response = requests.post(url=f"{root}/student/change_password/", data={'id': id})
	dict = json.loads(response.text)
	return dict, response.status_code

def reset_password(password_reset_token, new_password):
	response = requests.post(url=f"{root}/student/reset_password/", params={'token': password_reset_token}, data={'password': new_password})
	dict = json.loads(response.text)
	return dict, response.status_code
