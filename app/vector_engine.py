import json
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = faiss.IndexFlatL2(self.model.get_sentence_embedding_dimension())
        self.metadata = []

    def embed(self, data_batch):
        texts = [item["text"] for item in data_batch]
        vectors = self.model.encode(texts)
        self.index.add(np.array(vectors).astype('float32'))
        self.metadata.extend(data_batch)
        print(f"Added {len(data_batch)} items. Total items: {len(self.metadata)}")
        
        # 4. Save everything to disk immediately
        self.save()
        
        print(f"Added {len(data_batch)} items to the index. Total items: {len(self.metadata)}")
    def save(self):
        # Save the math (FAISS)
        faiss.write_index(self.index, "data/vector_database.index")
        # Save the text (Metadata)
        with open("data/metadata.json", "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=4)
        print("Database and metadata successfully saved to /data folder.")
    def load(self):
        if os.path.exists("data/vector_database.index") and os.path.exists("data/metadata.json"):
            self.index = faiss.read_index("data/vector_database.index")
            with open("data/metadata.json", "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            print(f"Loaded existing database with {len(self.metadata)} items.")
        else:
            print("No existing database found in /data. Starting fresh.")
    def search(self,query_text,top_k=1):
        print(f"Searching for: {query_text}")
        query_vector = self.model.encode([query_text]).astype('float32')
        distances, indices = self.index.search(query_vector, top_k)
        results=[]
        for i, idx in enumerate(indices[0]):
            if not idx == -1:
                match = self.metadata[idx]
                match['score']=distances[0][i]
                results.append(match)
        # print(winner['text'])
        return results
        
    
if __name__=="__main__":
    engine = Embedder()
    engine.load()
    # engine = Embedder(model_name="text-embedding-3-small")
    # engine = Embedder(model_name="embed-english-v3")
    if len(engine.metadata) == 0:
        data = [
            {'id': '2dd12f86e2f5', 'text': 'Visual snow syndrome (VSS) is an uncommon neurological condition...', 'source': 'wiki'},
            {'id': 'f997c979a838', 'text': 'Other common symptoms are palinopsia, enhanced entoptic phenomena...', 'source': 'wiki'}
        ]
        engine.embed(data)
    engine.embed(data)
    print(engine.search("what is common headaches?"))