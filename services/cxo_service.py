import requests
from bs4 import BeautifulSoup
import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import search_cxo_in_db, log_search
from config.config import CXO_DATABASE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xhtml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

CXO_TITLES = [
    'CEO', 'Chief Executive Officer',
    'CFO', 'Chief Financial Officer',
    'CTO', 'Chief Technology Officer',
    'COO', 'Chief Operating Officer',
    'CMO', 'Chief Marketing Officer',
    'CIO', 'Chief Information Officer',
    'CISO', 'Chief Information Security Officer',
    'CPO', 'Chief Product Officer',
    'CDO', 'Chief Data Officer',
    'CLO', 'Chief Legal Officer',
    'CHRO', 'Chief Human Resources Officer',
    'President', 'Managing Director', 'Executive Director',
    'Vice President', 'SVP', 'EVP', 'General Counsel',
    'Board Member', 'Chairman', 'Chairwoman',
]

def search_cxo(company_name):
    """Main search function - DB first, then web fallback."""
    results = []
    
    # 1. Search in our local DB
    db_results = search_cxo_in_db(company_name)
    if db_results:
        results.extend(db_results)
    
    # 2. Also scan CXO_DATABASE list for partial matches
    company_lower = company_name.lower()
    for cxo in CXO_DATABASE:
        if company_lower in cxo['company'].lower():
            # Check not already in results
            already = any(r.get('name') == cxo['name'] for r in results)
            if not already:
                results.append({
                    'name': cxo['name'],
                    'title': cxo['title'],
                    'company': cxo['company'],
                    'linkedin': cxo.get('linkedin', ''),
                    'email': '',
                    'source': 'database'
                })
    
    # 3. Web search fallback
    web_results = search_web(company_name)
    for wr in web_results:
        already = any(r.get('name') == wr.get('name') for r in results)
        if not already and wr.get('name'):
            results.append(wr)
    
    log_search(company_name, len(results))
    return results

def search_web(company_name):
    """Search the web for CXO contacts."""
    results = []
    
    queries = [
        f"{company_name} CEO CTO CFO executives leadership team",
        f"{company_name} C-suite executives officers",
        f"site:linkedin.com {company_name} CEO OR CFO OR CTO",
    ]
    
    for query in queries[:2]:  # Limit to 2 queries
        try:
            url = f"https://www.google.com/search?q={requests.utils.quote(query)}&num=10"
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code == 200:
                found = parse_google_results(resp.text, company_name)
                results.extend(found)
                if results:
                    break
        except Exception as e:
            print(f"[Web] Search error: {e}")
    
    # Also try DuckDuckGo
    if not results:
        try:
            url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(company_name + ' CEO CFO CTO executives')}"
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code == 200:
                found = parse_ddg_results(resp.text, company_name)
                results.extend(found)
        except Exception as e:
            print(f"[DDG] Search error: {e}")
    
    return results

def parse_google_results(html, company_name):
    """Extract CXO names from Google search results."""
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    seen = set()
    
    # Extract all text snippets
    for elem in soup.find_all(['span', 'div', 'p'], limit=200):
        text = elem.get_text(separator=' ', strip=True)
        if len(text) < 10 or len(text) > 500:
            continue
        
        found = extract_cxo_from_text(text, company_name)
        for f in found:
            key = f['name'].lower()
            if key not in seen:
                seen.add(key)
                results.append(f)
    
    return results[:10]

def parse_ddg_results(html, company_name):
    """Extract CXO names from DuckDuckGo results."""
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    seen = set()
    
    for elem in soup.find_all(class_=['result__snippet', 'result__title']):
        text = elem.get_text(separator=' ', strip=True)
        found = extract_cxo_from_text(text, company_name)
        for f in found:
            key = f['name'].lower()
            if key not in seen:
                seen.add(key)
                results.append(f)
    
    return results[:10]

def extract_cxo_from_text(text, company_name):
    """Use regex patterns to extract CXO names and titles from text."""
    results = []
    
    # Pattern: "Name, Title at Company" or "Name is the CEO of Company"
    patterns = [
        r'([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?),?\s+(?:is\s+)?(?:the\s+)?(' + '|'.join(CXO_TITLES[:20]) + r')',
        r'(' + '|'.join(CXO_TITLES[:20]) + r')\s+([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?)',
        r'([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s+serves?\s+as\s+(?:the\s+)?(' + '|'.join(CXO_TITLES[:10]) + r')',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if len(match) == 2:
                name, title = match[0], match[1]
                if len(name) > 30 or name.lower() in ['the company', 'this company']:
                    continue
                # Swap if title came first
                for t in CXO_TITLES[:20]:
                    if name.upper() == t or name == t:
                        name, title = title, name
                        break
                
                results.append({
                    'name': name.strip(),
                    'title': title.strip(),
                    'company': company_name,
                    'email': '',
                    'linkedin': f"https://linkedin.com/search/results/people/?keywords={requests.utils.quote(name + ' ' + company_name)}",
                    'source': 'web'
                })
    
    return results
