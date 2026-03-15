from urllib import parse
from scraper import Scraper
from vector_engine import Embedder
from openai import OpenAI
import os
from dotenv import load_dotenv
import numpy as np
import argparse
import json

from fastapi import FastAPI, Response
import faiss
import uvicorn
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from agent.agent import check_status, calculate_mscs, general_question

# Initialize FastAPI app
app = FastAPI()
class QueryRequest(BaseModel):
    question: str
load_dotenv()
# parse arguments for flexibility
base_dir = os.path.dirname(os.path.abspath(__file__))
default_pdf_path = os.path.normpath(os.path.join(base_dir, "..", "data", "Hard Hit-3.pdf"))

parser = argparse.ArgumentParser()
parser.add_argument("--data_path", type=str, default=default_pdf_path, help="Path to the PDF file to process")
parser.add_argument("--embedding_model", type=str, default="all-MiniLM-L6-v2", help="Name of the sentence transformer model to use for embeddings")
parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8080")), help="Port the FastAPI server should listen on")
args = parser.parse_args()

data_path = args.data_path
embedding_model = args.embedding_model
port = args.port


cache_encode = SentenceTransformer(embedding_model)
cache_index = faiss.IndexFlatL2(cache_encode.get_sentence_embedding_dimension())
cached_answers = []
MAX_CACHE_SIZE = 500
DISTANCE_THRESHOLD = 0.15


scrapper = Scraper()
engine = Embedder(model_name=embedding_model)
engine.load()
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate_mscs",
            "description": "Calculates Motion Speed and Cast Speed boosts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "aspd": {"type": "integer", "description": "Attack speed. Default to 0 if not mentioned."},
                    "cspd": {"type": "integer", "description": "Cast speed. Default to 0 if not mentioned."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "general_question",
            "description": "Searches the vector database for relevant information to answer general questions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {"type": "string"}
                },
                "required": ["search_query"]
            }
        }
    }
]

client = OpenAI(
        # This is the default and can be omitted
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        
    )

#data scarping and embedding
#if len(engine.metadata) == 0:
if not os.path.isfile(data_path):
    raise FileNotFoundError(
        f"PDF not found at '{data_path}'.\n" \
        f"Run the script from the project root or pass --data_path with the correct path.\n" \
        f"Current working directory: {os.getcwd()}"
    )
data = scrapper.get_pdf_text_plib(data_path)
    # data = scrapper.get_pdf_text("data/Hard Hit-2.pdf")
    # data = scrapper.get_page_wiki("https://en.wikipedia.org/wiki/Visual_snow_syndrome")
if len(data) > 0:
    engine.embed(data)


#answer generation
def llm_answer(prompt):
    messages = [
        {"role": "system", "content": "You are a precise Toram Online assistant. You have tools to calculate stats and search the game database. If the user asks about game mechanics, items, or lore, you MUST use the general_question tool to search the database. Assume skills are lv10."},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    response_message = response.choices[0].message
    if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
        tool_call = response_message.tool_calls[0]
            
        if tool_call.function.name == "calculate_mscs":
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                args = {}
            math_result = calculate_mscs(
            aspd=int(args.get("aspd", 0)), 
            cspd=int(args.get("cspd", 0))
            )
            return f"Agent Calculation: {math_result}"
        elif tool_call.function.name == "general_question":
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                args = {"search_query": prompt}
            retrieved = engine.search(args.get("search_query", prompt), top_k=1)
            
            if retrieved:
                return f"Database Result: {retrieved[0]['text']}"
            else:
                return "I searched the database but found no relevant information."
    return response_message.content

# API Endpoints
@app.get("/")
def check():
    return {"status": True}
@app.post("/query")
def ask(request:QueryRequest):
    query_vector = cache_encode.encode([request.question])[0]
    if cache_index.ntotal > 0:
        distances, indices = cache_index.search(np.array([query_vector]), 1)
        if distances[0][0] < DISTANCE_THRESHOLD:
            return {
                "question": request.question,
                "answer": cached_answers[indices[0][0]],
                "source": "cache"
            }
    answer = llm_answer(request.question)
#    final_prompt = f"""You are a precise, technical AI assistant.
# Answer the user's question using ONLY the provided context below. 
# If the context does not contain the answer, reply exactly with: "I do not have enough information to answer this."

# CONTEXT:
# {best_match['text']}

# USER QUESTION: 
# {request.question}
# """
    if cache_index.ntotal >= MAX_CACHE_SIZE:
        cache_index.reset()
        cached_answers.clear()

    cache_index.add(np.array([query_vector]))
    cached_answers.append(answer)
    return {
        "question":request.question,
        "answer":answer,
        "source": "new"
    }
@app.get("/health")
def health_check():
    return Response(status_code=200, content="OK")



if __name__=="__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=port)
