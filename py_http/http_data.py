from .imports import *
from .log import *

class HttpData:
	def __init__(self, http_json: json):
		self.__data = http_json

	def __str__(self):
		string = ""
		for key in self.__data:
			string += f"    {key}: {self.__data[key]}\n"
		return "HttpData {\n" + string + "}\n"

	def get_all(self):
		return self.__data

	def has(self, key: str) -> bool:
		return key in self.__data

	def get(self, key: str):
		if key not in self.__data:
			server_error(f"Unknown key for http_data: {key}.")
		return self.__data[key]

	def pop(self, key: str):
		if key not in self.__data:
			server_error(f"Unknown key for http_data: {key}.")
		return self.__data.pop(key)

	def add(self, key: str, value):
		self.__data.update({key: value})

	def remove(self, key: str):
		if key not in self.__data:
			server_error(f"Unknown key for http_data: {key}.")
		self.__data.pop(key)

