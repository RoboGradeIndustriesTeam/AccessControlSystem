import flask
from apievents.login import Login
from mysql.connector import connect
import os
import dotenv

dotenv.load_dotenv()
config = {
  'user': os.getenv("MYSQL_USER"),
  'password': os.getenv("MYSQL_PASS"),
  'host': os.getenv("MYSQL_HOST"),
  'database': os.getenv("MYSQL_DB"),
  'raise_on_warnings': True,
}

mysqldb = connect(**config)
APIDict = {"auth": Login}

app = flask.Flask("AccesControlSystem")
"""
Request structure
{
    "name": "<ApiClassName>",
    "data":{
        <DataForApi>
    }
}
"""
@app.route('/api', methods=["POST"])
def api():
    reqjson = flask.request.json
    try:
        return flask.jsonify(APIDict[reqjson["name"]].onRequest(reqjson['data'], mysqldb))
    except KeyError:
        return flask.jsonify({"error": 0})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8074, debug=True)