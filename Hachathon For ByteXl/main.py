from agent import Agent_core
from LLM import llm_handler
from Tools import Browser_Tools
from Memory import Memory
import time
import json


class WebNavigatorAgent:
    def __init__(self):
        # Core components
        self.llm = llm_handler.LLMHandler()
        self.browser = Browser_Tools.BrowserTools()
        self.agent = Agent_core.WebAgent(self.llm, self.browser)
        self.memory = Memory.AgentMemory()  # in-memory history only
        
    def process_request(self, user_input):
        """Process request using the internal agent and store basic history (no DB)."""
        try:
            start_time = time.time()
            
            # Execute task (Agent_core handles classification and steps)
            result = self.agent.execute_task(user_input)
            
            # Add timing info
            result["execution_time"] = time.time() - start_time
            
            # Save in simple memory history
            self.memory.add_task(user_input, result)
            return result

        except Exception as e:
            error_result = {"status": "error", "message": str(e)}
            self.memory.add_task(user_input, error_result)
            return error_result

    def get_task_history(self, count=5):
        """Return recent tasks from in-memory history."""
        return self.memory.get_recent_tasks(count)


# Standalone test
if __name__ == "__main__":
    agent = WebNavigatorAgent()
    test_task = "Search for best laptops under $1000"
    print(f"Testing: {test_task}")
    result = agent.process_request(test_task)
    print(f"Result: {json.dumps(result, indent=2)}")
