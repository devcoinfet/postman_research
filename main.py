import requests
from postman_scraper import *
import tldextract
import os
import uuid
#from tester import *

url = 'https://raw.githubusercontent.com/projectdiscovery/public-bugbounty-programs/main/chaos-bugbounty-list.json'#updated BB scopes



def extract_domain_parts(domain):
    """
    Extracts the subdomain and domain from a given domain string,
    correctly handling edge cases for TLDs, including country-code TLDs.
    """
    extracted = tldextract.extract(domain)
    # Reassemble domain without the TLD part.
    domain_without_tld = '.'.join(part for part in [extracted.subdomain, extracted.domain] if part)  # Exclude empty parts
    return domain_without_tld


    
    
def fetch_bugbounty_data(url):
    """
    Fetches the bug bounty program data from the given URL.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None
        

def parse_wildcard_scopes(data):
    """
    Parses the fetched data to extract entries from programs offering bounties.
    Now includes program name and URL along with the domain.
    Only considers programs with "bounty": true (as a boolean).
    """
    wildcard_scopes = []
    for program in data['programs']:  # Navigate through 'programs'
        if program.get('bounty') is True:  # Check if the program offers a bounty, explicitly checking for boolean True
            for domain in program.get('domains', []):
                scope_info = {
                    'name': program['name'],
                    'url': program['url'],
                    'domain': domain
                }
                if scope_info not in wildcard_scopes:  # Ensure unique entries
                    wildcard_scopes.append(scope_info)
    return wildcard_scopes

    
    

def create_unique_domain_dir(base_dir, domain):
    """
    Creates a unique directory for the domain's scraped results using a UUID.
    Returns the directory path.
    """
    unique_id = str(uuid.uuid4())
    dir_path = os.path.join(base_dir, f"{extract_domain_parts(domain)}_{unique_id}")
    os.makedirs(dir_path, exist_ok=True)
    print(f"Directory created: {dir_path}")
    return dir_path

def save_results_to_json(dir_path, data):
    """
    Saves scraped data to a JSON file within the specified directory.
    """
    filename = os.path.join(dir_path, f"results_{str(uuid.uuid4())}.json")
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Results saved to: {filename}")

    
def main():
    
     
    # Example call to the function
    ##results = scrape_workspace_collections("http://example.com")
    #print(results)
    
    data = fetch_bugbounty_data(url)
    if data:
        wildcard_scopes = parse_wildcard_scopes(data)
        if wildcard_scopes:  # Check if any scopes were found
            print("Scopes found:")
            for scope in wildcard_scopes:  # Adjust the slice as needed
                print(f"Program: {scope['name']}, URL: {scope['url']}, Domain: {scope['domain']}")
                tmp_clean_domain = extract_domain_parts(scope['domain'])#strip tld off domain so we can check a broader scope of leaks than just target.com matches this will get target and target.com
                print(f"Scraping Postman.com for  {tmp_clean_domain} leaks")
                
                try:
                   dir_path = create_unique_domain_dir('./reports', tmp_clean_domain)
                   postman_results = scrape_postman(tmp_clean_domain)
                   if postman_results:
                      print("Found Some Results\n")
                      print(postman_results)
                      save_results_to_json(dir_path, postman_results)
                      
                      tmp_json_results = json.loads(postman_results)
                      urls_to_check = tmp_json_results['URLS_SCRAPED']
                      print(urls_to_check)
                      '''
                      for urls in urls_to_check:
                          
                          try:
                             results = scrape_workspace_collections(urls)
                             if results:
                                print(results)
                          except Exception as ex:
                            print(ex)
                            pass
                      '''
                except Exception as PostmnScrpErr:
                  print(PostmnScrpErr)
                  pass
        else:
            print("No scopes found in the first few entries.")
     
if __name__ == "__main__":
    main()
