from db.models.model import Model

class RoleAssign(Model):
	id : int = 0
	userID : int = 0
	roleID : int = 0

	def __init__(self, dblink):
		super().__init__("roleassign", dblink)

	def fetch(self, data):
		self.id = data[0]
		self.userID = data[1]
		self.roleID = data[2]
		return self