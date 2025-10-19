from datetime import datetime
from pathlib import Path
import logging
import json

logger = logging.getLogger(__name__)
TASK_FILE = Path('appData/tasks.json')

class TaskHandler():
    # Timestamp for tasks
    def create_timestamp(self) -> str:
        now = datetime.now()
        timestamp = now.strftime('%d/%m/%y %H:%M:%S')

        return timestamp

    # Just append to task file
    def add_task(self, task_name, task_desc):
        with open(TASK_FILE, 'r') as f:
            data = json.load(f)

            last_id = max((record["id"] for record in data), default=0)
            new_task_id = last_id + 1

            new_task = {
                'id': new_task_id, 
                'title': task_name,
                'description': task_desc,
                'timestamp': self.create_timestamp(self)
            }

            data.append(new_task)
        
        with open(TASK_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f'Added task nr: {new_task_id} with name: "{task_name}" ')

    # Read tasks -> find specified one & remove it -> rewrite task file
    def remove_task(self, task_id):
        with open(TASK_FILE, 'r') as f:
            data = json.load(f)

            # Crazy one-liner to rewrite file data but without the specified task
            data = [task for task in data if task['id'] != task_id]
        
        with open(TASK_FILE, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
