
class Model:
	name = ""

	def __init__(self, name, dblink):
		self.db = dblink
		self.name = name
		self.cursor = dblink.cursor(buffered=True)

	def sql(self, sql):
		print(sql)
		self.cursor.execute(sql)

	def fetchone(self):
		data = self.cursor.fetchone()
		return data

	def fetchall(self):
		return self.cursor.fetchall()

	def commit(self):
		self.db.commit()

	def SELECT(self, FIELDS="*", ADDITIONAL="", oneOrAll=False):
		sql = "SELECT " + FIELDS + " FROM " + self.name + " " + ADDITIONAL
		self.sql(sql)
		if oneOrAll:
			return self.fetchall()
		return self.fetchone()

	def INSERT(self, VALUES : tuple):
		sql = "INSERT INTO " + self.name + " VALUES " + str(VALUES)
		
		self.sql(sql)
		self.commit()
		return self.SELECT("*", "ORDER BY id DESC LIMIT 1")

	def UPDATE(self, FIELDS : dict, ADDITIONAL=""):
		sql = "UPDATE " + self.name + " SET"
		for i in FIELDS.keys():
			if type(FIELDS[i]) != str:
				sql += " " + i + " = " + FIELDS[i]
			else:
				sql += " " + i + " = \"" + FIELDS[i] + "\""
		sql += " " + ADDITIONAL
		self.sql(sql)
		self.commit()

	def fetchBy(self, data):
		try:
			self.fetch(data)
		except TypeError:
			pass