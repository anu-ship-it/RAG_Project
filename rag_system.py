import requests
import json
from typing import List, Dict
import time

class RealRAGSystem:
    """
    A real RAG system that can answer ANY question by:
    1. Searching the web for relevant information
    2. Using LLM to generate answers from that information
    """
    
    def __init__(self, use_ollama: bool = True, openai_key: str = None):
        """
        Initialize Real RAG System.
        
        Args:
            use_ollama: If True, use local Ollama. If False, use OpenAI
            openai_key: OpenAI API key (only needed if use_ollama=False)
        """
        self.use_ollama = use_ollama
        self.openai_key = openai_key
        
    def search_web(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search the web using DuckDuckGo (no API key needed).
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results with title, snippet, and link
        """
        try:
            # Using DuckDuckGo Instant Answer API (free, no API key)
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            results = []
            
            # Get abstract (main answer)
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'Main Result'),
                    'snippet': data.get('Abstract'),
                    'link': data.get('AbstractURL', '')
                })
            
            # Get related topics
            for topic in data.get('RelatedTopics', [])[:num_results]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append({
                        'title': topic.get('Text', '')[:100],
                        'snippet': topic.get('Text', ''),
                        'link': topic.get('FirstURL', '')
                    })
            
            # If no results, try Wikipedia search as backup
            if not results:
                wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
                try:
                    wiki_response = requests.get(wiki_url, timeout=5)
                    if wiki_response.status_code == 200:
                        wiki_data = wiki_response.json()
                        results.append({
                            'title': wiki_data.get('title', ''),
                            'snippet': wiki_data.get('extract', ''),
                            'link': wiki_data.get('content_urls', {}).get('desktop', {}).get('page', '')
                        })
                except:
                    pass
            
            return results
            
        except Exception as e:
            print(f"⚠️ Search error: {str(e)}")
            return []
    
    def call_ollama(self, prompt: str, model: str = "llama2") -> str:
        """Call local Ollama API."""
        try:
            url = "http://localhost:11434/api/generate"
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500
                }
            }
            
            print("🤖 Generating answer with Ollama...")
            response = requests.post(url, json=data, timeout=120)
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                return f"❌ Error calling Ollama (Status {response.status_code}). Is Ollama running? Try: ollama serve"
                
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to Ollama. Please start it with: ollama serve"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            print("🤖 Generating answer with OpenAI...")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"❌ OpenAI Error: {response.status_code}"
                
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def answer_question(self, question: str) -> Dict:
        """
        Answer ANY question by searching web and using LLM.
        
        Args:
            question: Any question you want to ask
            
        Returns:
            Dict with 'answer' and 'sources'
        """
        print(f"\n{'='*80}")
        print(f"❓ Question: {question}")
        print(f"{'='*80}")
        
        # Step 1: Search the web
        print("\n🔍 Step 1: Searching the web for information...")
        search_results = self.search_web(question, num_results=5)
        
        if not search_results:
            return {
                'answer': "❌ I couldn't find any information on the web for this question. Try rephrasing it.",
                'sources': []
            }
        
        print(f"✅ Found {len(search_results)} relevant sources")
        
        # Step 2: Build context from search results
        context = ""
        for i, result in enumerate(search_results, 1):
            context += f"\nSource {i}:\n{result['snippet']}\n"
        
        # Step 3: Create prompt for LLM
        prompt = f"""You are a helpful assistant. Answer the following question based ONLY on the context provided. Be concise and accurate.

Context from web search:
{context}

Question: {question}

Instructions:
- Provide a clear, direct answer
- Use information from the context above
- If the context doesn't contain enough information, say so
- Keep your answer under 200 words

Answer:"""
        
        # Step 4: Generate answer using LLM
        print("\n🤖 Step 2: Generating answer using LLM...")
        if self.use_ollama:
            answer = self.call_ollama(prompt)
        else:
            answer = self.call_openai(prompt)
        
        return {
            'answer': answer,
            'sources': search_results
        }


def main():
    """Main interactive loop."""
    print("="*80)
    print("🌐 REAL RAG SYSTEM - Ask ANY Question!")
    print("="*80)
    print("\n✨ This system can answer questions about ANYTHING by:")
    print("   1. Searching the web for relevant information")
    print("   2. Using AI to generate accurate answers")
    print("\n💡 Setup:")
    print("   - Make sure Ollama is running: ollama serve")
    print("   - Or use OpenAI API (set use_ollama=False)")
    print("="*80)
    
    # Initialize RAG
    rag = RealRAGSystem(use_ollama=True)
    
    print("\n🎯 Example questions you can ask:")
    examples = [
        "What is quantum computing?",
        "Who won the latest FIFA World Cup?",
        "What are the health benefits of green tea?",
        "Explain blockchain technology",
        "What is the capital of France?",
        "How does photosynthesis work?"
    ]
    for i, ex in enumerate(examples, 1):
        print(f"   {i}. {ex}")
    
    print("\n" + "="*80)
    print("💬 Start asking questions! (type 'quit' to exit)")
    print("="*80)
    
    while True:
        print("\n")
        question = input("Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q', '']:
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
            break
        
        # Get answer
        result = rag.answer_question(question)
        
        # Display answer
        print(f"\n{'='*80}")
        print("📝 ANSWER:")
        print(f"{'='*80}")
        print(result['answer'])
        
        # Display sources
        if result['sources']:
            print(f"\n{'='*80}")
            print(f"📚 SOURCES ({len(result['sources'])} found):")
            print(f"{'='*80}")
            for i, source in enumerate(result['sources'][:3], 1):
                print(f"\n{i}. {source['title']}")
                if source['link']:
                    print(f"   🔗 {source['link']}")
        
        print(f"\n{'='*80}")


if __name__ == "__main__":
    main()
    