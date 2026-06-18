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
            "Supabase is not configured. Add SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY to your .env file."
        )

    return create_client(supabase_url, supabase_key)


def save_resume_analysis(filename: str, sections: dict) -> None:
    payload = {
        "filename": filename,
        "professional_summary": sections.get("summary", "").strip(),
        "strengths": sections.get("strengths", "").strip(),
        "weaknesses": sections.get("weaknesses", "").strip(),
        "ats_analysis": sections.get("ats", "").strip(),
        "suggestions": sections.get("suggestions", "").strip(),
        "career_level": sections.get("career_level", "").strip(),
    }

    supabase = get_supabase_client()
    supabase.table(TABLE_NAME).insert(payload).execute()
