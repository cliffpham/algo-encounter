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

# api = leetcode.LeetcodeAPI()

class User(flask_db.Model):
    username = CharField()
    password = CharField()

    class Meta:
        database = database

class Question(flask_db.Model):
    leetcode_id = TextField()
    submission = TextField()
    status = BooleanField()

    class Meta:
        database = database

@app.route('/')
def welcome():
    api = leetcode.LeetcodeAPI()
    questions = api.all_problems()
    
    return render_template('index.html', questions = questions)

@app.route('/username', methods=['GET', 'POST'])
def get_user():
    if request.method == 'POST':
        if request.form.get('username') and request.form.get('pw'):
            result = request.form.get('username')
            pw = request.form.get('pw')
            print(result)
            print(pw)
            user = User.create(username=result, password=pw)
            
            # output = subprocess.check_call(["leetcode", "user", "-l"])
            # print(output)
            
    return render_template('login.html')

@app.route('/list', methods = ['POST', 'GET'])
def get_list():
    if request.method == 'POST':
        result = request.form.get('difficulty')
    
    api = leetcode.LeetcodeAPI()
    output = api.list_problems(result)

    return render_template('list.html', output = output)

@app.route('/submit/<problemid>', methods = ['POST', 'GET'])
def post_question(problemid):
    print "SUBMITTING SOLUTION"
    api = leetcode.LeetcodeAPI()
    code = request.form.get('code')
    # q = Question.create(submission=code)
    return jsonify({
        "result" : api.submit_solution(problemid, "py", code)
    })

@app.route('/question', methods = ['POST'])
def question():

    result = request.form.get('id')
    
    return redirect(url_for('list'))


@app.route('/question/<problemid>', methods = ['GET'])
def get_question(problemid):

    output = subprocess.check_output(["leetcode", "show", problemid]).decode("utf-8")
    output = output.splitlines()

    api = leetcode.LeetcodeAPI()
    code = api.get_file(problemid)

    # if user has submitted a solution to the question before, retrieve most recent submission
    query = Question.select().where(Question.leetcode_id == problemid)
    if query.exists():
        code = Question.select().where(Question.leetcode_id == problemid)
        code = code[1].submission

    return render_template('submit.html', output = output, code=code, problemid=problemid)

@app.errorhandler(404)
def not_found(exc):
    return Response('<h3>Not found</h3>'), 404

def main():
    database.drop_tables([User, Question])
    database.create_tables([User, Question])
    app.run(debug=True)

if __name__ == '__main__':
    main()