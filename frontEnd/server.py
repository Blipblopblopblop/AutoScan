from flask import Flask, render_template, jsonify, request
from Api_basic import get_existing_tasks,connect_to_gmp,schedule_scan
import json
import os
import sys
from gvm.connections import TLSConnection
from gvm.protocols.latest import Gmp
from gvm.errors import GvmError
from gvm.transforms import EtreeCheckCommandTransform


app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/scan', methods=['GET', 'POST'])
def deploy():
    return render_template('scan.html')

@app.route('/groups', methods=['GET', 'POST'])
def schedule():
    return render_template('groups.html')

@app.route('/reports', methods=['GET', 'POST'])
def reports():
    return render_template('reports.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template('settings.html')


def load_tasks():
    with open('static/tasks.json', 'r') as file:
        tasks = json.load(file)
    return tasks


def save_tasks(tasks):
    with open('static/tasks.json', 'w') as file:
        json.dump(tasks, file, indent=4)

# Greenbone connection setup
connection = TLSConnection(hostname='100.74.219.96', port=9390)
transform = EtreeCheckCommandTransform()

username = 'Team'
password = ''

# retrieve port lists
@app.route('/add_task', methods=['POST'])
def add_task():
    try:
        task_data = request.get_json()

        task_name = task_data['name']
        scan_config = task_data['scanConfig']
        target_host = task_data['targetHost']
        date = task_data.get('date', None)
        time = task_data.get('time', None)

        result = schedule_scan(task_name, scan_config, target_host, date, time)

        return jsonify(result)

    except Exception as e:
        print(f"Error while scheduling scan: {e}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500
    
#function to get tasks from Greenbone
@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = get_existing_tasks()  
        if tasks is None:
            return jsonify({"error": "Failed to get tasks"}), 500
        return jsonify(tasks)
    except Exception as e:
        print(f"Error retrieving tasks: {e}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500

@app.route('/remove_task/<task_id>', methods=['DELETE'])
def remove_task(task_id):
    try:
        data = request.get_json()
        target_id = data.get('targetId')
        schedule_id = data.get('scheduleId')

        gmp = connect_to_gmp()
        if not gmp:
            return jsonify({"status": "Failed", "error": "Authentication failed"}), 500

        task_response = gmp.delete_task(task_id)
        print(f"Deleted task with ID: {task_id}")

        if target_id:
            target_response = gmp.delete_target(target_id)
            print(f"Deleted target with ID: {target_id}")

        if schedule_id:
            schedule_response = gmp.delete_schedule(schedule_id)
            print(f"Deleted schedule with ID: {schedule_id}")

        return jsonify({"status": "Success", "message": "Task, target, and schedule deleted successfully"})

    except Exception as e:
        print(f"Error while deleting task: {e}", file=sys.stderr)
        return jsonify({"status": "Failed", "error": str(e)}), 500



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
