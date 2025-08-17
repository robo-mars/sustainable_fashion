from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json

import config
from image_analyzer import analyze_image_bytes
from watsonx_agent import call_orchestrate_skill


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

app = FastAPI(title="Fashion 4-Option Agent (Hackathon)")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        result = analyze_image_bytes(image_bytes)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/action")
async def action(
    action: str = Form(None),
    prompt: str = Form(None),
    file: UploadFile = File(None),
    item_name: str = Form(None),
    condition: str = Form(None),
    location: str = Form(None),
    color: str = Form(None),
    color_name: str = Form(None)
):
    img_bytes = await file.read() if file else None
    # Compose inputs
    inputs = {}
    if item_name:
        inputs["item_name"] = item_name
    if condition:
        inputs["condition"] = condition
    if color:
        inputs["color"] = color
    if color_name:
        inputs["color_name"] = color_name
    if location:
        try:
            inputs["location"] = json.loads(location)
        except Exception:
            inputs["location"] = {"raw": location}
    if prompt:
        inputs["prompt"] = prompt

    # If a custom prompt is provided and no action, use style skill as default
    skill_map = {
        "style": config.STYLE_SKILL_ID,
        "recycle": config.RECYCLE_SKILL_ID,
        "sell": config.SELL_SKILL_ID,
        "donate": config.DONATE_SKILL_ID
    }
    if action:
        skill_id = skill_map.get(action)
        if not skill_id:
            return JSONResponse({"error":"unknown action"}, status_code=400)
        resp = call_orchestrate_skill(skill_id, inputs, image_bytes=img_bytes)
        return JSONResponse({"action": action, "result": resp})
    elif prompt:
        # If only prompt, use style skill as default
        skill_id = config.STYLE_SKILL_ID
        resp = call_orchestrate_skill(skill_id, inputs, image_bytes=img_bytes)
        return JSONResponse({"action": "custom_prompt", "result": resp})
    else:
        return JSONResponse({"error": "No action or prompt provided."}, status_code=400)

@app.get("/api/health")
def health():
    return {"status":"ok"}

# Mount static files after all API routes
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
