import os
import json
from google import genai
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Setup a Gemini Client
client = genai.Client(api_key="AIzaSyBKdJ685Etmj8RC9cjMHlfY0wnNQS75qcU")
MODEL_ID = "gemini-2.5-flash"

# Connecting to the existing Knowledge Base (ChromaDB)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# 3. Loading mock Customer Profiles
with open('mock_data.json', 'r') as f:
    customer_profiles = json.load(f)

# 4. Generating Recommedation using transaction event simulation

def get_recommendation(transaction_event):
    user_id = transaction_event['user_id']
    amount = transaction_event['data']['amount']
    description = transaction_event['data']['description']
    
    # Finding the particular user's profile
    user_profile = next((p for p in customer_profiles if p['user_id'] == user_id), None)
    if not user_profile:
        return "User profile not found."
    
    # Searching Vector DB for context of products available from the Bank
    docs = vector_db.similarity_search(description, k=2)
    product_context = "\n".join([d.page_content for d in docs])

    # Constructing the Prompt to ask LLM(Gemini)
    prompt_text = f"""
    SYSTEM: You are a helpful Financial Advisor for a Bank. 
    COMPLIANCE: Only recommend products that match the user's Risk Tolerance.
    
    USER PROFILE:
    - Monthly Income: {user_profile['historic_data']['avg_monthly_income']}
    - Risk Tolerance: {user_profile['risk_profiling']['tolerance']}
    - Financial Goal: {user_profile['questionnaire']['goals']}
    
    RECENT ACTIVITY:
    - User just spent ${amount} at {description}.
    
    AVAILABLE BANK PRODUCTS (Retrieved from DB):
    {product_context}
    
    TASK: Output a JSON object with keys: 'product_name' and 'recommendation' (the 2-sentence personalized message).
    Ensure the output is raw JSON without markdown formatting.
    """

    # 4. Generating Content
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt_text
    )
    
    # Cleaned and parsed JSON
    text_response = response.text.strip()
    if text_response.startswith("```json"):
        text_response = text_response[7:-3].strip()
    elif text_response.startswith("```"):
        text_response = text_response[3:-3].strip()
        
    try:
        return json.loads(text_response)
    except json.JSONDecodeError:
        # Fallback if JSON fails
        return {
            "product_name": "Bank Offer", 
            "recommendation": text_response
        }

# mock EVENT SIMULATION 
if __name__ == "__main__":
    sample_event = {
        "user_id": "USR_001",
        "data": {"amount": 250.00, "description": "International Flight Ticket"}
    }
    
    print("--- Generating Recommendation ---")
    recommendation = get_recommendation(sample_event)
    print(f"Recommendation for {sample_event['user_id']}:\n{recommendation}")