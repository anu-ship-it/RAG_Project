🌐 RealRAGSystem

A real Retrieval-Augmented Generation (RAG) system that can answer any question by combining web search + LLM reasoning.

🚀 Overview

RealRAGSystem is a Python-based implementation of a true RAG pipeline — it performs live web retrieval (via DuckDuckGo or Wikipedia) and then uses an LLM (either OpenAI GPT or local Ollama) to generate grounded, context-aware answers.

Unlike static RAG demos that rely on fixed datasets, this one searches the live web in real time and constructs a contextualized prompt for the LLM. That means it can answer any question you throw at it — from breaking news to scientific concepts.

✨ Features

🔍 Real Web Search — Queries DuckDuckGo’s public API for fresh, context-rich results.

🧠 Retrieval-Augmented Generation — Merges search results into a dynamic context for LLM reasoning.

🤖 LLM Options — Choose between:

Local Ollama
 (for free, offline generation)

Cloud-based OpenAI GPT-3.5 (for higher-quality responses)

📚 Automatic Source Attribution — Displays the top sources used in each answer.

🛡️ No API keys needed for search — DuckDuckGo API is public and keyless.

💬 Interactive CLI mode — Ask unlimited questions in a conversational shell.

🧩 Project Structure
📦 RealRAGSystem
│
├── real_rag.py           # Main implementation
├── requirements.txt       # Python dependencies (requests, etc.)
└── README.md              # This file

⚙️ Setup
1. Clone the repository
git clone [https://github.com/<your-username>/RealRAGSystem.git](https://github.com/anu-ship-it/RAG_Project)
cd RealRAGSystem

2. Install dependencies
pip install -r requirements.txt


Or manually:

pip install requests

3. Choose your LLM backend

You have two options:

Option A: Use Ollama (recommended, local & free)

Install Ollama
.

Pull a model (e.g. Llama 2):

ollama pull llama2


Start the Ollama server:

ollama serve

Option B: Use OpenAI GPT

Set your API key:

export OPENAI_API_KEY="your-openai-api-key"


Initialize with use_ollama=False in code.

🧠 Usage
Run interactively
python real_rag.py


You’ll see an interactive console like:

🌐 REAL RAG SYSTEM - Ask ANY Question!

✨ This system can answer questions about ANYTHING by:
   1. Searching the web for relevant information
   2. Using AI to generate accurate answers

💬 Start asking questions! (type 'quit' to exit)

Example interaction
Your question: What is quantum computing?

🔍 Step 1: Searching the web for information...
✅ Found 5 relevant sources

🤖 Step 2: Generating answer using LLM...
📝 ANSWER:
Quantum computing is a field of computation that uses quantum bits (qubits)...
📚 SOURCES:
1. Quantum computing - Wikipedia
   🔗 https://en.wikipedia.org/wiki/Quantum_computing

🧰 Code Overview
Class: RealRAGSystem

Handles the full RAG pipeline:

search_web(query) → performs DuckDuckGo & Wikipedia lookup

call_ollama(prompt) → uses local Ollama API

call_openai(prompt) → uses OpenAI GPT API

answer_question(question) → coordinates retrieval + generation

Function: main()

Launches an interactive command-line interface that lets users query live data and receive AI-composed answers.

⚡ Example Code Snippet
from real_rag import RealRAGSystem

rag = RealRAGSystem(use_ollama=True)
result = rag.answer_question("Explain blockchain technology")

print("Answer:", result['answer'])
for i, src in enumerate(result['sources']):
    print(f"{i+1}. {src['title']} ({src['link']})")

🧩 Dependencies
Library	Purpose
requests	For web and API requests
json	Parsing web API responses
typing	Type hints for clarity
time	Optional delay or logging
🔒 Notes

DuckDuckGo Instant Answer API requires no keys.

Ollama must be running locally (localhost:11434).

For OpenAI mode, make sure your API key is valid and rate limits allow usage.

🧭 Roadmap

 Add vector-based local document RAG (e.g., FAISS + PDFs)

 Add caching for repeated queries

 Add support for Claude / Gemini APIs

 Web dashboard version (Next.js frontend)

🧑‍💻 Author

Alpha — Senior Software Developer
Building AI-driven systems that merge retrieval, reasoning, and real-world intelligence.

📝 License

This project is licensed under the MIT License — free to use, modify, and distribute.
