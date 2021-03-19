from .base import API
import _md5

class Login(API):
    @staticmethod
    def onRequest(jsonData, mysqldb):
        retData = {}
        print(jsonData)
        cursor = mysqldb.cursor()
        cursor.execute("SELECT * FROM users WHERE login = %s AND password = %s", (jsonData['login'], jsonData['password']))
        data = cursor.fetchone()
        if not data:
            return {"error": 1}
        retData = {'id': data[0], 'login': data[1], "password": data[2]}
        return retData