from dotenv import load_dotenv
import os
import re

from langchain_groq import ChatGroq

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.3-70b-versatile",
    temperature=0
)

PROFILE_FIELDS = ["NAME", "AGE", "EDUCATION", "SKILLS", "SECTOR", "CERTIFICATIONS"]
REVIEW_FIELDS = ["SUMMARY", "STRENGTHS", "WEAKNESSES", "ATS", "SCORE", "SUGGESTIONS", "CAREER_LEVEL"]


def extract_field(text: str, field: str, all_fields: list[str]) -> str:
    others = "|".join(f for f in all_fields if f != field)
    pattern = rf"{field}:\s*(.*?)(?:\n\s*(?:{others}):|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


async def extract_candidate_profile(resume_text: str) -> dict:

    prompt = f"""
You are an expert recruiter extracting structured candidate data.

Read the resume below and return ONLY the format shown, nothing else.

NAME:
<candidate full name, or Unknown if not found>

AGE:
<candidate age as a plain number if explicitly stated in the resume, otherwise Unknown>

EDUCATION:
<current or most recent institution and degree/program, one line>

SKILLS:
<comma-separated list of key skills, max 8>

SECTOR:
<the main industry/role sector the candidate is targeting, 2-4 words>

CERTIFICATIONS:
<Yes if the resume lists any certifications, otherwise No>

Resume:
{resume_text}

IMPORTANT:
- Do NOT add markdown or bold text.
- Do NOT explain anything outside the six fields above.
- Every field must be present, in this exact order, each on its own line followed by its value.
- AGE must be a plain number or the word Unknown, never invented.
- CERTIFICATIONS must be exactly Yes or No.
"""

    response = await llm.ainvoke(prompt)
    text = response.content

    return {
        field.lower(): extract_field(text, field, PROFILE_FIELDS)
        for field in PROFILE_FIELDS
    }


async def analyze_resume(resume_text: str) -> str:

    prompt = f"""
You are an expert ATS system and senior recruiter.

Analyze the following resume and return ONLY the format below.

SUMMARY:
<2-4 sentence professional summary>

STRENGTHS:
- point
- point
- point

WEAKNESSES:
- point
- point
- point

ATS:
<short ATS compatibility analysis>

SCORE:
<number between 0 and 100>

SUGGESTIONS:
- point
- point
- point

CAREER_LEVEL:
<Intern / Junior / Mid-Level / Senior / Lead>

Resume:
{resume_text}

IMPORTANT:
- Do NOT add markdown.
- Do NOT use bold text.
- Do NOT explain anything outside the sections.
- SCORE must contain only a number.
"""

    response = await llm.ainvoke(prompt)

    return response.content