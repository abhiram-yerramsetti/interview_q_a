import os
import json
import requests
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import streamlit as st

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("❌ GEMINI_API_KEY not found. Please check your .env file.")
    st.stop()

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# Ensure storage folder exists
os.makedirs("storage", exist_ok=True)

# Gemini API helper
def call_gemini_api(prompt_text):
    payload = {
        "contents": [
            {"parts": [{"text": prompt_text}]}
        ]
    }
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"❌ API Error {response.status_code}: {response.text}")
        return None

# PDF parser
def parse_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    return text

# Streamlit UI
st.title("📝 Quasivo AI Interview App")

# Inputs
jd_text = st.text_area("Paste Job Description", height=200)
resume_text = st.text_area("Paste Resume Text", height=200)
uploaded_file = st.file_uploader("Or upload Resume as PDF", type="pdf")

if uploaded_file:
    resume_text = parse_pdf(uploaded_file)
    st.text_area("Extracted Resume Text", value=resume_text, height=200, disabled=True)

if st.button("Generate 5 Interview Questions"):
    if not jd_text.strip() or not resume_text.strip():
        st.warning("Please provide both JD and Resume text.")
    else:
        with st.spinner("Generating interview questions..."):
            prompt = (
                f"Based on the job description and résumé provided below, generate exactly 5 custom interview questions "
                f"that focus on how the candidate's experience and skills match the requirements of the job description. "
                f"These questions should assess the candidate’s suitability for the role. "
                f"Do not include analysis, commentary, or explanation — only list the 5 questions.\n\n"
                f"Job Description:\n{jd_text}\n\nRésumé:\n{resume_text}"
            )
            result = call_gemini_api(prompt)

        if result:
            text_output = result['candidates'][0]['content']['parts'][0]['text']
            questions = [line.strip() for line in text_output.split('\n') if line.strip()]
            st.session_state['questions'] = questions
            st.session_state['answers'] = [""] * len(questions)

if 'questions' in st.session_state:
    st.header("💬 Candidate Answers")
    for idx, q in enumerate(st.session_state['questions']):
        st.markdown(f"**Q{idx+1}: {q}**")
        st.session_state['answers'][idx] = st.text_area(
            f"Answer {idx+1}",
            value=st.session_state['answers'][idx],
            height=100
        )

    if st.button("Score Answers (1-10 scale)"):
        with st.spinner("Scoring answers..."):
            score_prompt = "Please score the following candidate answers on a scale of 1 to 10. Just provide the score for each without explanation or commentary.\n"
            for i, (q, a) in enumerate(zip(st.session_state['questions'], st.session_state['answers']), 1):
                score_prompt += f"Q{i}: {q}\nA: {a}\n"

            score_result = call_gemini_api(score_prompt)

        if score_result:
            score_text = score_result['candidates'][0]['content']['parts'][0]['text']
            st.subheader("🏆 Scoring Result")
            st.text(score_text)

            # Save session data
            session_data = {
                "job_description": jd_text,
                "resume": resume_text,
                "questions": st.session_state['questions'],
                "answers": st.session_state['answers'],
                "score_output": score_text
            }

            file_number = len(os.listdir("storage")) + 1
            filename = f"storage/session_{file_number}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            st.success(f"✅ Session saved as {filename}")
