from py_http import *

class Server(HttpServer):
	def __init__(self, root_dir: str):
		super().__init__("127.0.0.1", 5050)
		self.root_dir = root_dir

	def get_handler(self, endpoint: str, http_data: HttpData) -> HttpData:
		file_name = self.root_dir + endpoint
		if endpoint == "/":
			return self.read_static_file(file_name + "index.html")
		elif os.path.exists(file_name):
			return self.read_static_file(file_name)
		else:
			return self.error_page(500, f"Unknown endpoint: {endpoint}")

	def post_handler(self, endpoint: str, http_data: HttpData) -> HttpData:
		print(http_data.get(PAYLOAD))
		return self.error_page(500, f"Failed payload")

if __name__ == "__main__":
	sv = Server("web")
	sv.run()

