from db.models.model import Model

class ObjectSec(Model):
	id : int = 0
	userID : int = 0
	objectID : int = 0

	def __init__(self, dblink):
		super().__init__("objectssecs", dblink)

	def fetch(self, data):
		self.id = data[0]
		self.userID = data[1]
		self.objectID = data[2]
		return self