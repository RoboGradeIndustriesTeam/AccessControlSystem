from db.models.model import Model

class RoleAssign(Model):
	id : int = 0
	orgID : int = 0
	userID : int = 0
	byUserID : int = 0

	taskName : str = ""
	taskDesc : str = ""
	nfcTags : str = "" # .split(",")

	def __init__(self, dblink):
		super().__init__("tasks", dblink)

	def fetch(self, data):
		self.id = data[0]
		self.orgID = data[1]
		self.userID = data[2]
		self.byUserID = data[3]

		self.taskName = data[4]
		self.taskDesc = data[5]
		self.nfcTags = data[6]
		return self