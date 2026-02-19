# RAG (From wiki for now, since I don't have any specific source of data I wanna use):
## Overview
This is a standard RAG (Retrieval-Augmented Generation) that extracts texts from Wikipedia, then chunks these texts with a specific length and overlap, then embeds to local vector for retrieval using Gemini LLM API.
## Pipeline Architecture
1. **Extraction (Scraper):** : Uses `BeautifulSoup` to target `bodyContent` `<div>` of scraped Wikipedia's texts.
   - Employs custom HTTP headers (Was trying to see if that could bypass fandom Wiki for personal uses, but failed).
   - Strips noise (tables, references, scripts) before processing.
2. **Transformation (Cleaning & Hashing):**
   - Applies a custom `clean_text()` utility to normalize unicode, fix HTML escaping, and remove non-breaking spaces.
   - Generates a `SHA-1`  for future deduplication and database updates.
3. **Embedding:**
   - Use `sentence-transformers/all-MiniLM-L6-v2` to embed these chunks into 384-dimensional vectors.
4. **Vector Storage & Retrieval:**
   - Powered by `FAISS` (Facebook AI Similarity Search).
   - Uses `IndexFlatL2` (Euclidean distance) to search for user queries.
5. **Augmented Generation:**
   - Use Gemini LLM API for the answer.

## Tech Stack
* **Python 3.12+**
* **Ingestion:** `requests`, `beautifulsoup4`, `lxml`
* **Vector Database:** `faiss-cpu`
* **Embeddings:** `sentence-transformers`
* **LLM Integration:** `openai` (SDK adapted for Gemini API)

## Current Status
- [x] Basic HTML Scraper
- [x] Text Normalization & Hashing
- [x] Local Vector Embedding
- [x] FAISS Indexing & Search
- [x] LLM API Integration
- [x] Implement Sliding Window Chunking
- [ ] Migrate to Scanned PDF OCR Pipeline (Future)
     

