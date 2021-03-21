from db.models.model import Model

class Log(Model):
	id : int = 0
	date : int = 0
	success : int = 0

	def __init__(self, dblink):
		super().__init__("logs", dblink)

	def fetch(self, data):
		self.id = data[0]
		self.date = data[1]
		self.success = data[2]
		return self