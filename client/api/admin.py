import json
import requests

root = 'http://127.0.0.1:7000/api/student'

def login(id, password):
	response = requests.post(url=f"{root}/login/", data={'id': id, 'password': password})
	dict = json.loads(response.text)
	return dict, response.status_code, response.cookies

def logout(token):
	response = requests.post(headers={'Authorization': 'Token ' + token}, url=f"{root}/logout/")
	dict = json.loads(response.text)
	return dict, response.status_code

def get_all_students(token, page=1):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}?page={page}")
	dict = json.loads(response.text)
	return dict, response.status_code

def get_student_details(token, id):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}/{id}")
	dict = json.loads(response.text)
	return dict, response.status_code

def edit_student_details(token, id, data):
	response = requests.patch(headers={'Authorization': 'Token ' + token}, url=f"{root}/{id}/", data=data)
	dict = json.loads(response.text)
	return dict, response.status_code

def delete_student(token, id):
	response = requests.delete(headers={'Authorization': 'Token ' + token}, url=f"{root}/{id}/")
	return response.status_code
