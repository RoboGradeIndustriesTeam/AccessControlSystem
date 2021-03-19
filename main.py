import flask
from mysql.connector import connect
import os
import dotenv
from flask_cors import CORS
import uuid

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
app = flask.Flask("AccesControlSystem", static_folder='', template_folder='frontend')
CORS(app)

@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
@app.route('/indez.html', methods=["GET", "POST"])
def index():
    if not flask.request.cookies.get('token'):
        return flask.redirect('login.html')
    cursor.execute("SELECT * FROM users WHERE token", (flask.request.cookies.get('token')))
    user = cursor.fetchone()
    if not user:
        return flask.redirect('login.html')
    return flask.render_template('index.html', user=user)
@app.route('/login', methods=["GET", "POST"])
@app.route('/login.html', methods=["GET", "POST"])
def login():
    mysqldb.reconnect()
    if flask.request.method == "POST":
        cursor.execute("SELECT * FROM users WHERE login = %s AND password = %s", (flask.request.form.get('login'), flask.request.form.get('pass')))
        user = cursor.fetchone()
        if not user:
            user_token = uuid.uuid1()
            cursor.execute("UPDATE users SET token = %s WHERE id = %s", (user_token.hex, user[0]))
            mysqldb.commit()
            res = flask.redirect('/')
            res.set_cookie('token', bytes(user_token.hex.encode()), max_age=60*60*24*365*5)
            return res
    return flask.render_template("login.html")




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8074, debug=True)