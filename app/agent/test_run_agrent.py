import os
import google.generativeai as genai
from dotenv import load_dotenv
from agent import check_status, calculate_mscs
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    tools=[check_status, calculate_mscs] 
)
chat = model.start_chat(enable_automatic_function_calling=True)
user_prompt = "My current ASPD is 9000 and my CSPD is 9500. Can you calculate what that actually does?"

print(f"User: {user_prompt}\n")
response = chat.send_message(user_prompt)
print(f"Agent Response:\n{response.text}")