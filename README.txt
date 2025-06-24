# Quasivo AI Interview App

A Streamlit-based web app for conducting AI/ML technical interviews.

This app allows reviewers to:
- Paste or upload a job description and candidate resume
- Automatically generate 5 custom interview questions using Gemini API
- Capture candidate answers
- Use Gemini API to score answers on a 1-10 scale
- Save results as JSON locally

## Features
- Dynamic question generation based on job description and resume
- Resume parsing (supports PDF and text input)
- AI-powered answer scoring (1-10 scale, no explanations)
- Local session save as JSON in `storage/` folder

## Tech Stack
- Python 3.x
- Streamlit
- Google Generative AI (Gemini API)
- PyPDF2 for PDF resume parsing
- dotenv for API key management

## Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
