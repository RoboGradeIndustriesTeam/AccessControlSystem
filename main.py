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
from functions.UserAnalitycs import UserAnalitycs
import traceback


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
        if user.id == 0:
            res = flask.redirect('/')
            res.set_cookie('token', '', expires=0)
            return res
        user_role = getUserRole(user.id)

        userAnalitycs = UserAnalitycs().fetch(mysqldb, user.id)
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
        if user.id == 0:
            res = flask.redirect('/')
            res.set_cookie('token', '', expires=0)
            return res
        tmp = UserAnalitycs()
        userAnalitycs = tmp.fetch(mysqldb, user.id)
        if flask.request.method == "POST" and flask.request.form.get("form-type") == "addDet":
            name = flask.request.form.get("name")
            date = flask.request.form.get("daterange")
            nfcs = flask.request.form.getlist("states")
            sec = flask.request.form.get("sec")
            objID = flask.request.form.get("obj")
            nfcss = ""
            for i in nfcs:
                nfcss += i + ","
            if Task(mysqldb).SELECT("*", f"WHERE taskName = {name}") == None:
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
        tmp = UserAnalitycs()
    
    return flask.render_template('detours.html', user=user, user_role=user_role, userAnalitycs=userAnalitycs, nfces=tmp.nfcTags, secs=tmp.securityUsers, objects=tmp.objects, tasks=tmp.tasks)

@app.route('/users', methods=["GET", "POST"])
@app.route('/users.html', methods=["GET", "POST"])
def user():
    mysqldb.reconnect()
    if flask.request.cookies.get('token') is not None:
        user = User(mysqldb)
        user.fetchBy(user.SELECT("*", "WHERE token = \"" + flask.request.cookies.get('token') + "\""))
        user_role = getUserRole(user.id)
        if user.id == 0:
            res = flask.redirect('/')
            res.set_cookie('token', '', expires=0)
            return res
        tmp2 = UserAnalitycs()
        users = []
        userAnalitycs = tmp2.fetch(mysqldb, user.id)
        for i in tmp2.securityUsers:
            users.append(User(mysqldb).SELECT("*", f"WHERE id = {i[1]}"))
        if flask.request.method == "POST":
            ftyp = flask.request.form.get("form-type")

            if ftyp == "addUser":
                if (flask.request.form.get("user_name"),) in User(mysqldb).SELECT("login", oneOrAll=True):
                    tmp = User(mysqldb).SELECT('id', f"WHERE login = \"{flask.request.form.get('user_name')}\"")
                    if ObjectSec(mysqldb).SELECT("*", f"WHERE userID = {tmp[0]}") == None:
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

    return flask.render_template('users.html', user=user, user_role=user_role, userAnalitycs=userAnalitycs, users=users, objects=tmp2.objects)

@app.route('/object', methods=["GET", "POST"])
@app.route('/object.html', methods=["GET", "POST"])
def object():
    mysqldb.reconnect()
    if flask.request.cookies.get('token') is not None:
        user = User(mysqldb)
        user.fetchBy(user.SELECT("*", "WHERE token = \"" + flask.request.cookies.get('token') + "\""))
        if user.id == 0:
            res = flask.redirect('/')
            res.set_cookie('token', '', expires=0)
            return res
        user_role = getUserRole(user.id)
        tmp = UserAnalitycs()
        userAnalitycs = tmp.fetch(mysqldb, user.id)
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
    return flask.render_template('object.html', user=user, user_role=user_role, userAnalitycs=userAnalitycs, objects=tmp.objects)

@app.route('/nfc', methods=["GET", "POST"])
@app.route('/nfc.html', methods=["GET", "POST"])
def nfc():
    mysqldb.reconnect()
    if flask.request.cookies.get('token') is not None:
        user = User(mysqldb)
        user.fetchBy(user.SELECT("*", "WHERE token = \"" + flask.request.cookies.get('token') + "\""))
        if user.id == 0:
            res = flask.redirect('/')
            res.set_cookie('token', '', expires=0)
            return res
        user_role = getUserRole(user.id)
        tmp = UserAnalitycs()
        userAnalitycs = tmp.fetch(mysqldb, user.id)
        
        if flask.request.method == "POST" and flask.request.form.get("form-type") == "addNFC":
            if NFCAcc(mysqldb).SELECT("*", f"WHERE data = {flask.request.form.get('data')}") == None:
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
    return flask.render_template('nfc.html', user=user, user_role=user_role, userAnalitycs=userAnalitycs, objects=tmp.objects, nfces=tmp.nfcTags)

@app.route('/activate/<id>')
def act(id):
    mysqldb.reconnect()
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
        if user.id == 0:
            res = flask.redirect('/')
            res.set_cookie('token', '', expires=0)
            return res
        user_role = getUserRole(user.id)
        tmp = UserAnalitycs()
        userAnalitycs = tmp.fetch(mysqldb, user.id)
        if flask.request.method == "POST":
            if Object(mysqldb).SELECT("*", f"WHERE name = \"{flask.request.form.get('name')}\"") == None:
                Object(mysqldb).INSERT(f"(NULL, {user.id}, \"{flask.request.form.get('name')}\", \"{flask.request.form.get('address')}\")")
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
    return flask.render_template('manage_chop.html', user=user, user_role=user_role, userAnalitycs=userAnalitycs, objects=tmp.objects)


def getUserRole(userID):
    mysqldb.reconnect()
    try:
        tmp = RoleAssign(mysqldb)
        roleID = tmp.SELECT("*", f"WHERE userID = {userID}")
        print(roleID)
        user_role = Role(mysqldb)
        user_role.fetchBy(user_role.SELECT("*", f"WHERE id = {roleID[1]}"))
        return user_role
    except TypeError:
        print(traceback.format_exc())
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