import datetime
import os
from flask import (Flask, Response, render_template, request, redirect, jsonify, url_for)
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache
from peewee import *
from playhouse.flask_utils import FlaskDB, get_object_or_404, object_list
from playhouse.sqlite_ext import *
import subprocess
import leetcode

# configure our database
APP_DIR = os.path.dirname(os.path.realpath(__file__))
DATABASE = 'sqliteext:///%s' % os.path.join(APP_DIR, 'practice.db')
DEBUG = False
SECRET_KEY = 'dev'
SITE_WIDTH = 800

app = Flask(__name__)
app.config.from_object(__name__)

# instantiate the db wrapper
flask_db = FlaskDB(app)
database = flask_db.database

oembed_providers = bootstrap_basic(OEmbedCache())

api = leetcode.LeetcodeAPI()

class User(flask_db.Model):
    username = CharField()
    password = 'default'

    class Meta:
        database = database

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/username', methods=['GET', 'POST'])
def get_user():
    if request.method == 'POST':
        if request.form.get('username') and request.form.get('pw'):
            result = request.form.get('username')
            pw = request.form.get('pw')
            print(result)
            print(pw)
            
            output = subprocess.check_call(["leetcode", "user", "-l"])
            print(output)
            
    return render_template('login.html')

@app.route('/list', methods = ['POST', 'GET'])
def get_list():
    if request.method == 'POST':
        result = request.form.get('difficulty')
    
    output = api.list_problems(result)

    return render_template('list.html', output = output)

@app.route('/submit/<problemid>', methods = ['POST', 'GET'])
def post_question(problemid):
    print "SUBMITTING SOLUTION"
    api = leetcode.LeetcodeAPI()
    code = request.form.get('code')
    return jsonify({
        "result" : api.submit_solution(problemid, "py", code)
    })

@app.route('/question', methods = ['GET'])
def question():

    result = request.form.get('id')
    
    return redirect(url_for('localhost:5000/question/' + result))


@app.route('/question/<problemid>', methods = ['GET'])
def get_question(problemid):

    output = subprocess.check_output(["leetcode", "show", problemid]).decode("utf-8")
    output = output.splitlines()

    api = leetcode.LeetcodeAPI()
    code = api.get_file(problemid)

    return render_template('submit.html', output = output, code=code, problemid=problemid)

@app.errorhandler(404)
def not_found(exc):
    return Response('<h3>Not found</h3>'), 404

def main():
    database.drop_tables([User])
    database.create_tables([User])
    app.run(debug=True)

if __name__ == '__main__':
    main()