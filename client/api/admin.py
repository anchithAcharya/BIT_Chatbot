import json
import requests

root = 'http://127.0.0.1:7000/api/student'

def get_all_students(token, page=1):
	response = requests.get(headers={'Authorization': 'Token ' + token}, url=f"{root}?page={page}")
	dict = json.loads(response.text)
	return dict, response.status_code

def login(id, password):
	response = requests.post(url=f"{root}/login/", data={'id': id, 'password': password})
	dict = json.loads(response.text)
	return dict, response.status_code, response.cookies

def logout(token):
	response = requests.post(headers={'Authorization': 'Token ' + token}, url=f"{root}/logout/")
	dict = json.loads(response.text)
	return dict, response.status_code