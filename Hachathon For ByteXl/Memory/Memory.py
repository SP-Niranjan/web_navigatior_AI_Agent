import time
import json

class AgentMemory:
    def __init__(self):
        self.task_history = []
        self.context = {}
        
    def add_task(self, task, result):
        self.task_history.append({
            "task": task,
            "result": result,
            "timestamp": time.time(),
            "status": result.get("status", "unknown")
        })
        
    def get_recent_tasks(self, count=5):
        return self.task_history[-count:]
        
    def clear_history(self):
        self.task_history = []
