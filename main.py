import flask
from apievents.login import Login

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
        return flask.jsonify(APIDict[reqjson["name"]].onRequest(reqjson['data']))
    except KeyError:
        return flask.jsonify({"error": 0})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8074, debug=True)