import os
import re
import json
import streamlit as st
from mistralai import Mistral, UserMessage

st.set_page_config(page_title="Mistral Chatbot", layout="wide")


def get_api_key() -> str:
    try:
        if "MISTRAL_API_KEY" in st.secrets:
            return str(st.secrets["MISTRAL_API_KEY"]).strip()
    except Exception:
        pass
    return os.getenv("MISTRAL_API_KEY", "").strip()

API_KEY = get_api_key()
if not API_KEY:
    st.error(
        "Missing API key.\n\n"
        "Add it in one of these ways:\n"
        "1) Create .streamlit/secrets.toml with: MISTRAL_API_KEY = \"your_key\"\n"
        "2) Set environment variable MISTRAL_API_KEY\n"
    )
    st.stop()

client = Mistral(api_key=API_KEY)
MODEL = "mistral-small-latest"

# ============================================================
# Helpers
# ============================================================
def mistral_chat(prompt: str, is_json: bool = False) -> str:
    msgs = [UserMessage(content=prompt)]
    try:
        if is_json:
            r = client.chat.complete(
                model=MODEL,
                messages=msgs,
                response_format={"type": "json_object"},
            )
        else:
            r = client.chat.complete(model=MODEL, messages=msgs)
    except TypeError:
        r = client.chat.complete(model=MODEL, messages=msgs)
    return r.choices[0].message.content

def clean_json(txt: str) -> str:
    return txt.replace("```json", "").replace("```", "").strip()

# ============================================================
# Prompts + KB
# ============================================================
ALLOWED_CATEGORIES = [
    "card arrival",
    "change pin",
    "exchange rate",
    "country support",
    "cancel transfer",
    "charge dispute",
    "customer service",
]

CLASSIFY_PROMPT = """
You are a bank customer service bot.
Classify the bank inquiry into ONE category only:
card arrival
change pin
exchange rate
country support
cancel transfer
charge dispute
customer service

Return ONLY the category text. No explanations.

Inquiry: {q}
Category:
"""

KB = {
    "card arrival": "Track delivery in Cards > Track delivery. Request replacement if overdue.",
    "change pin": "Go to Cards > Manage card > Change PIN.",
    "exchange rate": "Exchange rate depends on network rate plus bank fee. Tell me the currencies.",
    "country support": "Most countries are supported. Tell me your destination.",
    "cancel transfer": "If pending, cancel in Transfers > Activity.",
    "charge dispute": "Open transaction > Dispute charge. Provide date, merchant, and reason.",
    "customer service": "Tell me your issue and I will guide you."
}

EMAIL_FACTS = """
30-year fixed-rate: interest rate 6.403%, APR 6.484%
15-year fixed-rate: interest rate 5.705%, APR 5.848%
"""

GREETINGS = {"hi", "hello", "hey", "yo", "good morning", "good afternoon", "good evening"}

def normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())

def parse_category(raw: str) -> str:
    r = normalize_text(raw)

    # first line only (often best)
    first_line = r.splitlines()[0].strip()

    # direct match
    if first_line in ALLOWED_CATEGORIES:
        return first_line

    # search any allowed category inside the output
    for cat in ALLOWED_CATEGORIES:
        if cat in r:
            return cat

    return "customer service"

def classify_intent(inquiry: str) -> str:
    q = normalize_text(inquiry)

    # Heuristic: very short / greetings -> customer service
    if len(q.split()) <= 2 or q in GREETINGS:
        return "customer service"

    try:
        raw = mistral_chat(CLASSIFY_PROMPT.format(q=inquiry))
        return parse_category(raw)
    except Exception:
        return "customer service"

# ============================================================
# Session state
# ============================================================
if "chat_history" not in st.session_state:
    # each item: {"role":"user"/"assistant", "text":"...", "cat": "optional"}
    st.session_state.chat_history = []

if "pending_text" not in st.session_state:
    st.session_state.pending_text = ""

if "draft_version" not in st.session_state:
    st.session_state.draft_version = 0

def bump_draft():
    st.session_state.draft_version += 1

# ============================================================
# Sidebar: Lab Tools
# ============================================================
st.sidebar.title("Lab Tools")

with st.sidebar.expander("Classification", expanded=False):
    txt = st.text_area("Inquiry", "Does your card work in Germany?", height=90)
    if st.button("Run Classification", key="tool_classify"):
        cat = classify_intent(txt)
        st.success(cat)

with st.sidebar.expander("JSON Extraction", expanded=False):
    notes = st.text_area(
        "Medical Notes",
        "60 year old male smoker diagnosed with diabetes weight 210 lbs",
        height=120
    )
    if st.button("Extract JSON", key="tool_json"):
        out = mistral_chat(
            f"Extract age, gender, diagnosis, weight, smoking as JSON from:\n{notes}",
            is_json=True
        )
        st.code(out, language="json")
        try:
            st.json(json.loads(clean_json(out)))
        except Exception:
            st.warning("Invalid JSON returned. Try again.")

with st.sidebar.expander("Email Reply", expanded=False):
    email = st.text_area("Email", "What is your 30-year APR and how is it compared to 15-year?", height=100)
    if st.button("Generate Email", key="tool_email"):
        prompt = f"""
You are a mortgage lender support bot.
Reply politely using only the facts below.
Sign as Lender Customer Support.

Facts:
{EMAIL_FACTS}

Email:
{email}
"""
        st.write(mistral_chat(prompt))

with st.sidebar.expander("Summarization", expanded=False):
    news = st.text_area("Newsletter", "Mistral partnered with Microsoft...", height=120)
    if st.button("Summarize", key="tool_sum"):
        st.write(mistral_chat(f"Summarize in 5-8 bullet points:\n\n{news}"))

# ============================================================
# Main: Chatbot UI (chat bubbles)
# ============================================================
st.title("Customer Support Chatbot")

left, right = st.columns([2, 1])

def choose_example(text: str):
    st.session_state.pending_text = text
    bump_draft()
    st.rerun()

with right:
    st.subheader("Quick Examples")

    examples = [
        "My card didn’t arrive. What should I do?",
        "I want to change my PIN.",
        "Does your card work in Germany?",
        "I need to cancel a transfer I just made.",
        "I was charged twice by a merchant.",
        "What exchange rate will I get for EUR to QAR?"
    ]

    for i, ex in enumerate(examples):
        st.button(
            ex,
            key=f"ex_{i}",
            use_container_width=True,
            on_click=choose_example,
            args=(ex,)
        )

with left:
    # Render chat history as bubbles
    for item in st.session_state.chat_history:
        if item["role"] == "user":
            with st.chat_message("user"):
                st.markdown(item["text"])
        else:
            with st.chat_message("assistant"):
                cat = item.get("cat", "")
                if cat:
                    st.caption(f"Category: {cat}")
                st.markdown(item["text"])

    st.divider()

    # Fresh widget key when we need to paste/clear
    draft_key = f"draft_{st.session_state.draft_version}"

    default_val = st.session_state.pending_text
    if st.session_state.pending_text:
        st.session_state.pending_text = ""

    # Input in a form (predictable send)
    with st.form("chat_form", clear_on_submit=False):
        msg = st.text_input("Message", value=default_val, key=draft_key, placeholder="Type here...")
        send = st.form_submit_button("Send")

    col1, col2 = st.columns([1, 1])
    if col2.button("Clear", use_container_width=True):
        st.session_state.chat_history = []
        bump_draft()
        st.rerun()

    if send and msg.strip():
        inquiry = msg.strip()
        cat = classify_intent(inquiry)
        guidance = KB.get(cat, KB["customer service"])

        prompt = f"""
You are a helpful bank support assistant.
Answer using ONLY the guidance below.
Keep it short and clear.

Guidance:
{guidance}

Customer question:
{inquiry}

Answer:
"""
        try:
            answer = mistral_chat(prompt).strip()
        except Exception:
            answer = guidance

        st.session_state.chat_history.append({"role": "user", "text": inquiry})
        st.session_state.chat_history.append({"role": "assistant", "text": answer, "cat": cat})

        bump_draft()
        st.rerun()
