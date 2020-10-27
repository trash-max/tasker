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
    tasks = db.relationship('Task', backref='project', order_by="Task.priority")

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
    app.logger.info(str(data))


### Routing ###
# JSON API
@app.route('/api2', methods=['POST', 'GET'])
def api_json():
    if (request.is_json):
        json_request = request.get_json()
        json_response = {"server_status": 201,
                        "job_status": "done",
                        "description": "job done"}
        write_json(json_request, './examples/last_request.json')
        app.logger.info("write last_request.json")

        # Validate API key
        if json_request["api_key"] != "super_secret_key":
            json_response.update({"job_status": "error",
                                "description": "Invalid API key"})
            return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type':'application/json'}

        # Tasks list
        if json_request["request"] == "get_tasks":
            write_json(json_request, './examples/tasks_list_request.json')
            app.logger.info("write tasks_list_request.json")

            try:
                project = Project.query.filter(Project.slug==json_request["project"]["slug"]).first_or_404()
            except:
                json_response.update({"job_status": "error",
                                    "description": "Can`t read database or find project by slug"})
                return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type':'application/json'}

            task_list = {}
            task_counter = 0
            for task in project.tasks:
                i = {"task": task.text, "priority": task.priority, "slug": task.slug, "solved": task.solved}
                task_list.update({task_counter: i})
                task_counter = task_counter + 1
            json_response.update({"project": {"name": project.name, "slug": project.slug, "total_tasks": task_counter}})
            json_response.update({"tasks_list": task_list})
            write_json(json_response, './examples/tasks_list_response.json')
            app.logger.info("write tasks_list_response.json")
            return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type':'application/json'}

        # Projects list
        if json_request["request"] == "get_projects":
            write_json(json_request, './examples/project_list_request.json')
            try:
                projects = Project.query.all()
            except:
                json_response.update({"job_status": "error",
                                    "description": "Can`t read database"})
                return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type':'application/json'}
            project_list = {}
            project_counter = 0
            for project in projects:
                i = {"name": project.name, "slug": project.slug}
                project_list.update({project_counter: i})
                project_counter = project_counter + 1
            json_response.update({"project_list": project_list})
            write_json(json_response, './examples/project_list_response.json')
            return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type':'application/json'}

        # New tasks adding
        if json_request["request"] == "add_new_task":
            write_json(json_request, './examples/new_task_request.json')

            if json_request["task"]["text"] == "":
                json_response.update({"job_status": "error",
                                    "description": "task text can`t be empty"})
                return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type':'application/json'}
            if not json_request["task"]["priority"].isdigit():
                json_response.update({"job_status": "error",
                                    "description": "task priority must be digit from 1 to 10"})
                return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type':'application/json'}
            if not json_request["task"]["priority"] in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                json_response.update({"job_status": "error",
                                    "description": "task priority must be from 1 to 10"})
                return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type':'application/json'}

            try:
                project = Project.query.filter(Project.slug==json_request["task"]["project_slug"]).first_or_404()
            except:
                json_response.update({"job_status": "error",
                                    "description": "Can`t read database or find project by slug"})
                return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type':'application/json'}

            new_task = Task(text=json_request["task"]["text"], priority=json_request["task"]["priority"], project=project)
            try:
                db.session.add(new_task)
                db.session.commit()
            except:
                json_response.update({"job_status": "error",
                                    "description": "Can`t write database (can`t add new task in database)"})
                return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type':'application/json'}
            json_response.update({"description": "new task added"})
            write_json(json_response, './examples/new_task_response.json')
            return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type':'application/json'}

        # Switch solved status of tasks
        if json_request["request"] == "solved_switch":
            write_json(json_request, './examples/switch_solved_status_request.json')

            try:
                task = Task.query.filter(Task.slug==json_request["task"]["slug"]).first_or_404()
            except:
                json_response.update({"job_status": "error",
                                    "description": "Can`t read database or find task by slug"})
                return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type':'application/json'}

            if task.solved:
                task.solved = False
            else:
                task.solved = True

            try:
                db.session.commit()
            except:
                json_response.update({"job_status": "error",
                                    "description": "Can`t write database (can`t change solved status)"})
                return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type':'application/json'}

            json_response.update({"description": "task solved status is changed"})
            write_json(json_response, './examples/switch_solved_status_response.json')
            return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type':'application/json'}



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
    return render_template('tasks.html', tasks=project.tasks, header=project.name), 200


@app.route('/')
def index():
    projects = Project.query.all()
    return render_template('projects.html', projects=projects), 200


### Main ###
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
