from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import shutil

from utils import extract_text_from_pdf
from graph import analyze_resume

app = FastAPI()

# STATIC FILES
app.mount("/static", StaticFiles(directory="static"), name="static")

# TEMPLATES
templates = Jinja2Templates(directory="templates")


# HOME PAGE
@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# ANALYZE RESUME
@app.post("/analyze")
async def analyze_cv(
    request: Request,
    resume: UploadFile = File(...)
):

    # CREATE UPLOADS FOLDER
    os.makedirs("uploads", exist_ok=True)

    # SAVE PDF
    file_path = f"uploads/{resume.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    # EXTRACT TEXT
    resume_text = extract_text_from_pdf(file_path)

    # AI ANALYSIS
    analysis = analyze_resume(resume_text)

    sections = {
        "summary": "",
        "strengths": "",
        "weaknesses": "",
        "ats": "",
        "score": "",
        "suggestions": "",
        "career_level": ""
    }

    current = None

    for line in analysis.splitlines():

        line = line.strip()

        if line.startswith("SUMMARY:"):
            current = "summary"
            continue

        elif line.startswith("STRENGTHS:"):
            current = "strengths"
            continue

        elif line.startswith("WEAKNESSES:"):
            current = "weaknesses"
            continue

        elif line.startswith("ATS:"):
            current = "ats"
            continue

        elif line.startswith("SCORE:"):
            current = "score"
            continue

        elif line.startswith("SUGGESTIONS:"):
            current = "suggestions"
            continue

        elif line.startswith("CAREER_LEVEL:"):
            current = "career_level"
            continue

        if current:
            sections[current] += line + "\n"

    # RETURN RESULT PAGE
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
           "filename": resume.filename, 
           "sections": sections
        }
    )

