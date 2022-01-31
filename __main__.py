import os
import yaml
import threading

from taskeduler.task import TaskManager
from taskeduler.parser import TaskParser
from pvpc_bot.bot.bot import ReeBot
from pvpc_bot.config import TASKS_FILE, TASKS_PATH


def set_task_path():
    with open(TASKS_FILE, "rt") as f:
        tasks_dct = yaml.safe_load(f.read())
        for task in tasks_dct:
            current_path = tasks_dct[task]["script"]["file"]
            tasks_dct[task]["script"]["file"] = os.path.join(TASKS_PATH, os.path.basename(current_path))
    
    with open(TASKS_FILE, "wt") as f:
        f.write(yaml.safe_dump(tasks_dct))

if __name__ == "__main__":
    # Create the task manager loop
    set_task_path()
    task_parser = TaskParser(TASKS_FILE)
    task_manager = TaskManager()
    for task_name, task in task_parser.tasks.items():
        task_manager.add_task(task_name, task)
    
    task_thread = threading.Thread(target=task_manager.loop.start)
    task_thread.start()

    # Create the bot loop
    ree_bot = ReeBot()
    ree_bot.infinity_polling()

