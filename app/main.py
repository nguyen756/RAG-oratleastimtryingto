from scraper import Scraper
from vector_engine import Embedder
from openai import OpenAI
import os
from dotenv import load_dotenv

from fastapi import FastAPI, Response
import faiss
import uvicorn
from pydantic import BaseModel

app = FastAPI()
class QueryRequest(BaseModel):
    question: str
load_dotenv()
# def load_llm(prompt):
    # client = OpenAI(
    #     # This is the default and can be omitted
    #     api_key=os.getenv("GEMINI_API_KEY"),
    #     base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    # )
    # response = client.chat.completions.create(
    #     model="gemini-2.5-flash",
    #     messages=[
    #         {"role": "user", "content": prompt}
    #     ]
    # )
    # return response.choices[0].message.content
# def run():
#     scrapper = Scraper()
#     engine = Embedder(model_name="all-MiniLM-L6-v2")
#     data = scrapper.get_page("https://en.wikipedia.org/wiki/Visual_snow_syndrome")
#     engine.embed(data)
    # for item in data:
    #     print(item)
    # user_query = input("Ask a question about Visual Snow Syndrome: ")
    # retrieved =engine.search(user_query, top_k=1)   
    # if not retrieved:
    #     print("No relevant information found.")
    #     return
    # engine.search("Snow?")
    # for item in retrieved:
    #     print(f"Source: {item['source']}")
    #     print(f"Text: {item['text']}\n")
#     best_match = retrieved[0]
#     final_prompt = f"""You are a precise, technical AI assistant.
# Answer the user's question using ONLY the provided context below. 
# If the context does not contain the answer, reply exactly with: "I do not have enough information to answer this."

# CONTEXT:
# {best_match['text']}

# USER QUESTION: 
# {user_query}
# """
#     return final_prompt
    # print(final_prompt)




client = OpenAI(
        # This is the default and can be omitted
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
scrapper = Scraper()
engine = Embedder(model_name="all-MiniLM-L6-v2")
engine.load()

if len(engine.metadata) == 0:
    data = scrapper.get_pdf_text_plib("data/Hard Hit-2.pdf")
    # data = scrapper.get_pdf_text("data/Hard Hit-2.pdf")
    # data = scrapper.get_page_wiki("https://en.wikipedia.org/wiki/Visual_snow_syndrome")
engine.embed(data)

def llm_answer(prompt):
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

@app.get("/")
def check():
    return {"status":{"true"}}

@app.post("/query")
def ask(request:QueryRequest):
    retrieved = engine.search(request.question,top_k=1)
    if not retrieved:
        return 
    best_match = retrieved[0]
#    final_prompt = f"""You are a precise, technical AI assistant.
# Answer the user's question using ONLY the provided context below. 
# If the context does not contain the answer, reply exactly with: "I do not have enough information to answer this."

# CONTEXT:
# {best_match['text']}

# USER QUESTION: 
# {request.question}
# """
    final_prompt = f"""You are a precise, all knowing MMORPG player. Answer with the context of CONTEXT: precisely. But you don't overanalyze, straightforward
CONTEXT:
{best_match['text']}

USER QUESTION: 
{request.question}
"""
    answer = llm_answer(final_prompt)
    return {
        "question":request.question,
        "answer":answer
    }
@app.get("/health")
def health_check():
    return Response(status_code=200, content="OK")
if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
    # prompt = run()
    # print(load_llm(prompt))
