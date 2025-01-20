from googleapiclient.discovery import build
import requests
from bs4 import BeautifulSoup
import re
import os
from typing import List, Dict, Optional

class ESGSearcher:
    def __init__(self, api_key: str, cse_id: str):
        """
        Initialize the ESG searcher with Google Custom Search credentials.
        
        Args:
            api_key (str): Google API key
            cse_id (str): Custom Search Engine ID
        """
        self.api_key = api_key
        self.cse_id = cse_id
        self.service = build("customsearch", "v1", developerKey=api_key)

    def search_reports(self, query: str, num_results: int = 10) -> List[Dict]:
        """
        Search for ESG reports using Google Custom Search API.
        
        Args:
            query (str): Search query string
            num_results (int): Number of results to return
            
        Returns:
            List[Dict]: List of search results with titles and links
        """
        results = []
        try:
            search_response = self.service.cse().list(
                q=query,
                cx=self.cse_id,
                num=num_results
            ).execute()
            
            for item in search_response.get("items", []):
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet")
                })
        except Exception as e:
            print(f"Error during search: {e}")
        return results

    def fetch_content(self, url: str) -> Optional[Dict]:
        """
        Fetch content from a URL, handling both HTML and PDF content.
        
        Args:
            url (str): URL to fetch
            
        Returns:
            Optional[Dict]: Dictionary containing content type and extracted text/file path
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            if "application/pdf" in response.headers.get("Content-Type", ""):
                # Ensure downloads directory exists
                os.makedirs("downloads", exist_ok=True)
                pdf_name = f"downloads/{url.split('/')[-1]}"
                with open(pdf_name, "wb") as pdf_file:
                    pdf_file.write(response.content)
                return {"type": "pdf", "content": pdf_name}
            else:
                soup = BeautifulSoup(response.text, "html.parser")
                text = " ".join([p.get_text() for p in soup.find_all("p")])
                return {"type": "html", "content": text}
        except Exception as e:
            print(f"Error fetching content from {url}: {e}")
            return None

    def parse_esg_data(self, content: Dict) -> Dict:
        """
        Parse ESG-related data from fetched content.
        
        Args:
            content (Dict): Content dictionary from fetch_content
            
        Returns:
            Dict: Extracted ESG data
        """
        data = {}
        carbon_pattern = r"carbon emissions(?:[^0-9]*)([0-9,]+) (metric tons|MT|tCO2e)"
        net_zero_pattern = r"net-zero by (\d{4})"

        if content["type"] == "html":
            text = content["content"]
            carbon_match = re.search(carbon_pattern, text, re.IGNORECASE)
            net_zero_match = re.search(net_zero_pattern, text, re.IGNORECASE)

            if carbon_match:
                data["carbon_emissions"] = f"{carbon_match.group(1)} {carbon_match.group(2)}"
            if net_zero_match:
                data["net_zero_target"] = net_zero_match.group(1)
        elif content["type"] == "pdf":
            # TODO: Implement PDF parsing
            data["note"] = "PDF parsing not implemented yet"

        return data

    def validate_data(self, data: Dict) -> Dict:
        """
        Validate extracted ESG data.
        
        Args:
            data (Dict): Extracted ESG data
            
        Returns:
            Dict: Validated ESG data with potential error messages
        """
        if "carbon_emissions" not in data:
            data["error"] = data.get("error", []) + ["Missing carbon emissions data"]
        if "net_zero_target" not in data:
            data["error"] = data.get("error", []) + ["Missing net-zero target"]
        return data

    def process_search_results(self, results: List[Dict]) -> List[Dict]:
        """
        Process a list of search results to extract ESG data.
        
        Args:
            results (List[Dict]): List of search results
            
        Returns:
            List[Dict]: Processed results with extracted ESG data
        """
        processed_data = []
        for result in results:
            print(f"Processing: {result['title']} - {result['link']}")
            content = self.fetch_content(result["link"])
            if content:
                parsed_data = self.parse_esg_data(content)
                validated_data = self.validate_data(parsed_data)
                validated_data.update({
                    "source": result["link"],
                    "title": result["title"],
                    "snippet": result["snippet"]
                })
                processed_data.append(validated_data)
        return processed_data

def main():
    API_KEY = "AIzaSyAN2E1enTpjpQ2g8HuGypNa39MN2HfF9v0"
    CSE_ID = "075034cc0c205406e"
    
    searcher = ESGSearcher(API_KEY, CSE_ID)
    
    # Example search query
    query = '"Johnson & Johnson" ("sustainability report" OR "ESG report" OR "climate impact" OR "carbon emissions" OR "net-zero goals") ("2023" OR "2022" OR "latest") -stock -shares'
    
    # Perform search
    search_results = searcher.search_reports(query)
    
    # Process and extract data from search results
    processed_data = searcher.process_search_results(search_results)
    
    # Print results
    print("\nProcessed Results:")
    for data in processed_data:
        print("\nResult:")
        for key, value in data.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    main() 