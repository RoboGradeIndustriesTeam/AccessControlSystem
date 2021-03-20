import flask
from mysql.connector import connect
import os
import dotenv
from flask_cors import CORS
import uuid
from db.models.user import *
from db.models.roleassign import *
from db.models.role import *
from db.models.nfcaccs import *
from db.models.object import *
from db.models.objectsecs import *
from db.models.task import *


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
    if not flask.request.cookies.get('token') or User(mysqldb).SELECT("*", "WHERE token = \"" + flask.request.cookies.get('token') + "\"") is None:
        return flask.redirect('login.html')
    user = User(mysqldb)
    user.fetchBy(user.SELECT("*", "WHERE token = \"" + flask.request.cookies.get('token') + "\""))
    tmp = RoleAssign(mysqldb)
    roleID = tmp.SELECT("roleID", f"WHERE userID = {user.id}")
    user_role = Role(mysqldb)
    user_role.fetchBy(user_role.SELECT("*", f"WHERE id = {roleID[0]}"))
    objects = Object(mysqldb).SELECT("*", f"WHERE userOrgID = {user.id}", True)
    nfcAccs = 0
    objectsLen = 0
    secs = 0
    taskslen = 0
    if objects:
        for i in objects:
            nfcaccsinobject = len(NFCAcc(mysqldb).SELECT("*", f"WHERE orgID = {i[0]}", True))
            nfcAccs += nfcaccsinobject
        objectsLen = len(objects)
        for i in objects:
            secsinpobjects = len(ObjectSec(mysqldb).SELECT("*", f"WHERE objectID = {i[0]}", True))
            secs += secsinpobjects
        for i in objects:
            tasksinprojects = len(Task(mysqldb).SELECT("*", f"WHERE orgID = {i[0]}", True))
            taskslen += tasksinprojects
    print("Objects: ", objectsLen, "\nNFCAccs: ", nfcAccs, "\nSecurities: ", secs, "\nTasks: ", taskslen)
    if not user:
        return flask.redirect('login.html')
    return flask.render_template('index.html', user=user, user_role=user_role, userAnalitycs=[taskslen, objectsLen, secs, nfcAccs])


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


@app.route("/create_a_bypass", methods=["GET", "POST"])
@app.route("/create_a_bypass.html", methods=["GET", "POST"])
def crBypass():
    mysqldb.reconnect()
    if not flask.request.cookies.get('token') or User(mysqldb).SELECT("*", "WHERE token = \"" + flask.request.cookies.get('token') + "\"") is None:
        return flask.redirect('login.html')
    user = User(mysqldb)
    user.fetchBy(user.SELECT("*", "WHERE token = \"" + flask.request.cookies.get('token') + "\""))
    tmp = RoleAssign(mysqldb)
    roleID = tmp.SELECT("roleID", f"WHERE userID = {user.id}")
    user_role = Role(mysqldb)
    user_role.fetchBy(user_role.SELECT("*", f"WHERE id = {roleID[0]}"))
    objects = Object(mysqldb).SELECT("*", f"WHERE userOrgID = {user.id}", True)
    nfces = []
    nfcAccs = 0
    objectsLen = 0
    secs = 0
    secss = []
    taskslen = 0
    if objects:
        for i in objects:
            nfc = NFCAcc(mysqldb).SELECT("*", f"WHERE orgID = {i[0]}", True)
            nfces.extend(nfc)
            nfcaccsinobject = len(nfc)
            nfcAccs += nfcaccsinobject
        objectsLen = len(objects)
        for i in objects:
            ssecs = ObjectSec(mysqldb).SELECT("*", f"WHERE objectID = {i[0]}", True)
            for j in ssecs:
                secss.append(User(mysqldb).SELECT("*", f"WHERE id = {j[1]}"))
            secsinpobjects = len(ssecs)
            secs += secsinpobjects
        for i in objects:
            tasksinprojects = len(Task(mysqldb).SELECT("*", f"WHERE orgID = {i[0]}", True))
            taskslen += tasksinprojects
    
    if flask.request.method == "POST":
        name = flask.request.form.get("name")
        date = flask.request.form.get("daterange")
        nfcs = flask.request.form.getlist("states")
        sec = flask.request.form.get("sec")
        objID = flask.request.form.get("obj")
        nfcss = ""
        for i in nfcs:
            nfcss += i + ","
        Task(mysqldb).INSERT(f"(NULL, {objID}, {user.id}, {sec}, \"{name}\", \"{date}\", \"{nfcss}\")")

    return flask.render_template('create_bypass.html', user=user, user_role=user_role, userAnalitycs=[taskslen, objectsLen, secs, nfcAccs], nfces=nfces, secs=secss, objects=objects)
app.jinja_env.globals.update(len=len, User=User, Role=Role, RoleAssign=RoleAssign, NFCAcc=NFCAcc, Task=Task, Object=Object, ObjectSec=ObjectSec, mysqldb=mysqldb)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8074, debug=True)