import json
import requests


root = 'http://127.0.0.1:7000/api'


# Marks:

# Non-detail
def get_all_marks(token, student=None, subject=None, branch=None, semester=None, page=1):
	params = {
		'student': student,
		'subject': subject,
		'branch': branch,
		'semester': semester,
		'page': page
	}

	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/marks", params=params)
	dict = json.loads(response.text)
	return dict, response.status_code

def add_marks(token, data):
	response = requests.post(headers={'Authorization': 'Token ' + token}, url=f"{root}/marks/", data=data)
	dict = json.loads(response.text)
	return dict, response.status_code

def get_marks_brief(token, id):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/student/{id}/marks/brief")
	dict = json.loads(response.text)
	return dict, response.status_code

def get_marks_report(token, id):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/student/{id}/marks/report")
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
def get_all_attendance(token, student=None, subject=None, branch=None, semester=None, page=1):
	params = {
		'student': student,
		'subject': subject,
		'branch': branch,
		'semester': semester,
		'page': page
	}

	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/attendance", params=params)
	dict = json.loads(response.text)
	return dict, response.status_code

def add_attendance(token, data):
	response = requests.post(headers={'Authorization': 'Token ' + token}, url=f"{root}/attendance/", data=data)
	dict = json.loads(response.text)
	return dict, response.status_code

def get_attendance_brief(token, id):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/student/{id}/attendance/brief")
	dict = json.loads(response.text)
	return dict, response.status_code

def get_attendance_report(token, id):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/student/{id}/attendance/report")
	dict = json.loads(response.text)
	return dict, response.status_code


# Detail
def get_attendance_details(token, student_id, subject_id):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/attendance/{student_id}-{subject_id}")
	dict = json.loads(response.text)
	return dict, response.status_code

def edit_attendance_details(token, student_id, subject_id, data):
	response = requests.patch(headers={'Authorization': 'Token ' + token}, url=f"{root}/attendance/{student_id}-{subject_id}/", data=data)
	dict = json.loads(response.text)
	return dict, response.status_code

def delete_attendance(token, student_id, subject_id):
	response = requests.delete(headers={'Authorization': 'Token ' + token}, url=f"{root}/attendance/{student_id}-{subject_id}/")
	dict = json.loads(response.text)
	return dict, response.status_code



# Metadata:
def get_branch_names(token):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/metadata/branches")
	dict = json.loads(response.text)
	return dict, response.status_code