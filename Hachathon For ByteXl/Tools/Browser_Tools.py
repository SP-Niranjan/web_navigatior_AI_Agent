from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

class BrowserTools:
    def __init__(self):
        self.driver = None
        
    def start_browser(self, headless=True):
        """Start Chrome browser with automatic driver management"""
        try:
            # Chrome options
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Auto-download and setup ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            return {"status": "success", "message": "Browser started"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    def navigate_to(self, url):
        """Navigate to a URL"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            self.driver.get(url)
            time.sleep(2)  # Wait for page load
            return {"status": "success", "url": self.driver.current_url}
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    def click_element(self, selector):
        """Click an element using CSS selector"""
        try:
            wait = WebDriverWait(self.driver, 10)
            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    def type_text(self, selector, text):
        """Type text into an element"""
        try:
            wait = WebDriverWait(self.driver, 10)
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            element.clear()
            element.send_keys(text)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    def extract_text(self, selector=None):
        """Extract text from page or specific element"""
        try:
            if selector:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                texts = [elem.text for elem in elements if elem.text.strip()]
            else:
                # Extract page title and main content
                title = self.driver.title
                body = self.driver.find_element(By.TAG_NAME, "body").text[:500]
                texts = [f"Title: {title}", f"Content: {body}"]
            
            return {"status": "success", "data": texts}
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    def get_page_title(self):
        """Get current page title"""
        try:
            return {"status": "success", "data": [self.driver.title]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    def close_browser(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
