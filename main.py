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
from db.models.logs import *
from time import gmtime, strftime


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
    if flask.request.cookies.get('token') is not None:
        user = User(mysqldb)
        user.fetchBy(user.SELECT("*", "WHERE token = \"" + flask.request.cookies.get('token') + "\""))
        tmp = RoleAssign(mysqldb)
        
        user_role = getUserRole(user.id)

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
        userAnalitycs=[taskslen, objectsLen, secs, nfcAccs]
    else:
        if flask.request.method == "POST":
            user2 = cursor.fetchone()
            user2 = User(mysqldb)
            user2.fetchBy(user2.SELECT("*", f"WHERE login = \"{flask.request.form.get('login')}\" AND password = \"{flask.request.form.get('pass')}\""))
            if user2 is not None:
                
                user_token = str(uuid.uuid1())
                user2.UPDATE({"token": user_token}, f"WHERE id = {user2.id}")
                mysqldb.commit()
                res = flask.redirect('/')
                res.set_cookie('token', bytes(user_token.encode()), max_age=60*60*24*365*5)
                return res
        user = None
        user_role = None
        userAnalitycs = [0, 0, 0, 0]    
    return flask.render_template('index.html', user=user, user_role=user_role, userAnalitycs=userAnalitycs)



@app.route("/detours", methods=["GET", "POST"])
@app.route("/detours.html", methods=["GET", "POST"])
def crBypass():
    mysqldb.reconnect()
    
    if flask.request.cookies.get('token') is not None:
        user = User(mysqldb)
        user.fetchBy(user.SELECT("*", "WHERE token = \"" + flask.request.cookies.get('token') + "\""))
        user_role = getUserRole(user.id)
        objects = Object(mysqldb).SELECT("*", f"WHERE userOrgID = {user.id}", True)
        nfcAccs = 0
        objectsLen = 0
        secs = 0
        secss = []
        nfces = []
        tasks = []
        taskslen = 0
        if objects:
            for i in objects:
                nnfc = NFCAcc(mysqldb).SELECT("*", f"WHERE orgID = {i[0]}", True)
                nfces.extend(nnfc)
                nfcaccsinobject = len(nnfc)
                nfcAccs += nfcaccsinobject
            objectsLen = len(objects)
            for i in objects:
                secccs = ObjectSec(mysqldb).SELECT("*", f"WHERE objectID = {i[0]}", True)
                secss.extend(secccs)
                secsinpobjects = len(secccs)
                secs += secsinpobjects
            for i in objects:
                tsk = Task(mysqldb).SELECT("*", f"WHERE orgID = {i[0]}", True)
                tasks.extend(tsk)
                tasksinprojects = len(tsk)
                taskslen += tasksinprojects
        userAnalitycs=[taskslen, objectsLen, secs, nfcAccs]
        if flask.request.method == "POST" and flask.request.form.get("form-type") == "addDet":
            name = flask.request.form.get("name")
            date = flask.request.form.get("daterange")
            nfcs = flask.request.form.getlist("states")
            sec = flask.request.form.get("sec")
            objID = flask.request.form.get("obj")
            nfcss = ""
            for i in nfcs:
                nfcss += i + ","
            Task(mysqldb).INSERT(f"(NULL, {objID}, {user.id}, {sec}, \"{name}\", \"{date}\", \"{nfcss}\")")
    else:
        if flask.request.method == "POST":
            user2 = cursor.fetchone()
            user2 = User(mysqldb)
            user2.fetchBy(user2.SELECT("*", f"WHERE login = \"{flask.request.form.get('login')}\" AND password = \"{flask.request.form.get('pass')}\""))
            if user2 is not None:
                user_token = str(uuid.uuid1())
                user2.UPDATE({"token": user_token}, f"WHERE id = {user2.id}")
                mysqldb.commit()
                res = flask.redirect('/')
                res.set_cookie('token', bytes(user_token.encode()), max_age=60*60*24*365*5)
                return res
        user = None
        user_role = None
        userAnalitycs = [0, 0, 0, 0]
        secss = []
        nfces = []
        objects = []
    
    return flask.render_template('detours.html', user=user, user_role=user_role, userAnalitycs=[taskslen, objectsLen, secs, nfcAccs], nfces=nfces, secs=secss, objects=objects, tasks=tasks)

@app.route('/users', methods=["GET", "POST"])
@app.route('/users.html', methods=["GET", "POST"])
def user():
    mysqldb.reconnect()
    if flask.request.cookies.get('token') is not None:
        user = User(mysqldb)
        user.fetchBy(user.SELECT("*", "WHERE token = \"" + flask.request.cookies.get('token') + "\""))
        user_role = getUserRole(user.id)
        objects = Object(mysqldb).SELECT("*", f"WHERE userOrgID = {user.id}", True)
        nfcAccs = 0
        objectsLen = 0
        secs = 0
        users = []
        taskslen = 0
        if objects:
            for i in objects:
                nfcaccsinobject = len(NFCAcc(mysqldb).SELECT("*", f"WHERE orgID = {i[0]}", True))
                nfcAccs += nfcaccsinobject
            objectsLen = len(objects)
            for i in objects:
                ssssec = ObjectSec(mysqldb).SELECT("*", f"WHERE objectID = {i[0]}", True)
                for i in ssssec:
                    user3 = User(mysqldb)
                    users.append(user3.SELECT("*", f"WHERE id = {i[1]}"))
                secsinpobjects = len(ssssec)
                secs += secsinpobjects
            for i in objects:
                tasksinprojects = len(Task(mysqldb).SELECT("*", f"WHERE orgID = {i[0]}", True))
                taskslen += tasksinprojects
        userAnalitycs=[taskslen, objectsLen, secs, nfcAccs]
        if flask.request.method == "POST":
            ftyp = flask.request.form.get("form-type")

            if ftyp == "addUser":
                if (flask.request.form.get("user_name"),) in User(mysqldb).SELECT("login", oneOrAll=True):
                    tmp = User(mysqldb).SELECT('id', f"WHERE login = \"{flask.request.form.get('user_name')}\"")
                    ObjectSec(mysqldb).INSERT(f"(NULL, {tmp[0]}, {int(flask.request.form.get('obj'))})")
                
    else:
        if flask.request.method == "POST":
            user2 = cursor.fetchone()
            user2 = User(mysqldb)
            user2.fetchBy(user2.SELECT("*", f"WHERE login = \"{flask.request.form.get('login')}\" AND password = \"{flask.request.form.get('pass')}\""))
            if user2 is not None:
                user_token = str(uuid.uuid1())
                user2.UPDATE({"token": user_token}, f"WHERE id = {user2.id}")
                mysqldb.commit()
                res = flask.redirect('/')
                res.set_cookie('token', bytes(user_token.encode()), max_age=60*60*24*365*5)
                return res
        user = None
        user_role = None
        userAnalitycs = [0, 0, 0, 0]
        users = []
        objects = []

    return flask.render_template('users.html', user=user, user_role=user_role, userAnalitycs=[taskslen, objectsLen, secs, nfcAccs], users=users, objects=objects)

@app.route('/object', methods=["GET", "POST"])
@app.route('/object.html', methods=["GET", "POST"])
def object():
    mysqldb.reconnect()
    if flask.request.cookies.get('token') is not None:
        user = User(mysqldb)
        user.fetchBy(user.SELECT("*", "WHERE token = \"" + flask.request.cookies.get('token') + "\""))
        user_role = getUserRole(user.id)
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
        userAnalitycs=[taskslen, objectsLen, secs, nfcAccs]
    else:
        if flask.request.method == "POST":
            user2 = cursor.fetchone()
            user2 = User(mysqldb)
            user2.fetchBy(user2.SELECT("*", f"WHERE login = \"{flask.request.form.get('login')}\" AND password = \"{flask.request.form.get('pass')}\""))
            if user2 is not None:
                user_token = str(uuid.uuid1())
                user2.UPDATE({"token": user_token}, f"WHERE id = {user2.id}")
                mysqldb.commit()
                res = flask.redirect('/')
                res.set_cookie('token', bytes(user_token.encode()), max_age=60*60*24*365*5)
                return res
        user = None
        user_role = None
        userAnalitycs = [0, 0, 0, 0]    
    return flask.render_template('object.html', user=user, user_role=user_role, userAnalitycs=userAnalitycs, objects=objects)

@app.route('/nfc', methods=["GET", "POST"])
@app.route('/nfc.html', methods=["GET", "POST"])
def nfc():
    mysqldb.reconnect()
    if flask.request.cookies.get('token') is not None:
        user = User(mysqldb)
        user.fetchBy(user.SELECT("*", "WHERE token = \"" + flask.request.cookies.get('token') + "\""))
        user_role = getUserRole(user.id)
        objects = Object(mysqldb).SELECT("*", f"WHERE userOrgID = {user.id}", True)
        nfcAccs = 0
        nfces = []
        objectsLen = 0
        secs = 0
        taskslen = 0
        if objects:
            for i in objects:
                nfccc = NFCAcc(mysqldb).SELECT("*", f"WHERE orgID = {i[0]}", True)
                nfces.extend(nfccc)
                nfcaccsinobject = len(nfccc)
                nfcAccs += nfcaccsinobject
            objectsLen = len(objects)
            for i in objects:
                secsinpobjects = len(ObjectSec(mysqldb).SELECT("*", f"WHERE objectID = {i[0]}", True))
                secs += secsinpobjects
            for i in objects:
                tasksinprojects = len(Task(mysqldb).SELECT("*", f"WHERE orgID = {i[0]}", True))
                taskslen += tasksinprojects
        userAnalitycs=[taskslen, objectsLen, secs, nfcAccs]
        if flask.request.method == "POST" and flask.request.form.get("form-type") == "addNFC":
            NFCAcc(mysqldb).INSERT(f"(NULL, {flask.request.form.get('data')}, {flask.request.form.get('obj')} )")
    else:
        if flask.request.method == "POST":
            user2 = cursor.fetchone()
            user2 = User(mysqldb)
            user2.fetchBy(user2.SELECT("*", f"WHERE login = \"{flask.request.form.get('login')}\" AND password = \"{flask.request.form.get('pass')}\""))
            if user2 is not None:
                user_token = str(uuid.uuid1())
                user2.UPDATE({"token": user_token}, f"WHERE id = {user2.id}")
                mysqldb.commit()
                res = flask.redirect('/')
                res.set_cookie('token', bytes(user_token.encode()), max_age=60*60*24*365*5)
                return res
        user = None
        user_role = None
        userAnalitycs = [0, 0, 0, 0]    
    return flask.render_template('nfc.html', user=user, user_role=user_role, userAnalitycs=userAnalitycs, objects=objects, nfces=nfces)

@app.route('/activate/<id>')
def act(id):
    print(id)
    tmp = NFCAcc(mysqldb).SELECT("*", f"WHERE nfcID = {id}")
    time = strftime("%Y %m %d %H %M %S", gmtime())
    if not tmp:
        Log(mysqldb).INSERT(f"(NULL, \"{time}\", 0)")
        return "Ошибка"
    else:
        Log(mysqldb).INSERT(f"(NULL, \"{time}\", 1)")
        return "Успех"

@app.route('/manage_chop', methods=["GET", "POST"])
@app.route('/manage_chop.html', methods=["GET", "POST"])
def manage_chop():
    mysqldb.reconnect()
    if flask.request.cookies.get('token') is not None:
        user = User(mysqldb)
        user.fetchBy(user.SELECT("*", "WHERE token = \"" + flask.request.cookies.get('token') + "\""))
        user_role = getUserRole(user.id)
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
        userAnalitycs=[taskslen, objectsLen, secs, nfcAccs]
    else:
        if flask.request.method == "POST":
            user2 = cursor.fetchone()
            user2 = User(mysqldb)
            user2.fetchBy(user2.SELECT("*", f"WHERE login = \"{flask.request.form.get('login')}\" AND password = \"{flask.request.form.get('pass')}\""))
            if user2 is not None:
                user_token = str(uuid.uuid1())
                user2.UPDATE({"token": user_token}, f"WHERE id = {user2.id}")
                mysqldb.commit()
                res = flask.redirect('/')
                res.set_cookie('token', bytes(user_token.encode()), max_age=60*60*24*365*5)
                return res
        user = None
        user_role = None
        userAnalitycs = [0, 0, 0, 0]    
    return flask.render_template('manage_chop.html', user=user, user_role=user_role, userAnalitycs=userAnalitycs)


def getUserRole(userID):
    try:
        tmp = RoleAssign(mysqldb)
        roleID = tmp.SELECT("*", f"WHERE userID = {userID}")
        user_role = Role(mysqldb)
        user_role.fetchBy(user_role.SELECT("*", f"WHERE id = {roleID[1]}"))
        return user_role
    except TypeError:
        return None

def GetUserByID(uid):
    return User(mysqldb).SELECT("*", f"WHERE id = {uid}")

def GetObjByID(uid):
    return Object(mysqldb).SELECT("*", f"WHERE id = {uid}")

def GetNFCByObejct(oid):
    return NFCAcc(mysqldb).SELECT("*", f"WHERE orgID = {oid}", True)

def GetSecsByObejct(uid):
    return ObjectSec(mysqldb).SELECT("*", f"WHERE objectID = {uid}", True)

app.jinja_env.globals.update(len=len, User=User, Role=Role, RoleAssign=RoleAssign, NFCAcc=NFCAcc, Task=Task, Object=Object, ObjectSec=ObjectSec, mysqldb=mysqldb, getUserRole=getUserRole, GetUserByID=GetUserByID, GetObjByID=GetObjByID, GetNFCByObejct=GetNFCByObejct, GetSecsByObejct=GetSecsByObejct)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)