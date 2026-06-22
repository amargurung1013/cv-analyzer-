import asyncio
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils import extract_text_from_pdf
from graph import analyze_resume, extract_candidate_profile, extract_field, REVIEW_FIELDS
from database import save_resume_analysis

app = FastAPI()

# Static files - mount on both standard and prefix paths for sub-path routing compatibility
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/cv-analyzer-/static", StaticFiles(directory="static"), name="cv_analyzer_static")

# Templates
templates = Jinja2Templates(directory="templates")

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# In-memory store of the most recent analysis batches, keyed by batch id,
# so the dashboard page can render the same results without re-uploading.
BATCH_STORE: dict[str, list[dict]] = {}


@app.get("/")
@app.get("/cv-analyzer-")
@app.get("/cv-analyzer-/")
async def home(request: Request):
    prefix = "/cv-analyzer-" if request.url.path.startswith("/cv-analyzer-") else ""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"prefix": prefix}
    )


@app.api_route("/result", methods=["GET", "POST"])
@app.api_route("/cv-analyzer-/result", methods=["GET", "POST"])
async def analyze_cv(
    request: Request,
    resume: Annotated[list[UploadFile], File()] = None
):
    prefix = "/cv-analyzer-" if request.url.path.startswith("/cv-analyzer-") else ""

    # Redirect GET requests back home
    if request.method == "GET":
        return RedirectResponse(f"{prefix}/")

    # Prevent crash on empty file selection or None list
    if not resume or (len(resume) == 1 and resume[0].filename == ""):
        return RedirectResponse(url=f"{prefix}/", status_code=303)

    all_results = []

    for file in resume:

        try:

            # Save file
            safe_filename = Path(file.filename).name
            file_path = UPLOAD_DIR / safe_filename

            contents = await file.read()

            with open(file_path, "wb") as f:
                f.write(contents)

            # Extract text (blocking PDF parsing -> run off the event loop)
            resume_text = await asyncio.to_thread(extract_text_from_pdf, file_path)

            # Analyze with LLM (two focused async calls, won't block other requests)
            profile = await extract_candidate_profile(resume_text)
            analysis = await analyze_resume(resume_text)

            sections = {
                "name": profile.get("name", "") or "Unknown",
                "age": profile.get("age", "") or "Unknown",
                "education": profile.get("education", ""),
                "skills": profile.get("skills", ""),
                "sector": profile.get("sector", ""),
                "certifications": profile.get("certifications", "") or "Unknown",
            }

            for field in REVIEW_FIELDS:
                sections[field.lower()] = extract_field(analysis, field, REVIEW_FIELDS)

            # Save to database (wrapped in try-except for fault tolerance)
            try:
                await asyncio.to_thread(
                    save_resume_analysis,
                    filename=safe_filename,
                    sections=sections
                )
            except Exception as db_err:
                print(f"Database Save Error: {db_err}")

            # Convert score to float for sorting
            try:
                numeric_score = float(
                    sections["score"]
                    .replace("%", "")
                    .strip()
                )
            except:
                numeric_score = 0

            all_results.append(
                {
                    "filename": safe_filename,
                    "score_value": numeric_score,
                    "sections": sections
                }
            )

        except Exception as e:

            all_results.append(
                {
                    "filename": file.filename,
                    "score_value": 0,
                    "sections": {
                        "name": "Unknown",
                        "age": "Unknown",
                        "education": "",
                        "skills": "",
                        "sector": "",
                        "certifications": "Unknown",
                        "summary": f"Error: {str(e)}",
                        "strengths": "",
                        "weaknesses": "",
                        "ats": "",
                        "score": "0",
                        "suggestions": "",
                        "career_level": ""
                    }
                }
            )

    # Sort candidates by score descending
    all_results.sort(
        key=lambda x: x["score_value"],
        reverse=True
    )

    # Store this batch so the dashboard page can render it on request
    batch_id = uuid.uuid4().hex
    BATCH_STORE[batch_id] = all_results

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "results": all_results,
            "prefix": prefix,
            "batch_id": batch_id
        }
    )


@app.get("/dashboard/{batch_id}")
@app.get("/cv-analyzer-/dashboard/{batch_id}")
async def dashboard(request: Request, batch_id: str):
    prefix = "/cv-analyzer-" if request.url.path.startswith("/cv-analyzer-") else ""

    results = BATCH_STORE.get(batch_id)

    if results is None:
        return RedirectResponse(url=f"{prefix}/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "results": results,
            "prefix": prefix,
            "batch_id": batch_id
        }
    )