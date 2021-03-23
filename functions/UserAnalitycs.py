import db.models

class UserAnalitycs:
    nfcTags : db.models.nfcaccs.NFCAcc = []
    securityUsers : db.models.objectsecs.ObjectSec = []
    objects : db.models.object.Object = []
    tasks : db.models.task.Task = []


    def fetch(self, mysqldb, userID):
        objects = db.models.object.Object(mysqldb).SELECT("*", f"WHERE userOrgID = {userID}", True)
        self.objects = objects
        self.securityUsers = []
        self.nfcTags = []
        self.tasks = []
        nfcAccs = 0
        objectsLen = 0
        securityUsersLen = 0
        tasksLen = 0
        if objects:
            for i in objects:
                tmp = db.models.nfcaccs.NFCAcc(mysqldb).SELECT("*", f"WHERE orgID = {i[0]}", True)
                self.nfcTags.extend(tmp)
                nfcaccsinobject = len(tmp)
                securityUsersLen += nfcaccsinobject
            objectsLen = len(objects)
            for i in objects:
                tmp = db.models.objectsecs.ObjectSec(mysqldb).SELECT("*", f"WHERE objectID = {i[0]}", True)
                self.securityUsers.extend(tmp)
                secsinpobjects = len(tmp)
                securityUsersLen += secsinpobjects
            for i in objects:
                tmp = db.models.task.Task(mysqldb).SELECT("*", f"WHERE orgID = {i[0]}", True)
                self.tasks.extend(tmp)
                tasksinprojects = len(tmp)
                tasksLen += tasksinprojects
        return [tasksLen, objectsLen, securityUsersLen, nfcAccs]