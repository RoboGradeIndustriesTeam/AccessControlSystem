import flask
from mysql.connector import connect
import os
import dotenv
from flask_cors import CORS

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

@app.route('/login', methods=["GET", "POST"])
@app.route('/login.html', methods=["GET", "POST"])
def index():
    pass

@app.route('/login', methods=["GET", "POST"])
@app.route('/login.html', methods=["GET", "POST"])
def login():
    mysqldb.reconnect()
    if flask.request.method == "POST":
        cursor.execute("SELECT * FROM users WHERE login = %s AND password = %s", (flask.request.form.get('login'), flask.request.form.get('pass')))
        user = cursor.fetchone()
        print(user)
    return flask.render_template("login.html")




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8074, debug=True)