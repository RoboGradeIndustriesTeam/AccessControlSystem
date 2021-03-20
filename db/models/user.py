from db.models.model import Model

class User(Model):
	id : int = 0
	login : str = ""
	password : str = ""
	token : str = ""

	def __init__(self, dblink):
		super().__init__("users", dblink)

	def fetch(self, data):
		self.id = data[0]
		self.login = data[1]
		self.password = data[2]
		self.token = data[3]
		return self