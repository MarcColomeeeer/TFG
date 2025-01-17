import urllib.request
import xml.etree.ElementTree as ET
import os
import time
from datetime import datetime
import json

# Function to save data to a JSON file
def save_to_json(papers, filename="papers.json"):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(papers, file, ensure_ascii=False, indent=4)
    print(f"Data saved to {filename}")


# Example usage
def download_papers():
    # queries = [
        # "cat:cs.AI",
        # "cat:cs.AR",
        # "cat:cs.CC",
        # "cat:cs.CE",
        # "cat:cs.CG",
        # "cat:cs.CL",
        # "cat:cs.CR", aaaaaaaa
        # "cat:cs.CV",
        # "cat:cs.CY",
        # "cat:cs.DB",
        # "cat:cs.DC",
        # "cat:cs.DL",
        # "cat:cs.DM",
        # "cat:cs.DS",
        # "cat:cs.ET",
        # "cat:cs.FL",
        # "cat:cs.GL",
        # "cat:cs.GR",
        # "cat:cs.GT",
        # "cat:cs.HC",
        # "cat:cs.IR",
        # "cat:cs.IT",
        # "cat:cs.LG",
    #     "cat:cs.LO",
    #     "cat:cs.MA",
    #     "cat:cs.MM",
    #     "cat:cs.MS",
    #     "cat:cs.NA",
    #     "cat:cs.NE",
    #     "cat:cs.NI",
    #     "cat:cs.OH",
    #     "cat:cs.OS",
    #     "cat:cs.PF",
    #     "cat:cs.PL",
    #     "cat:cs.RO",
    #     "cat:cs.SC",
    #     "cat:cs.SD",
    #     "cat:cs.SE",
    #     "cat:cs.SI",
    #     "cat:cs.SY"
    # ]

    queries = [
        "cat:eess.AS",
        "cat:eess.IV",
        "cat:eess.SP",
        "cat:eess.SY",
    ]

    for query in queries:
        year_counts = {}  # Dictionary to count papers per year
        papers = []  # Local list passed to the function

        for value in range(0, 20001, 2000):
            for _ in range(0, 5):
            
                url = f'http://export.arxiv.org/api/query?search_query={query}&start={value}&max_results=2000'
        
                try:
                    data = urllib.request.urlopen(url)
                    # Decode with error handling
                    xml_data = data.read().decode('utf-8', errors='replace')
                except Exception as e:
                    print(f"Error fetching data: {e}")
                    return
                
                # Parse XML
                try:
                    root = ET.fromstring(xml_data)
                except ET.ParseError as e:
                    print(f"Error parsing XML: {e}")
                    return
                
                atom_ns = '{http://www.w3.org/2005/Atom}'
                arxiv_ns = '{http://arxiv.org/schemas/atom}'
                
                for entry in root.findall(f'{atom_ns}entry'):
                    # Extract unique paper ID
                    id_tag = entry.find(f'{atom_ns}id')
                    if id_tag is None:
                        continue
                    paper_id = id_tag.text
                    # Skip papers that have already been seen
                    if paper_id in seen_papers:
                        continue
                    
                    # Add paper to the seen set
                    seen_papers.add(paper_id)
                    
                    primary_category = entry.find(f'{arxiv_ns}primary_category').attrib['term']
                    # Check if primary category matches the query
                    if primary_category != query.split(':')[1]:
                        continue
                    
                    title = entry.find(f'{atom_ns}title').text
                    authors = [author.find(f'{atom_ns}name').text for author in entry.findall(f'{atom_ns}author')]
                    summary = entry.find(f'{atom_ns}summary').text
                    published_date = entry.find(f'{atom_ns}published').text
                    pdf_link = entry.find(f'{atom_ns}link[@title="pdf"]').attrib['href']
                    
                    # Extract year only
                    published_year = datetime.strptime(published_date, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y')
                    
                    # Increment year count
                    if published_year in year_counts:
                        year_counts[published_year] += 1
                    else:
                        year_counts[published_year] = 1
                    
                    papers.append({
                        "title": title,
                        "authors": authors,
                        "category": primary_category,
                        "published_year": published_year,
                        "summary": summary,
                        "pdf_link": pdf_link
                    })                
                time.sleep(3)

        # Print year counts
        for year, count in sorted(year_counts.items()):
            print(f"{year}: {count}")

        # Save data to JSON
        filename = f"{query.split(':')[1]}.json"
        save_to_json(papers, filename=filename)


seen_papers = set()

# Run the download process
download_papers()