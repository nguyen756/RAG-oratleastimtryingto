import hashlib
import html
import re
class Utils:
    @staticmethod
    def sha1(text, length=12):
        text=str(text)
        h= hashlib.sha1(text.encode("utf-8")).hexdigest()
        return h[:length]
    @staticmethod
    def clean_text(text):
        if not text:
            return ""
        text=str(text)
        text = html.unescape(text)
        text = text.replace("\xa0", " ")
        text = re.sub(r"\s+", " ", text).strip()
        return text
    @staticmethod
    def chunk_text(text, chunk_size=250,overlap=30)->list:
        if not text:
            return []
        text=str(text)
        start=0
        text_length=len(text)
        chunks=[]
        while start<text_length:
            end=start+chunk_size
            chunk=text[start:end]
            chunks.append(chunk)
            start = end - overlap
        return chunks
       