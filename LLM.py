import requests
import json
from typing import List, Dict
import re

class UniversalRAG:
    """
    A RAG system that can answer ANY question by searching the web.
    No extra dependencies needed - just requests!
    """
    
    def __init__(self, use_ollama: bool = True, openai_key: str = None):
        self.use_ollama = use_ollama
        self.openai_key = openai_key
        print("✅ Universal RAG System initialized")
        print("💡 You can ask ANYTHING - no limitations!")
    
    def search_wikipedia(self, query: str) -> List[Dict]:
        """Search Wikipedia for information."""
        try:
            # Step 1: Search for relevant articles
            search_url = "https://en.wikipedia.org/w/api.php"
            search_params = {
                'action': 'opensearch',
                'search': query,
                'limit': 5,
                'format': 'json'
            }
            
            response = requests.get(search_url, params=search_params, timeout=10)
            search_data = response.json()
            
            results = []
            titles = search_data[1] if len(search_data) > 1 else []
            descriptions = search_data[2] if len(search_data) > 2 else []
            links = search_data[3] if len(search_data) > 3 else []
            
            # Step 2: Get detailed content for each result
            for i, title in enumerate(titles[:3]):
                try:
                    # Get page summary
                    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
                    summary_response = requests.get(summary_url, timeout=5)
                    
                    if summary_response.status_code == 200:
                        data = summary_response.json()
                        extract = data.get('extract', '')
                        
                        if extract and len(extract) > 50:  # Only add if substantial content
                            results.append({
                                'title': data.get('title', title),
                                'snippet': extract,
                                'link': data.get('content_urls', {}).get('desktop', {}).get('page', links[i] if i < len(links) else '')
                            })
                except Exception as e:
                    # Fallback to basic info
                    if i < len(descriptions) and descriptions[i]:
                        results.append({
                            'title': title,
                            'snippet': descriptions[i],
                            'link': links[i] if i < len(links) else ''
                        })
            
            return results
            
        except Exception as e:
            print(f"⚠️ Wikipedia search error: {str(e)}")
            return []
    
    def search_duckduckgo_api(self, query: str) -> List[Dict]:
        """Search using DuckDuckGo Instant Answer API."""
        try:
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
            
            # Get main abstract
            if data.get('Abstract') and len(data.get('Abstract', '')) > 50:
                results.append({
                    'title': data.get('Heading', 'Main Answer'),
                    'snippet': data.get('Abstract'),
                    'link': data.get('AbstractURL', '')
                })
            
            # Get related topics
            for topic in data.get('RelatedTopics', [])[:4]:
                if isinstance(topic, dict) and 'Text' in topic:
                    text = topic.get('Text', '')
                    if len(text) > 50:  # Only substantial content
                        results.append({
                            'title': text[:80] + '...' if len(text) > 80 else text,
                            'snippet': text,
                            'link': topic.get('FirstURL', '')
                        })
            
            return results
            
        except Exception as e:
            print(f"⚠️ DuckDuckGo search error: {str(e)}")
            return []
    
    def search_web(self, query: str) -> List[Dict]:
        """
        Search the web using multiple sources.
        Works for ANY question!
        """
        print(f"🔍 Searching for: '{query}'")
        
        all_results = []
        
        # Try Wikipedia first (most reliable and detailed)
        print("   📚 Searching Wikipedia...")
        wiki_results = self.search_wikipedia(query)
        if wiki_results:
            print(f"   ✓ Found {len(wiki_results)} Wikipedia results")
            all_results.extend(wiki_results)
        
        # Try DuckDuckGo for additional info
        print("   🦆 Searching DuckDuckGo...")
        ddg_results = self.search_duckduckgo_api(query)
        if ddg_results:
            print(f"   ✓ Found {len(ddg_results)} DuckDuckGo results")
            all_results.extend(ddg_results)
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_results = []
        for result in all_results:
            title_lower = result['title'].lower()
            if title_lower not in seen_titles and result['snippet']:
                seen_titles.add(title_lower)
                unique_results.append(result)
        
        return unique_results[:5]  # Return top 5 unique results
    
    def call_ollama(self, prompt: str, model: str = "llama2") -> str:
        """Generate answer using Ollama."""
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
            
            response = requests.post(url, json=data, timeout=180)
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                return f"❌ Ollama error (status {response.status_code})"
                
        except requests.exceptions.ConnectionError:
            return """❌ Cannot connect to Ollama!

Please start Ollama:
1. Open a NEW Command Prompt window
2. Type: ollama serve
3. Keep that window open
4. Come back here and try again"""
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def call_openai(self, prompt: str) -> str:
        """Generate answer using OpenAI."""
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
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"❌ OpenAI error: {response.status_code}"
                
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def answer(self, question: str) -> Dict:
        """
        Answer ANY question - no limitations!
        
        Args:
            question: ANY question you want to ask
            
        Returns:
            Dict with answer and sources
        """
        if not question or question.strip() == "":
            return {
                'answer': "Please ask a question!",
                'sources': []
            }
        
        print(f"\n{'='*80}")
        print(f"❓ Your Question: {question}")
        print(f"{'='*80}\n")
        
        # Step 1: Search the web
        search_results = self.search_web(question)
        
        if not search_results:
            return {
                'answer': """❌ I couldn't find information for this question.

Possible reasons:
• No internet connection
• Question too vague
• Try rephrasing your question

Example questions that work well:
• "What is Python programming?"
• "Who invented the telephone?"
• "What is photosynthesis?"
• "Explain quantum computing"
""",
                'sources': []
            }
        
        print(f"\n✅ Found {len(search_results)} relevant sources\n")
        
        # Step 2: Build context from search results
        context = "Information from web sources:\n\n"
        for i, result in enumerate(search_results, 1):
            context += f"[Source {i}] {result['title']}:\n{result['snippet']}\n\n"
        
        # Step 3: Create prompt for LLM
        prompt = f"""You are a helpful AI assistant. Answer the question below using ONLY the information provided in the context.

{context}

Question: {question}

Instructions:
• Give a clear, direct answer
• Use information from the sources above
• Be concise (2-3 paragraphs maximum)
• If the context doesn't contain enough information, say so

Answer:"""
        
        # Step 4: Generate answer using LLM
        print("🤖 Generating answer with AI...")
        print("   (This may take 10-30 seconds...)\n")
        
        if self.use_ollama:
            answer = self.call_ollama(prompt)
        else:
            answer = self.call_openai(prompt)
        
        return {
            'answer': answer,
            'sources': search_results
        }


def main():
    """Interactive Q&A loop."""
    print("="*80)
    print("🌐 UNIVERSAL RAG SYSTEM - Ask ANYTHING!")
    print("="*80)
    print("\n✨ This system can answer questions about ANY topic:")
    print("   • Science, History, Geography, Technology")
    print("   • Sports, Entertainment, Health, Politics")
    print("   • Current events, Famous people, Definitions")
    print("   • Literally ANYTHING!")
    print("\n⚙️  Requirements:")
    print("   ✓ Ollama must be running (run: ollama serve)")
    print("   ✓ Internet connection")
    print("   ✓ No extra packages needed!")
    print("="*80)
    
    # Initialize system
    rag = UniversalRAG(use_ollama=True)
    
    print("\n💬 START ASKING! Type any question (or 'quit' to exit)")
    print("="*80)
    print("\n💡 Example questions to try:")
    examples = [
        "What is artificial intelligence?",
        "Who is Elon Musk?",
        "How does the internet work?",
        "What is the tallest mountain?",
        "Explain photosynthesis",
        "What causes earthquakes?"
    ]
    for i, ex in enumerate(examples, 1):
        print(f"   {i}. {ex}")
    print("\n   ...or ask literally anything else!")
    print("="*80)
    
    while True:
        try:
            question = input("\n🎤 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q', 'bye']:
                print("\n👋 Thanks for using Universal RAG! Goodbye!")
                break
            
            if not question:
                print("   ⚠️ Please type a question!")
                continue
            
            # Get answer
            result = rag.answer(question)
            
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
                for i, source in enumerate(result['sources'], 1):
                    print(f"\n{i}. {source['title']}")
                    if source['link']:
                        print(f"   🔗 {source['link']}")
            
            print(f"\n{'='*80}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            print("Please try again with a different question.")


if __name__ == "__main__":
    main()
    # For testing purposes, you can also call:
    # rag = UniversalRAG(use_ollama=True)
    # result = rag.answer("What is the capital of France?")
    # print(result['answer'])