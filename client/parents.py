import json
import requests

from .common import root


# Parents authentication
def login(id, password):
	response = requests.post(url=f"{root}/parent/login/", data={'id': id, 'password': password})
	dict = json.loads(response.text)
	return dict, response.status_code, response.cookies

def logout(token):
	response = requests.post(headers={'Authorization': 'Token ' + token}, url=f"{root}/parent/logout/")
	dict = json.loads(response.text)
	return dict, response.status_code

def forgot_password(id):
	response = requests.post(url=f"{root}/parent/forgot_password/", data={'id': id})
	dict = json.loads(response.text)
	return dict, response.status_code

def reset_password(password_reset_token, new_password):
	response = requests.post(url=f"{root}/parent/password_reset/", params={'token': password_reset_token}, data={'password': new_password})
	dict = json.loads(response.text)
	return dict, response.status_code

def change_password(token, data):
	response = requests.patch(headers={'Authorization': 'Token ' + token}, url=f"{root}/parent/me/", data=data)
	dict = json.loads(response.text)
	return dict, response.status_code


# Parents account
def get_account_details(token):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/parent/me")
	dict = json.loads(response.text)
	return dict, response.status_code

def edit_account_details(token, data, files=None):
	response = requests.patch(headers={'Authorization': 'Token ' + token}, url=f"{root}/parent/me/", data=data, files=files)
	dict = json.loads(response.text)
	return dict, response.status_code


def get_student_details(token):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/parent/me/student")
	dict = json.loads(response.text)
	return dict, response.status_code

def get_student_marks_report(token):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/parent/me/student/marks")
	dict = json.loads(response.text)
	return dict, response.status_code

def get_student_attendance_report(token):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/parent/me/student/attendance")
	dict = json.loads(response.text)
	return dict, response.status_code
