import json
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class WebAgent:
    def __init__(self, llm_handler, browser_tools):
        self.llm = llm_handler
        self.browser = browser_tools

    def execute_task(self, user_input):
        # Start browser
        start_result = self.browser.start_browser()
        if start_result.get("status") != "success":
            return {"status": "error", "message": "Failed to start browser"}
        
        try:
            # Step 1: Classify the task type
            task_type = self.classify_task(user_input)
            print(f"🧠 Task classified as: {task_type}")
            
            # Step 2: Execute based on task type
            if task_type == "shopping":
                return self._handle_shopping(user_input)
            elif task_type == "navigation":
                return self._handle_navigation(user_input)
            elif task_type == "question":
                return self._handle_question(user_input)
            elif task_type == "search":
                return self._handle_search(user_input)
            else:
                return self._handle_general(user_input)
                
        finally:
            self.browser.close_browser()
            
    def classify_task(self, user_input):
        """Enhanced task classification"""
        text = user_input.lower().strip()
        
        # Shopping keywords
        shopping_keywords = [
            "best", "buy", "purchase", "price", "cheap", "expensive", 
            "under", "rupees", "dollars", "shoes", "phone", "laptop",
            "product", "compare", "review", "rating", "deals"
        ]
        if any(keyword in text for keyword in shopping_keywords):
            return "shopping"
            
        # Navigation commands
        nav_keywords = ["go to", "navigate to", "visit", "open"]
        if any(keyword in text for keyword in nav_keywords):
            return "navigation"
            
        # Question patterns
        question_keywords = ["what is", "who is", "how does", "why does", "tell me about"]
        if any(keyword in text for keyword in question_keywords):
            return "question"
            
        # Search patterns  
        search_keywords = ["search for", "find", "look up", "research"]
        if any(keyword in text for keyword in search_keywords):
            return "search"
            
        return "general"
        
    def _handle_shopping(self, user_input):
        """Handle shopping/product search requests"""
        print(f"🛒 Performing shopping search...")
        
        # Navigate to Google
        nav_result = self.browser.navigate_to("google.com")
        if nav_result.get("status") != "success":
            return {"status": "error", "message": "Could not access Google"}
        
        try:
            # Wait for and find the search box
            wait = WebDriverWait(self.browser.driver, 10)
            search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
            
            # Clear and type search query
            search_box.clear()
            search_box.send_keys(user_input)
            search_box.send_keys(Keys.RETURN)
            
            # Wait for results to load
            time.sleep(3)
            
            # Extract search results
            results = self._extract_search_results()
            
            # Use AI to analyze and format results
            formatted_results = self._format_shopping_results(user_input, results)
            
            return {
                "status": "completed",
                "extracted_data": formatted_results,
                "execution_log": [nav_result, {"status": "success", "action": "search_performed"}]
            }
            
        except Exception as e:
            # Fallback: extract basic page content
            extract_result = self.browser.extract_text()
            return {
                "status": "completed",
                "extracted_data": [f"Search performed for: {user_input}", "Found Google search results"],
                "execution_log": [nav_result]
            }
    
    def _extract_search_results(self):
        """Extract search result snippets from Google results page"""
        results = []
        try:
            # Look for search result containers (Google's class names change, so we try multiple)
            selectors = [
                "div.g",  # Common Google result container
                ".tF2Cxc",  # Another Google result class
                "div[data-async-context]",  # Alternative selector
                ".ULSxyf",  # Shopping results
                ".X7NTVe"   # Product cards
            ]
            
            for selector in selectors:
                elements = self.browser.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for i, element in enumerate(elements[:5]):  # Get top 5 results
                        try:
                            text = element.text.strip()
                            if text and len(text) > 10:  # Only meaningful content
                                results.append(f"Result {i+1}: {text[:200]}...")
                        except:
                            continue
                    break  # If we found results with one selector, stop trying others
            
            # If no structured results, get general page text
            if not results:
                page_text = self.browser.driver.find_element(By.TAG_NAME, "body").text
                # Extract relevant lines that might contain product info
                lines = page_text.split('\n')
                for line in lines[:10]:
                    if any(word in line.lower() for word in ['price', '₹', 'buy', 'rating', 'review']):
                        results.append(line.strip())
                        
        except Exception as e:
            results = [f"Could not extract detailed results, but search was performed"]
            
        return results if results else ["Search completed - check browser for results"]
    
    def _format_shopping_results(self, query, raw_results):
        """Use AI to format shopping results nicely"""
        try:
            # Create context for LLM
            context = "\n".join(raw_results[:5])  # Top 5 results
            
            messages = [
                {"role": "system", "content": "You are a helpful shopping assistant. Format search results into a clean, useful summary for the user. Focus on products, prices, and key details."},
                {"role": "user", "content": f"User searched for: '{query}'\n\nSearch results found:\n{context}\n\nPlease format this into a helpful shopping summary:"}
            ]
            
            formatted_response = self.llm.generate_response(messages)
            
            # Combine formatted response with raw results
            return [
                f"🛒 Shopping Search Results for: {query}",
                f"📋 AI Summary: {formatted_response}",
                "📊 Raw Results:",
                *raw_results[:3]  # Include top 3 raw results
            ]
            
        except:
            return [
                f"🛒 Shopping Search Results for: {query}",
                *raw_results[:5]
            ]
    
    def _handle_navigation(self, user_input):
        """Handle direct navigation tasks"""
        url = self._extract_url(user_input)
        if url:
            nav_result = self.browser.navigate_to(url)
            if nav_result.get("status") == "success":
                extract_result = self.browser.get_page_title()
                return {
                    "status": "completed",
                    "extracted_data": extract_result.get("data", []),
                    "execution_log": [nav_result, extract_result]
                }
        return {"status": "error", "message": "Could not find URL to navigate to"}
        
    def _handle_question(self, user_input):
        """Handle questions by searching Google"""
        topic = self._extract_question_topic(user_input)
        print(f"🔍 Searching for: {topic}")
        
        nav_result = self.browser.navigate_to("google.com")
        if nav_result.get("status") != "success":
            return {"status": "error", "message": "Could not access search engine"}
            
        try:
            # Perform actual Google search
            wait = WebDriverWait(self.browser.driver, 10)
            search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
            search_box.clear()
            search_box.send_keys(topic)
            search_box.send_keys(Keys.RETURN)
            time.sleep(2)
            
            # Extract search results
            results = self._extract_search_results()
            answer = self._generate_answer(user_input, results)
            
            return {
                "status": "completed",
                "extracted_data": [f"Answer: {answer}"],
                "execution_log": [nav_result, {"status": "success", "action": "search_performed"}]
            }
        except:
            extract_result = self.browser.extract_text()
            answer = self._generate_answer(user_input, extract_result.get("data", []))
            return {
                "status": "completed",
                "extracted_data": [f"Answer: {answer}"],
                "execution_log": [nav_result, extract_result]
            }
        
    def _handle_search(self, user_input):
        """Handle explicit search requests"""
        search_term = user_input.replace("search for", "").replace("find", "").strip()
        return self._handle_shopping(search_term)  # Treat search as shopping for now
        
    def _handle_general(self, user_input):
        """Handle general requests"""
        return self._handle_shopping(user_input)  # Default to shopping search
        
    # Helper methods (same as before)
    def _extract_question_topic(self, question):
        question = question.lower()
        for phrase in ["what is", "who is", "how does", "why does", "tell me about"]:
            question = question.replace(phrase, "").strip()
        return question
        
    def _generate_answer(self, question, web_data):
        try:
            context = " ".join(web_data[:3]) if web_data else "Search results"
            messages = [
                {"role": "system", "content": "Answer questions helpfully based on the context provided."},
                {"role": "user", "content": f"Question: {question}\nContext: {context}\nAnswer:"}
            ]
            return self.llm.generate_response(messages)
        except:
            return f"I found information about: {self._extract_question_topic(question)}"
        
    def _extract_url(self, text):
        domains = ["google.com", "wikipedia.org", "example.com", "github.com"]
        text_lower = text.lower()
        
        for domain in domains:
            if domain in text_lower:
                return domain
                
        import re
        url_pattern = r'([a-zA-Z0-9-]+\.(?:com|org|net|edu|gov))'
        match = re.search(url_pattern, text)
        if match:
            return match.group(1)
            
        return None
# agent = WebAgent(llm_handler=None, browser_tools=None)
# print(agent.classify_task("buy a laptop under 50000"))

