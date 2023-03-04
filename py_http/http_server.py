from .imports import *
from .log     import *
from .http_parser import *
from .http_data import *
from .http_response import *


# @brief Class to store the socket connection
# @param conn  : socket.socket connection class
# @param active: Bool to describe if the connection is active or not

class HttpConn:
	def __init__(self, conn: socket.socket, active: bool):
		self.conn        = conn
		self.active      = active
		self.temp_buffer = ""

	def __str__(self):
		return "HttpConn {\n" + f"Conn: {self.conn}\n" + f"active: {self.active}\n" + f"temp_buffer: {self.temp_buffer}\n" + "}\n"


# @brief HttpServer is a class of the main server. Users are meant to inherent from this class
# @param ip  : Ip address of the server
# @param port: Port of the server

class HttpServer:
	def __init__(self, ip: str, port: int):
		self.ip = ip
		self.port = port
		self.running = True
		self.__establish_server()


	# @brief Function to create socket server

	def __establish_server(self):
		try:
			self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
			self.server.bind((self.ip, self.port))
		except Exception as e:
			server_error(f"Failed to create server on ({self.ip}:{self.port}).\nReason: {e}")


	# @brief Function that reads static files and converts it into HttpData
	# @param file_name = Name of the file to read
	# @return Returns the HttpData of the file

	def read_static_file(self, file_name: str) -> HttpData:
		if not os.path.exists(file_name):
			server_error(f"Failed to locate file: {file_name}")

		with open(file_name, "rb") as f:
			file = f.read()
		http_data = HttpData({})
		http_data.add(HTTP_STATUS, "HTTP/1.1 200 OK")
		http_data.add(CONTENT_TYPE, http_types[file_name.split(".")[-1]])
		http_data.add(CONTENT_LEN, len(file))
		http_data.add(PAYLOAD, file)
		return http_data


	# @brief Function that creates an error page and converts it into HttpData
	# @param code = Error code
	# @param erro = Error message
	# @return Returns HttpData of the error page

	def error_page(self, code: int, error: str) -> HttpData:
		html = bytes(f"""
			<html>
			<body>
				<h1>{error}</h1>
			</body>
			</html>
		""", encoding=ENCODE_FMT)

		http_data = HttpData({})
		http_data.add(HTTP_STATUS, f"HTTP/1.1 {code} " + http_response[str(code)]["message"])
		http_data.add(CONTENT_TYPE, http_types["html"])
		http_data.add(CONTENT_LEN, len(html))
		http_data.add(PAYLOAD, html)
		return http_data


	# @brief This function is resposnible for detection of payload during post request. If not received it waits to receive again
	# @param conn = HttpConn class
	# @param data = Http string
	# @return Returns bool (true: Done capturing, false: Capturing not finished)

	def __post_checker(self, conn: HttpConn, data: str) -> bool:
		parsed_recv = parse_http_to_json(data)
		if parsed_recv[REQUEST] == POST:
			if PAYLOAD not in parsed_recv:
				conn.temp_buffer = data
				return False
			payload = parsed_recv[PAYLOAD]
			if not payload:
				conn.temp_buffer = data
				return False
		return True


	# @brief Function that handles individual connections
	# @param http_conn: HttpConn object

	def __conn_handler(self, http_conn: HttpConn):
		while http_conn.active:
			recv = http_conn.conn.recv(BUFF_SIZE).decode(ENCODE_FMT)
			if recv:

				# This block resolves the loss of payload during post requests
				if http_conn.temp_buffer:
					http_conn.temp_buffer += recv
					recv = http_conn.temp_buffer

				if not self.__post_checker(http_conn, recv):
					continue
				http_conn.temp_buffer = ""

				# Parsing the received http protocol
				parsed_recv = parse_http_to_json(recv)
				http_data = HttpData(parsed_recv)

				# Handling the requests
				request = http_data.get(REQUEST)
				if request == GET:
					ret_http_data = self.get_handler(http_data.get(ENDPOINT), http_data)
				elif request == POST:
					ret_http_data = self.post_handler(http_data.get(ENDPOINT), http_data)
				else:
					server_error(f"Unknown request from client: {request}")

				if not ret_http_data:
					server_error("Return http data is not supposed to be none. Fix the returns for get and post handlers.")

				# Adding necessary headers
				ret_http_data.add(CONNECTION, KEEP_ALIVE)
				ret_http_data.add(ALLOW_ORIGIN, "*")

				# Converting http data to bytes
				ret_data = parse_httpdata_to_bytes(ret_http_data)
				http_conn.conn.send(ret_data)
			else:
				http_conn.active = False


	# @brief Function to run the server

	def run(self):
		self.server.listen()
		server_sucess(f"Server listening on ({self.ip}:{self.port})")
		while self.running:
			conn, addr = self.server.accept()
			http_conn  = HttpConn(conn, True)
			server_sucess(http_conn)
			new_thread = threading.Thread(target = self.__conn_handler, args = (http_conn,))
			new_thread.start()


