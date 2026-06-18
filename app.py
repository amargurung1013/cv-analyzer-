from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pathlib import Path

from utils import extract_text_from_pdf
from graph import analyze_resume
from database import save_resume_analysis

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
@app.api_route("/analyze", methods=["GET", "POST"])
@app.api_route("/result", methods=["GET", "POST"])
async def analyze_cv(
    request: Request,
    resume: UploadFile | None = File(None)
):
    if request.method == "GET" or resume is None:
        return RedirectResponse(url="/")

    # CREATE UPLOADS FOLDER
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    # SAVE PDF
    safe_filename = Path(resume.filename).name
    file_path = upload_dir / safe_filename

    with open(file_path, "wb") as buffer:
        buffer.write(await resume.read())

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

    # SAVE ANALYSIS TO SUPABASE
    try:
        save_resume_analysis(safe_filename, sections)
    except Exception as error:
        print(f"Supabase save failed: {error}")

    # RETURN RESULT PAGE
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
           "filename": safe_filename,
           "sections": sections
        }
    )
