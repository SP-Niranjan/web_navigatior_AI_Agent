import ollama

class LLMHandler:
    def __init__(self, model="qwen2.5:0.5b"):
        self.model = model
        
    def generate_response(self, messages):
        response = ollama.chat(
            model=self.model,
            messages=messages
        )
        return response['message']['content']
        
    def parse_task(self, user_input):
        messages = [
            {"role": "system", "content": "You are a web automation assistant. Break down user requests into browser actions. Return JSON format with actions: navigate_to, click_element, type_text, extract_text"},
            {"role": "user", "content": f"Parse this task: {user_input}"}
        ]
        return self.generate_response(messages)
