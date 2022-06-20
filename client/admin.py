import json
import requests

from .common import root

# Admin authentication
def login(id, password):
	response = requests.post(url=f"{root}/admin/login/", data={'id': id, 'password': password})
	dict = json.loads(response.text)
	return dict, response.status_code, response.cookies

def logout(token):
	response = requests.post(headers={'Authorization': 'Token ' + token}, url=f"{root}/admin/logout/")
	dict = json.loads(response.text)
	return dict, response.status_code

def change_password(id):
	response = requests.post(url=f"{root}/admin/change_password/", data={'id': id})
	dict = json.loads(response.text)
	return dict, response.status_code

def reset_password(password_reset_token, new_password):
	response = requests.post(url=f"{root}/admin/reset_password/", params={'token': password_reset_token}, data={'password': new_password})
	dict = json.loads(response.text)
	return dict, response.status_code

# Manage Students:

# Non-detail
def get_all_students(token, page=1):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/student/?page={page}")
	dict = json.loads(response.text)
	return dict, response.status_code

def create_new_student(token, data, files=None):
	response = requests.post(headers={'Authorization': 'Token ' + token}, url=f"{root}/student/", data=data, files=files)
	dict = json.loads(response.text)
	return dict, response.status_code


# Detail
def get_student_details(token, id):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/student/{id}")
	dict = json.loads(response.text)
	return dict, response.status_code

def edit_student_details(token, id, data, files=None):
	response = requests.patch(headers={'Authorization': 'Token ' + token}, url=f"{root}/student/{id}/", data=data, files=files)
	dict = json.loads(response.text)
	return dict, response.status_code

def get_student_marks_brief(token, id):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/student/{id}/marks")
	dict = json.loads(response.text)
	return dict, response.status_code

def get_student_attendance_brief(token, id):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/student/{id}/attendance")
	dict = json.loads(response.text)
	return dict, response.status_code

def delete_student(token, id):
	response = requests.delete(headers={'Authorization': 'Token ' + token}, url=f"{root}/student/{id}/")
	dict = json.loads(response.text)
	return dict, response.status_code



# Manage Staff:

# Non-detail
def get_all_staff(token, page=1):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/staff/?page={page}")
	dict = json.loads(response.text)
	return dict, response.status_code

def create_new_staff(token, data, files=None):
	response = requests.post(headers={'Authorization': 'Token ' + token}, url=f"{root}/staff/", data=data, files=files)
	dict = json.loads(response.text)
	return dict, response.status_code


# Detail
def get_staff_details(token, id):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/staff/{id}")
	dict = json.loads(response.text)
	return dict, response.status_code

def edit_staff_details(token, id, data, files=None):
	response = requests.patch(headers={'Authorization': 'Token ' + token}, url=f"{root}/staff/{id}/", data=data, files=files)
	dict = json.loads(response.text)
	return dict, response.status_code

def delete_staff(token, id):
	response = requests.delete(headers={'Authorization': 'Token ' + token}, url=f"{root}/staff/{id}/")
	dict = json.loads(response.text)
	return dict, response.status_code
