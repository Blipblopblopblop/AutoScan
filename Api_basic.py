import sys
import pytz
from datetime import datetime
from icalendar import Calendar, Event
from gvm.connections import TLSConnection
from gvm.protocols.latest import Gmp
from gvm.transforms import EtreeCheckCommandTransform
from gvm.errors import GvmError


# Global connection setup
connection = TLSConnection(hostname='100.74.219.96', port=9390)
transform = EtreeCheckCommandTransform()
username = 'Team'
password = 'UsK]+m1KXNAyTT?fpWjS'

def connect_to_gmp():
    try:
        gmp = Gmp(connection=connection, transform=transform)
        gmp.authenticate(username, password)
        print("Authenticated successfully")
        return gmp
    except GvmError as e:
        print(f"Error during authentication: {e}", file=sys.stderr)
        return None

#retrive port lists 
def get_port_lists(gmp):
    try:
       
        port_lists = gmp.get_port_lists()
        targets_response = gmp.get_targets()

        for target in targets_response.xpath('target'):
            target_name = target.find('name').text
            target_id = target.get('id')
            print(f"Target Name: {target_name}, Target ID: {target_id}")

        # Print available port lists and return the UUID 
        port_list_uuid = None
        for port_list in port_lists.xpath('port_list'):
            name = port_list.find('name').text
            uuid = port_list.get('id')
            print(f"Port List Name: {name}, UUID: {uuid}")

            if name == 'All IANA assigned TCP':
                port_list_uuid = uuid

        if port_list_uuid:
            print(f"UUID for 'All IANA assigned TCP': {port_list_uuid}")
        else:
            print("Port list 'All IANA assigned TCP' not found.")

        return port_list_uuid
    except GvmError as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return None

scan_config ='daba56c8-73ec-11df-a475-002264764cea'

# create schedule
def schedule_scan(task_name, scan_config, target_host, date=None, time=None):
    try:
        gmp = connect_to_gmp()  
        if not gmp:
            return {"status": "Failed", "error": "Authentication failed"}

        port_list_id = get_port_lists(gmp)
        if not port_list_id:
            return {"status": "Failed", "error": "Port list not found"}

        target_id = None
        targets = gmp.get_targets()
        for target in targets.xpath('target'):
            if target.find('name').text == task_name:
                target_id = target.get('id')
                print(f"Target '{task_name}' already exists with ID: {target_id}")
                break

        if not target_id:
            
            target_response = gmp.create_target(
                name=task_name,
                hosts=[target_host],
                port_list_id=port_list_id
            )
            target_id = target_response.get("id")
            print(f"Created new target '{task_name}' with ID: {target_id}")

        
        scanner_id = '08b69003-5fc2-4037-a479-93b440211c73'
        

        schedule_id = None
        if date and time:
            
            cal = Calendar()
            cal.add('prodid', '-//My Product//')
            cal.add('version', '2.0')

            event = Event()
            event.add('dtstamp', datetime.now(tz=pytz.UTC))
            start_datetime = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M')
            event.add('dtstart', start_datetime.replace(tzinfo=pytz.UTC))

            cal.add_component(event)

            schedule_response = gmp.create_schedule(
                name=f"Schedule for {task_name}",
                icalendar=cal.to_ical(),
                timezone='UTC'
            )
            schedule_id = schedule_response.get("id")
            print(f"Schedule created with ID: {schedule_id}")

        task_response = gmp.create_task(
            name=task_name,
            config_id='daba56c8-73ec-11df-a475-002264764cea',
            target_id=target_id,
            scanner_id=scanner_id,
            schedule_id=schedule_id
        )
        task_id = task_response.get("id")
        print(f"Task '{task_name}' created with ID: {task_id}")

        return {"status": "Success", "task_id": task_id}

    except GvmError as e:
        print(f"An error occurred while scheduling the scan: {e}", file=sys.stderr)
        return {"status": "Failed", "error": str(e)}

    except ValueError as e:
        print(f"Connection error: {e}", file=sys.stderr)
        return {"status": "Failed", "error": "Connection error occurred"}

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return {"status": "Failed", "error": str(e)}

# retrieve the port lists
gmp = connect_to_gmp()
if gmp:
    get_port_lists(gmp)

def get_existing_tasks():
    try:
        gmp = connect_to_gmp()
        if not gmp:
            return None

        tasks_response = gmp.get_tasks()
        tasks = []

        for task in tasks_response.xpath('task'):
            task_info = {
                'id': task.get('id'),  # Include task ID
                'name': task.find('name').text,
                'status': task.find('status').text,
                'progress': task.find('progress').text if task.find('progress') is not None else '0',
                'date': task.find('creation_time').text,
                'target_id': task.find('target').get('id'),  # Ensure target ID is fetched
                'schedule_id': task.find('schedule').get('id') if task.find('schedule') is not None else None  # Ensure schedule ID is fetched if exists
            }
            tasks.append(task_info)

        return tasks

    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return None

    

def delete_task(task_id):
    try:
        gmp = connect_to_gmp()
        if not gmp:
            return {"status": "Failed", "error": "Authentication failed"}

        # Use Greenbone's API to delete the task by its ID
        gmp.delete_task(task_id)
        print(f"Task with ID {task_id} deleted successfully.")
        return {"status": "Success", "message": f"Task {task_id} deleted successfully."}
    except GvmError as e:
        print(f"Error deleting task {task_id}: {e}", file=sys.stderr)
        return {"status": "Failed", "error": str(e)}
