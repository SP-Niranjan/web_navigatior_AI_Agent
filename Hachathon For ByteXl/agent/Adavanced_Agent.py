from main import WebNavigatorAgent
import json
import time

class AdvancedWebAgent(WebNavigatorAgent):
    def __init__(self):
        super().__init__()
        
    def smart_search(self, query, websites=['google.com', 'wikipedia.org']):
        """Search multiple websites and compare results"""
        results = {}
        
        for site in websites:
            task = f"Go to {site} and search for {query}"
            print(f"🔍 Searching {site}...")
            result = self.process_request(task)
            results[site] = result.get('extracted_data', [])
            
        return results
        
    def website_comparison(self, sites):
        """Compare information from multiple websites"""
        comparison = {}
        
        for site in sites:
            print(f"📊 Analyzing {site}...")
            task = f"Go to {site} and extract page information"
            result = self.process_request(task)
            comparison[site] = {
                'status': result.get('status'),
                'data': result.get('extracted_data', [])
            }
            
        return comparison
        
    def generate_report(self, task, result):
        """Generate a formatted report using AI"""
        summary_prompt = f"Summarize this web automation result: {result}"
        
        messages = [
            {"role": "system", "content": "Create a brief, professional summary of web automation results."},
            {"role": "user", "content": summary_prompt}
        ]
        
        summary = self.llm.generate_response(messages)
        
        report = {
            'task': task,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': result.get('status'),
            'summary': summary,
            'raw_data': result.get('extracted_data', [])
        }
        
        return report

# Demo the advanced features
def demo_advanced_features():
    print("🚀 Advanced Web Navigator AI Agent Demo")
    print("=" * 50)
    
    agent = AdvancedWebAgent()
    
    # Feature 1: Smart Search
    print("\n🔍 Feature 1: Multi-Website Search")
    search_results = agent.smart_search("artificial intelligence", ['example.com'])
    print("Search Results:", json.dumps(search_results, indent=2)[:300] + "...")
    
    # Feature 2: Website Comparison  
    print("\n📊 Feature 2: Website Comparison")
    comparison = agent.website_comparison(['example.com', 'google.com'])
    print("Comparison Results:", json.dumps(comparison, indent=2)[:300] + "...")
    
    # Feature 3: AI Report Generation
    print("\n📋 Feature 3: AI Report Generation")
    test_result = {'status': 'completed', 'extracted_data': ['Example Domain', 'This domain is for examples']}
    report = agent.generate_report("Visit example.com", test_result)
    print("Generated Report:", json.dumps(report, indent=2)[:400] + "...")

if __name__ == "__main__":
    demo_advanced_features()
