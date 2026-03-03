from hashlib import sha1

import requests
from bs4 import BeautifulSoup
from utils import Utils
import fitz
import re
from sync import Sync



class Scraper:
    def __init__(self):
        self.headers = {
            # The ID Card (User Agent)
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # The Language (I speak English)
            "Accept-Language": "en-US,en;q=0.9",
            # The Referer (I came from Google, not a script)
            "Referer": "https://www.google.com/",
            # The Capability (I can read HTML)
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            # The Connection (Keep the line open)
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "DNT": "1",  # Do Not Track
        }

    ledger = Sync()
    def get_pdf_text(self,pdf_path):
        if not pdf_path:
            return []
        try:
            document = fitz.open(pdf_path)
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return []
        text =  ""
        
        
        for page in document:
            text += page.get_text()
            
        document.close()
        cleaned_text = Utils.clean_text(text)
        chunk_texts = Utils.chunk_text(cleaned_text)
        
        
        chunks=[]
        if chunk_texts:
                for chunk in chunk_texts:
                    chunk_id = Utils.sha256(chunk)
                    if self.ledger.is_duplicate(chunk_id):
                        continue
                    chunks.append({
                        "id": chunk_id,
                        "text": chunk,
                        "source": pdf_path
                })
        return chunks
    def get_pdf_text_plib(self,pdf_path):
        if not pdf_path:
            return []
        try:
            document = fitz.open(pdf_path)
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return []
        text =  ""
        
        
        for page in document:
            text += page.get_text()
            
        document.close()
        cleaned_text = Utils.clean_text(text)
        pattern = r"\|\s*#[^\s]+"
        raw_chunks = re.split(pattern, cleaned_text)
        text_chunks = [chunk.strip() for chunk in raw_chunks if chunk.strip()]
        chunks = []
        if text_chunks:
            for chunk in text_chunks:
                chunk_id = Utils.sha256(chunk)
                if self.ledger.is_duplicate(chunk_id):
                    continue
                chunks.append({
                    "id": chunk_id,
                    "text": chunk,
                    "source": pdf_path 
                })
                
        return chunks
    def get_page_wiki(self,url):
        try:
            res=requests.get(url,headers=self.headers,timeout=10)
            if res.status_code!=200:
                print(f"Error: Status {res.status_code}")
                return []
        except Exception as e:
            print(f"Error fetching page: {e}")
            return []
        soup=BeautifulSoup(res.text,"html.parser")
        content = soup.find("div", {"id": "bodyContent"})
        if not content:
            return []   
        for tag in content.select("script, style, table, .reflist, .mw-editsection, .infobox, .reference"):
            tag.decompose()
        chunks = []
        for p in content.find_all("p"):
            text = Utils.clean_text(p.get_text())
            text = Utils.chunk_text(text)
            if text:
                for chunk in text:
                    chunk_id = Utils.sha256(chunk)
                    if self.ledger.is_duplicate(chunk_id):
                        continue
                    chunks.append({
                        "id": chunk_id,
                        "text": chunk,
                        "source": url
                })
        return chunks
if __name__=="__main__":
    scrapper = Scraper()
    data = scrapper.get_page_wiki("https://en.wikipedia.org/wiki/Visual_snow_syndrome")
    for item in data:
        print(item)