from db.models.model import Model

class NFCAcc(Model):
	id : int = 0
	nfcID : int = 0
	orgID : int = 0

	def __init__(self, dblink):
		super().__init__("nfcaccs", dblink)

	def fetch(self, data):
		self.id = data[0]
		self.nfcID = data[1]
		self.orgID = data[2]
		return self