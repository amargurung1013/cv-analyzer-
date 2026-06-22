import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

TABLE_NAME = "resume_analyses"


def get_supabase_client() -> Client:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set."
        )

    return create_client(supabase_url, supabase_key)


def save_resume_analysis(
    filename: str,
    sections: dict
) -> None:

    try:

        score = float(
            sections.get("score", "0")
            .replace("%", "")
            .strip()
        )

    except ValueError:

        score = 0

    full_payload = {
        "filename": filename,
        "candidate_name": sections.get("name", "").strip(),
        "candidate_age": sections.get("age", "").strip(),
        "education": sections.get("education", "").strip(),
        "skills": sections.get("skills", "").strip(),
        "sector": sections.get("sector", "").strip(),
        "certifications": sections.get("certifications", "").strip(),
        "professional_summary": sections.get("summary", "").strip(),
        "strengths": sections.get("strengths", "").strip(),
        "weaknesses": sections.get("weaknesses", "").strip(),
        "ats_analysis": sections.get("ats", "").strip(),
        "suggestions": sections.get("suggestions", "").strip(),
        "career_level": sections.get("career_level", "").strip(),
        "score": score,
    }

    base_payload = {
        "filename": filename,
        "professional_summary": sections.get("summary", "").strip(),
        "strengths": sections.get("strengths", "").strip(),
        "weaknesses": sections.get("weaknesses", "").strip(),
        "ats_analysis": sections.get("ats", "").strip(),
        "suggestions": sections.get("suggestions", "").strip(),
        "career_level": sections.get("career_level", "").strip(),
    }

    supabase = get_supabase_client()

    attempts = [
        full_payload,
        {**base_payload, "score": score},
        base_payload,
    ]

    last_error = None

    for attempt_payload in attempts:
        try:
            response = supabase.table(TABLE_NAME).insert(attempt_payload).execute()
            print(f"Supabase insert OK: {response.data}")
            return
        except Exception as e:
            last_error = e
            print(f"Supabase insert failed with payload keys {list(attempt_payload.keys())}: {e}")

    raise last_error