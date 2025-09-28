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
        start_result = self.browser.start_browser()
        if start_result.get("status") != "success":
            return {"status": "error", "message": "Failed to start browser"}
        
        try:
            task_type = self.classify_task(user_input)
            print(f"Task classified as: {task_type}")
            
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
        text = user_input.lower().strip()
        shopping_keywords = ["best", "buy", "purchase", "price", "cheap", "expensive", 
                             "under", "rupees", "dollars", "shoes", "phone", "laptop",
                             "product", "compare", "review", "rating", "deals"]
        if any(keyword in text for keyword in shopping_keywords):
            return "shopping"
        nav_keywords = ["go to", "navigate to", "visit", "open"]
        if any(keyword in text for keyword in nav_keywords):
            return "navigation"
        question_keywords = ["what is", "who is", "how does", "why does", "tell me about"]
        if any(keyword in text for keyword in question_keywords):
            return "question"
        search_keywords = ["search for", "find", "look up", "research"]
        if any(keyword in text for keyword in search_keywords):
            return "search"
        return "general"
        
    def _handle_shopping(self, user_input):
        nav_result = self.browser.navigate_to("google.com")
        if nav_result.get("status") != "success":
            return {"status": "error", "message": "Could not access Google"}
        
        try:
            wait = WebDriverWait(self.browser.driver, 10)
            search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
            search_box.clear()
            search_box.send_keys(user_input)
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)
            results = self._extract_search_results()
            formatted_results = self._format_shopping_results(user_input, results)
            return {"status": "completed",
                    "extracted_data": formatted_results,
                    "execution_log": [nav_result, {"status": "success", "action": "search_performed"}]}
        except:
            extract_result = self.browser.extract_text()
            return {"status": "completed",
                    "extracted_data": [f"Search performed for: {user_input}", "Found Google search results"],
                    "execution_log": [nav_result]}
    
    def _extract_search_results(self):
        results = []
        try:
            selectors = ["div.g", ".tF2Cxc", "div[data-async-context]", ".ULSxyf", ".X7NTVe"]
            for selector in selectors:
                elements = self.browser.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for i, element in enumerate(elements[:5]):
                        try:
                            text = element.text.strip()
                            if text and len(text) > 10:
                                results.append(f"Result {i+1}: {text[:200]}...")
                        except:
                            continue
                    break
            if not results:
                page_text = self.browser.driver.find_element(By.TAG_NAME, "body").text
                lines = page_text.split('\n')
                for line in lines[:10]:
                    if any(word in line.lower() for word in ['price', '₹', 'buy', 'rating', 'review']):
                        results.append(line.strip())
        except:
            results = ["Could not extract detailed results, but search was performed"]
        return results if results else ["Search completed - check browser for results"]
    
    def _format_shopping_results(self, query, raw_results):
        try:
            context = "\n".join(raw_results[:5])
            messages = [{"role": "system", "content": "You are a helpful shopping assistant. Format search results into a clean, useful summary for the user. Focus on products, prices, and key details."},
                        {"role": "user", "content": f"User searched for: '{query}'\n\nSearch results found:\n{context}\n\nPlease format this into a helpful shopping summary:"}]
            formatted_response = self.llm.generate_response(messages)
            return [f"Shopping Search Results for: {query}",
                    f"AI Summary: {formatted_response}",
                    "Raw Results:",
                    *raw_results[:3]]
        except:
            return [f"Shopping Search Results for: {query}", *raw_results[:5]]
    
    def _handle_navigation(self, user_input):
        url = self._extract_url(user_input)
        if url:
            nav_result = self.browser.navigate_to(url)
            if nav_result.get("status") == "success":
                extract_result = self.browser.get_page_title()
                return {"status": "completed",
                        "extracted_data": extract_result.get("data", []),
                        "execution_log": [nav_result, extract_result]}
        return {"status": "error", "message": "Could not find URL to navigate to"}
        
    def _handle_question(self, user_input):
        topic = self._extract_question_topic(user_input)
        nav_result = self.browser.navigate_to("google.com")
        if nav_result.get("status") != "success":
            return {"status": "error", "message": "Could not access search engine"}
        try:
            wait = WebDriverWait(self.browser.driver, 10)
            search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
            search_box.clear()
            search_box.send_keys(topic)
            search_box.send_keys(Keys.RETURN)
            time.sleep(2)
            results = self._extract_search_results()
            answer = self._generate_answer(user_input, results)
            return {"status": "completed",
                    "extracted_data": [f"Answer: {answer}"],
                    "execution_log": [nav_result, {"status": "success", "action": "search_performed"}]}
        except:
            extract_result = self.browser.extract_text()
            answer = self._generate_answer(user_input, extract_result.get("data", []))
            return {"status": "completed",
                    "extracted_data": [f"Answer: {answer}"],
                    "execution_log": [nav_result, extract_result]}
        
    def _handle_search(self, user_input):
        search_term = user_input.replace("search for", "").replace("find", "").strip()
        return self._handle_shopping(search_term)
        
    def _handle_general(self, user_input):
        return self._handle_shopping(user_input)
    
    def _extract_question_topic(self, question):
        question = question.lower()
        for phrase in ["what is", "who is", "how does", "why does", "tell me about"]:
            question = question.replace(phrase, "").strip()
        return question
        
    def _generate_answer(self, question, web_data):
        try:
            context = " ".join(web_data[:3]) if web_data else "Search results"
            messages = [{"role": "system", "content": "Answer questions helpfully based on the context provided."},
                        {"role": "user", "content": f"Question: {question}\nContext: {context}\nAnswer:"}]
            return self.llm.generate_response(messages)
        except:
            return f"I found information about: {self._extract_question_topic(question)}"
        
    def _extract_url(self, text):
        domains = ["google.com", "wikipedia.org", "example.com", "github.com"]
        text_lower = text.lower()
        for domain in domains:
            if domain in text_lower:
                return domain
        url_pattern = r'([a-zA-Z0-9-]+\.(?:com|org|net|edu|gov))'
        match = re.search(url_pattern, text)
        if match:
            return match.group(1)
        return None
