from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from flask import request
from flask import jsonify

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
# from flask_api import status

from string import ascii_lowercase
import random
import json


### Config ###
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

### how to ###
# db.create_all
# db.session.add(object)
# db.session.commit()
# tasker = Project.query.filter_by(name='Tasker').first()
#
# python manage.py db init
# python manage.py db migrate
# python manage.py db upgrade

# Generate random URL part
def slugify(size):
    return ''.join(random.choice(ascii_lowercase) for i in range(size))


### Models ###
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    slug = db.Column(db.String(32), unique=True)
    tasks = db.relationship('Task', backref='project')

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        self.slug = slugify(8)

    def __repr__(self):
        return f'<Project: {self.name}>'


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text(140))
    slug = db.Column(db.String(8), unique=True)
    priority = db.Column(db.Integer)
    solved = db.Column(db.Boolean)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        self.solved = False
        self.slug = slugify(4)

    def __repr__(self):
        return f'<Task: {self.text}, priority: {self.priority}, solved: {self.solved}>'


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


### Routing ###
# JSON API
@app.route('/api2', methods=['POST', 'GET'])
def api_json():
    if (request.is_json):
        json_request = request.get_json()
        json_response = {"server_status": 201}
        write_json(json_request, './examples/last_request.json')
        # Validate FPI key
        if json_request["api_key"] != "super_secret_key":
            json_response.update({"error": "invalid API key"})
            return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'ContentType':'application/json'}


        if json_request["request"] == "get_tasks":
            write_json(json_request, './examples/tasks_list_request.json')
            slug = json_request["project"]["slug"]
            try:
                project = Project.query.filter(Project.slug==slug).first()
            except:
                json_response.update({"error": "error reading database"})
                return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'ContentType':'application/json'}
            task_list = {}
            task_counter = 0
            for task in project.tasks:
                i = {"task": task.text, "slug": task.slug, "solved": task.solved}
                task_list.update({task_counter: i})
                task_counter = task_counter + 1
            json_response.update({"tasks_list": task_list})
            write_json(json_response, './examples/tasks_list_response.json')
            return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'ContentType':'application/json'}


        json_response = {
            "status": 200,
            "is_json": request.is_json,
            "test": "test",}
        return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'ContentType':'application/json'}
    else:
        return('<h1> Not Json </h1>'), 200, {'ContentType':'text/html'}


# Web presentation
@app.route('/<slug>')
def tasks_list(slug):
    project = Project.query.filter(Project.slug==slug).first_or_404()
    return render_template('tasks.html', tasks=project.tasks)


@app.route('/')
def index():
    projects = Project.query.all()
    return render_template('projects.html', projects=projects), 200


### Main ###
if __name__ == '__main__':
    app.run(debug=True)
