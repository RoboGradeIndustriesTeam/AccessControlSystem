from .base import API
class Login(API):
    @staticmethod
    def onRequest(jsonData):
        retData = {}
        print(jsonData)
        return retData
