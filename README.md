# Project-Nexora

This project is a prototype of an intelligent cross-sell assistant. It combines **Real-time Event Simulation**, **Retrieval-Augmented Generation (RAG)**,**LLM** and **Digital Channel Delivery** to provide personalized financial product recommendations based on customer's transaction behavior and risk profiles.

##  1. Installation & Setup

Follow these steps to get the agent running on your local machine.

### Prerequisites

* Python 3.10 or higher
* Pip (Python package manager)

### Step 1: Clone & Install Dependencies

```bash
# Install required libraries
pip install streamlit google-genai langchain-huggingface langchain-chroma pypdf twilio sentence-transformers

```

### Step 2: Generate API Keys

#### **A. Google Gemini AI Key**

1. Visit the [Google AI Studio](https://aistudio.google.com/).
2. Log in with your Google Account.
3. Click on **"Get API key"** and then **"Create API key in new project"**.
4. Copy this key; you will paste it into `main_agent.py`.

#### **B. Twilio Messaging Service**

1. Sign up/Log in to the [Twilio Console](https://www.twilio.com/console).
2. Locate your **Account SID** and **Auth Token** on the dashboard.
3. Go to **Messaging > Services** and click **"Create Messaging Service"**.
4. Follow the setup to get a **Messaging Service SID**.
5. Ensure you have a "Verified Caller ID" (your phone number) to receive SMS in trial mode.

### Step 3: Configure the Scripts

* Open `main_agent.py` and `app.py`.
* Replace the placeholder strings with your actual keys:
* `genai.Client(api_key="YOUR_GEMINI_KEY")`
* `TWILIO_SID`, `TWILIO_TOKEN`, and `TWILIO_SERVICE_SID`.



### Step 4: Seed the Knowledge Base

1. Under the folder named `bank_docs/`.
2. Drop your bank product PDFs (Loan terms, Insurance policies) into this folder.
3. Run the ingestion script to create the local Vector DB:

```bash
python ingest.py

```

---

##  2. Prototype Description

### Current Structure

The project is modularized to reflect the system architecture of a first stage-level of our Project Nexora:

* **`ingest.py`**: The ETL pipeline. It parses PDFs, chunks text, and stores embeddings in a local **ChromaDB** instance.
* **`main_agent.py`**: The core logic. It handles user profile matching, RAG retrieval, and the Gemini 2.5 Flash orchestration.
* **`app.py`**: The **Streamlit** frontend. It serves as the unified interface for "Push" simulations and "Pull" chat interactions.
* **`mock_data.json`**: Contains simulated user personas, including historic data and risk tolerances.
* **`interaction_logs.csv`**: Acts as the **Analytics Engine** database, tracking every "Accept" or "Dismiss" action, for future analysis of user's choices.

### Implementation Logic

1. **Event Detection (Push):** When a transaction is entered, the agent retrieves the user's risk profile and searches the Vector DB for products related to that spend.
2. **Smart Chat (Pull):** Users can ask open-ended questions. The system performs a similarity search in ChromaDB to provide grounded, compliant answers.
3. **Compliance Filter:** System prompts strictly instruct the LLM to cross-reference recommendations against the `risk_tolerance` found in the user profile.
4. **Omnichannel Delivery:** Upon user acceptance, the **Twilio API** triggers an SMS notification to the user's mobile device.

---

##  3. Important Technical Details

### The "Compliance Filter"

This prototype implements a "soft" compliance layer via **Prompt Engineering**(as a partial implementation of the logic). The LLM is given a System Instruction to never recommend a product with a risk rating higher than the user's tolerance (e.g., a "Conservative" user will not be pitched "Crypto" or "Aggressive Equities").

### Data Privacy (Simulated for prototype)

In accordance with banking standards, the prototype demonstrates PII (Personally Identifiable Information) protection by using `user_id` tokens rather than real names in the backend processing logs.

### Known Constraints

* **Local DB:** The ChromaDB is stored locally in the `./chroma_db` folder. Deleting this folder will require re-running `ingest.py`.
* **Twilio Trial:** If using a Twilio Trial account, you can only send SMS to your verified phone number for upto only 5 verified recipients.

##  4. Running the Demo

1. Start the UI: `streamlit run app.py`
2. Select a User (e.g., **USR_001** - Low Risk).
3. Simulate a high-value purchase.
4. Review the AI recommendation.
5. **Accept** the offer to receive a real-time SMS.
6. Toggle **"Show system interaction logs"** at the bottom to view the data audit trail.
7. Ask Nexora (Smart Chat) about any questions related to Loans, Insurance and Investment.

## 5.Demo Video
(https://www.youtube.com/watch?v=r3iQa_GfqzE)


