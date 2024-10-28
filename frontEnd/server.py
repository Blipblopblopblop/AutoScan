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

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

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
    
@app.route('/get_latest_reports', methods=['GET'])
def get_latest_reports():
    try:
        with Gmp(connection=connection, transform=transform) as gmp:
            gmp.authenticate(username, password)
            report_ids = []
            
            # Get tasks
            resp = gmp.get_tasks()
     
            for task in resp.findall('task'):
                last = task.find('last_report')
                if last is not None:
                    report = last.find('report')
                    if report is not None:
                        report_id = report.get('id')
                        report_data = get_CVES_latest_report(report_id, gmp)
                        report_ids.append(report_data)
            
            return jsonify(report_ids)
    except GvmError as e:
        print('An error occurred:', e, file=sys.stderr)
        return jsonify({"error": str(e)}), 500


def get_CVES_latest_report(report_id, gmp):
    if not report_id:
        return {"error": "No report ID provided"}

    XML = 'a994b278-1f62-11e1-96ac-406186ea4fc5'
    report = gmp.get_report(report_id, report_format_id=XML, filter_string="apply_overrides=0 levels=hml rows=100 min_qod=70 first=1 sort-reverse=severity")
    
    cve_results = []
    for result in report.findall('.//result'):
        cve_ref = result.find('.//ref[@type="cve"]')
        cve_id = cve_ref.attrib['id'] if cve_ref is not None else None
        severities = result.find('.//severities')
        severity_value = severities.attrib['score'] if severities is not None else None
        
        if severity_value is not None and float(severity_value) > 0 and cve_id is not None:
            description = result.find('.//description')
            description_value = description.text.strip() if description is not None else 'No description available.'
            cve_results.append({
                'CVE ID': cve_id,
                'Severity': severity_value,
                'Description': description_value
            })
    
    return {
        'Report ID': report_id,
        'CVEs': cve_results
    }

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
