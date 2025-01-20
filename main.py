from searcher_prototype import ESGSearcher

def main():
    # Replace with your actual API key and CSE ID
    API_KEY = "AIzaSyAN2E1enTpjpQ2g8HuGypNa39MN2HfF9v0"
    CSE_ID = "075034cc0c205406e"

    searcher = ESGSearcher(API_KEY, CSE_ID)
    
    query = '"Johnson & Johnson" ("sustainability report" OR "ESG report" OR "climate impact" OR "carbon emissions" OR "net-zero goals") ("2023" OR "2022" OR "latest") -stock -shares'
    
    # Get and process search results
    search_results = searcher.search_reports(query)
    processed_data = searcher.process_search_results(search_results)
    
    # Print results
    print("\nProcessed Results:")
    for data in processed_data:
        print("\nResult:")
        for key, value in data.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()
