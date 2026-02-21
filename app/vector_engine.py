from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = faiss.IndexFlatL2(self.model.get_sentence_embedding_dimension())
        self.metadata = []

    def embed(self, json):
        texts = [item["text"] for item in json]
        vectors = self.model.encode(texts)
        self.index.add(np.array(vectors).astype('float32'))
        faiss.write_index(self.index, "vector_database.index")
        self.metadata.extend(json)
        
        print(f"Added {len(json)} items to the index. Total items: {len(self.metadata)}")
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
    # engine = Embedder(model_name="text-embedding-3-small")
    # engine = Embedder(model_name="embed-english-v3")
    data = [
        {'id': '2dd12f86e2f5', 'text': 'Visual snow syndrome (VSS) is an uncommon neurological condition in which the primary symptom is persistent flickering white, black, transparent, or colored dots across the whole visual field. It is distinct from the symptom of visual snow itself, which can also have several other causes; these cases are referred to as "VSS mimics."', 'source': 'https://en.wikipedia.org/wiki/Visual_snow_syndrome'},
        {'id': 'f997c979a838', 'text': 'Other common symptoms are palinopsia, enhanced entoptic phenomena, photophobia, and tension headaches. The condition is typically always present and has no known cure, as viable treatments are still under research. Astigmatism, although not presumed connected to these visual disturbances, is a common comorbidity. Migraines and tinnitus are common comorbidities that are both associated with a more severe presentation of the syndrome.', 'source': 'https://en.wikipedia.org/wiki/Visual_snow_syndrome'}
    ]
    engine.embed(data)
    engine.search("what is common headaches?")