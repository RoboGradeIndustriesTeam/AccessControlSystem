from db.models.model import Model

class Role(Model):
	id : int = 0
	roleName : str = ""
	roleColor : str = ""

	isAdmin : int = 0
	isOrg : int = 0
	isSec : int = 0

	def __init__(self, dblink):
		super().__init__("roles", dblink)

	def fetch(self, data):
		self.id = data[0]
		self.roleName = data[1]
		self.roleColor = data[2]

		self.isAdmin = data[3]
		self.isSec = data[4]
		return self
