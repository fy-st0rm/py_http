from .log import *
from .http_data import *
from .defines import *

def parse_http_to_json(http: str) -> dict:
	http_json = {}

	lines = http.split("\r\n\r\n")
	meta_lines = lines[0]
	payload    = lines[1]

	# Parsing the first line 
	meta_lines = meta_lines.split("\r\n")
	request  = meta_lines.pop(0)
	request, endpoint, http_ver = request.split(" ")
	http_json.update({
		REQUEST      : request,
		ENDPOINT     : endpoint,
		HTTP_VERSION : http_ver
	})

	# Parsing meta data 
	for meta in meta_lines:
		key, val = meta.split(": ")
		http_json.update({key: val})

	# Adding the payload
	try:
		if payload:
			payload = json.loads(payload)
			http_json.update({"payload": payload})
	except Exception as e:
		server_error(f"Failed to load payload. Payload needs to be in json.\nReason: {e}.")

	return http_json


def parse_httpdata_to_bytes(http_data: HttpData) -> bytes:
	res = b""

	# Adding the status
	res += http_data.pop(HTTP_STATUS).encode(ENCODE_FMT) + b"\n"

	# Adding rest of the header
	data = http_data.get_all()
	for key in data:
		if key != PAYLOAD:
			res += f"{key}: {data[key]}\r\n".encode(ENCODE_FMT)

	# Adding payload
	if http_data.has(PAYLOAD):
		res += b"\r\n"
		payload = http_data.get(PAYLOAD)
		if type(payload) == bytes:
			res += payload
		elif type(payload) == str:
			res += http_data.get(PAYLOAD).encode(ENCODE_FMT)
		else:
			server_error(f"Unsupported payload type: {type(payload)}.")

	return res

