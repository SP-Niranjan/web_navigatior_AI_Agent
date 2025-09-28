WebNavigatorAgent – Hackathon Project:
An AI-powered autonomous web navigation agent built during the ByteXL Hackathon.
This project demonstrates how LLMs, memory, and browser automation can work together to explore and interact with the web intelligently.

Features:
LLM-powered reasoning – Uses a language model to decide actions.
Browser automation – Automatically opens sites, searches, and interacts with elements.
Memory system – Stores visited pages, actions, and results.
Modular agent design – Each component (LLM, Tools, Memory) can be extended independently.

Tech Stack:
Python 3.12+
Selenium / BrowserTools (for web automation)
Ollama (for the web automation search and analyse the informations)
Custom Agent Core (coordinates LLM + browser + memory)

Project Structure:
HACHATHON FOR BYTEXL/
│── agent/
│   ├── Advacanced_Agent.py
│   ├── Agent_core.py
│   └── __pycache__/
│
│── LLM/
│   ├── llm_handler.py
│   └── __pycache__/
│
│── Memory/
│   ├── Memory.py
│   └── __pycache__/
│
│── Tools/
│   ├── Browser_Tools.py
│   └── __pycache__/
│
│── main.py
│── requirements_db.txt
│── Runnable.py
│── Runnable2.py
│── __pycache__/


Getting Started:
(Befor getting started install Ollama and then Download the Llama3 model)
1️. Clone the repository
git clone https://github.com/SP-Niranjan/web_navigatior_AI_Agent

cd the folder ex: cd web_navigator_AI_Agent

2️. Install dependencies:
pip install -r requirements.txt

3️. Run the project:
python Runnable2.py

Example Use Case:
Search for "Show me Shoe within 500-10000"

 The agent will search the browser backend, search automatically, and store actions in memory, extract the information and ollama will analyse the informations then give the best suiting output.
