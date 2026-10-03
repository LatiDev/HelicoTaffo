import ollama, dataclasses, json, subprocess, time

class Model:
    def __init__(self, ip, name, thread = 1):
        self.model: str = name
        self.cmodel: str= f"{name}-{thread}t"

        self.process = subprocess.Popen(
            ["ollama", "serve"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL, 
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        ollama.create(
            model=self.cmodel, 
            from_=self.model, 
            parameters={"num_thread": thread}
        )
        
        self.process.terminate()

        self.client = ollama.Client(host=f"http://{ip}:11434")

    def ask(self, prompt: str):            
        response: ollama.ChatResponse = self.client.chat(model=self.cmodel, messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content'].strip()