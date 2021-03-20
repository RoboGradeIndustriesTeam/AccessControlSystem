import flask
from mysql.connector import connect
import os
import dotenv
from flask_cors import CORS
import uuid
from db.models.user import *
from db.models.roleassign import *
from db.models.role import *

dotenv.load_dotenv()
config = {
  'user': os.getenv("MYSQL_USER"),
  'password': os.getenv("MYSQL_PASS"),
  'host': os.getenv("MYSQL_HOST"),
  'database': os.getenv("MYSQL_DB"),
  'raise_on_warnings': True,
}
mysqldb = connect(**config)
cursor = mysqldb.cursor()
app = flask.Flask("AccessControlSystem", static_folder='', template_folder='frontend')
CORS(app)

@app.route('/', methods=["GET", "POST"])

@app.route('/index', methods=["GET", "POST"])
@app.route('/index.html', methods=["GET", "POST"])
def index():
    mysqldb.reconnect()
    print(flask.request.cookies.get('token'))
    if not flask.request.cookies.get('token') or User(mysqldb).SELECT("*", "WHERE token = \"" + flask.request.cookies.get('token') + "\"") is None:
        return flask.redirect('login.html')
    user = User(mysqldb)
    user.fetchBy(user.SELECT("*", "WHERE token = \"" + flask.request.cookies.get('token') + "\""))
    tmp = RoleAssign(mysqldb)
    roleID = tmp.SELECT("roleID", f"WHERE userID = {user.id}")
    user_role = Role(mysqldb)
    user_role.fetchBy(user_role.SELECT("*", f"WHERE id = {roleID[0]}"))
    if not user:
        return flask.redirect('login.html')
    return flask.render_template('index.html', user=user, user_role=user_role)


@app.route('/login', methods=["GET", "POST"])
@app.route('/login.html', methods=["GET", "POST"])
def login():
    mysqldb.reconnect()
    if flask.request.method == "POST":
        user = cursor.fetchone()
        user = User(mysqldb)
        user.fetchBy(user.SELECT("*", f"WHERE login = \"{flask.request.form.get('login')}\" AND password = \"{flask.request.form.get('pass')}\""))
        if user is not None:
            user_token = uuid.uuid1()
            user.UPDATE({"token": str(user_token)}, f"WHERE id = {user.id}")
            mysqldb.commit()
            res = flask.redirect('/')
            res.set_cookie('token', bytes(str(user_token).encode()), max_age=60*60*24*365*5)
            return res
    return flask.render_template("login.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8074, debug=True)