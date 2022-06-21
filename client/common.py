import json
import requests


root = 'http://127.0.0.1:7000/api'


# Marks:

# Non-detail
def get_all_marks(token, student_id=None, subject_id=None, page=1):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/marks/?page={page}", params={'student': student_id, 'subject': subject_id})
	dict = json.loads(response.text)
	return dict, response.status_code

def add_marks(token, data):
	response = requests.post(headers={'Authorization': 'Token ' + token}, url=f"{root}/marks/", data=data)
	dict = json.loads(response.text)
	return dict, response.status_code


# Detail
def get_marks_details(token, student_id, subject_id):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/marks/{student_id}-{subject_id}")
	dict = json.loads(response.text)
	return dict, response.status_code

def edit_marks_details(token, student_id, subject_id, data):
	response = requests.patch(headers={'Authorization': 'Token ' + token}, url=f"{root}/marks/{student_id}-{subject_id}/", data=data)
	dict = json.loads(response.text)
	return dict, response.status_code

def delete_marks(token, student_id, subject_id):
	response = requests.delete(headers={'Authorization': 'Token ' + token}, url=f"{root}/marks/{student_id}-{subject_id}/")
	dict = json.loads(response.text)
	return dict, response.status_code



# Attendance:

# Non-detail
def get_all_atendance(token, student_id=None, subject_id=None, page=1):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/atendance/?page={page}", params={'student': student_id, 'subject': subject_id})
	dict = json.loads(response.text)
	return dict, response.status_code

def add_atendance(token, data):
	response = requests.post(headers={'Authorization': 'Token ' + token}, url=f"{root}/atendance/", data=data)
	dict = json.loads(response.text)
	return dict, response.status_code


# Detail
def get_atendance_details(token, student_id, subject_id):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/atendance/{student_id}-{subject_id}")
	dict = json.loads(response.text)
	return dict, response.status_code

def edit_atendance_details(token, student_id, subject_id, data):
	response = requests.patch(headers={'Authorization': 'Token ' + token}, url=f"{root}/atendance/{student_id}-{subject_id}/", data=data)
	dict = json.loads(response.text)
	return dict, response.status_code

def delete_atendance(token, student_id, subject_id):
	response = requests.delete(headers={'Authorization': 'Token ' + token}, url=f"{root}/atendance/{student_id}-{subject_id}/")
	dict = json.loads(response.text)
	return dict, response.status_code



# Metadata:
def get_branch_names():
	response = requests.get(url=f"{root}/metadata/branches")
	dict = json.loads(response.text)
	return dict, response.status_code