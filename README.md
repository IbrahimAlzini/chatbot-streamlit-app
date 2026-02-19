# Mistral Customer Support Chatbot (Streamlit Lab)

This project is a Streamlit-based AI chatbot built using the **Mistral API**.  
It was developed as part of a university lab to demonstrate:

- Intent classification using LLMs  
- Knowledge-base grounded responses  
- JSON extraction and summarization  
- Streamlit UI integration  

The chatbot simulates a **bank customer support assistant**.

---

## Features

### AI Chatbot
- Detects customer intent (card arrival, PIN change, dispute, etc.)
- Uses a knowledge base for safe responses
- Real chat-style UI using Streamlit chat bubbles

### Lab Tools (Sidebar)
- Intent Classification tool  
- JSON extraction from text  
- Email response generator  
- Newsletter summarization  

### Secure API Key Handling
The API key is NOT stored in the repository.  
It is loaded from:

- `.streamlit/secrets.toml`  
or  
- Environment variable  

This keeps the key safe when uploading to GitHub.

---

## Project Structure
project/
│
├── app.py
├── requirements.txt
└── README.md

---

## How to Run Locally

### 1. Clone the repo

git clone https://github.com/IbrahimAlzini/chatbot-streamlit-app.git
cd chatbot-streamlit-app


---

### 2. Install dependencies

pip install -r requirements.txt


---

### 3. Add your Mistral API key

Create folder:

.streamlit


Create file:

.streamlit/secrets.toml


Add:

MISTRAL_API_KEY = "your_api_key_here"


---

### 4. Run the app

streamlit run app.py


The chatbot will open in your browser.

---

## Deploy on Streamlit Cloud

1. Upload repo to GitHub  
2. Go to https://share.streamlit.io  
3. Deploy your repo  
4. Add your API key in **App Settings → Secrets**

The key stays private and secure.

---

## Lab Learning Outcomes

This project demonstrates:

- Using Mistral LLM API in Python
- Prompt engineering for classification
- Building a Streamlit AI interface
- Handling secrets securely
- Creating a simple AI support system

---


## Author

Ibrahim Alzini  

