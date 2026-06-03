from dotenv import load_dotenv
import os

from langchain_groq import ChatGroq

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.3-70b-versatile"
)


def analyze_resume(resume_text):

    prompt = f"""
    You are a professional resume reviewer.

    Analyze this resume and respond ONLY in this exact format:

    SUMMARY:
    <professional summary>

    STRENGTHS:
    - point
    - point

    WEAKNESSES:
    - point
    - point

    ATS:
    <ATS analysis>

    SCORE:
    <number only>

    SUGGESTIONS:
    - point
    - point

    CAREER_LEVEL:
    <career level>

    Resume:
    {resume_text}
    """

    response = llm.invoke(prompt)

    return response.content