from db.models.model import Model

class Object(Model):
	id : int = 0
	userOrgID : int = 0
	name : str = ""
	address : str = ""

	def __init__(self, dblink):
		super().__init__("objects", dblink)

	def fetch(self, data):
		self.id = data[0]
		self.userOrgID = data[1]
		self.name = data[2]
		self.address = data[3]
		return self