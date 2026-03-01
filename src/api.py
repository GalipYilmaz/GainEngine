from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any
from src.data_manager import DataManager
from src.workout_engine import WorkoutEngine
from src.visualization import WorkoutVisualizer
from src.pdf_exporter import PDFExporter

# Create the FastAPI application instance
app = FastAPI(title="GainEngine API")

# Initialize the modules
data_manager = DataManager()
workout_engine = WorkoutEngine(data_manager)
visualizer = WorkoutVisualizer()
pdf_exporter = PDFExporter()

# Load the ML model
workout_engine.load_model()

# Mount static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Request Models
class WorkoutRequest(BaseModel):
    split_name: str
    equipment_profile: str
    volume_level: str = "Normal"

class SwapRequest(BaseModel):
    exercise_name: str
    equipment_profile: str
    current_day_exercises: List[str] = []

# Helper Function: Converts profile string to equipment list
def get_equipment_list(profile: str) -> List[str]:
    all_eq = data_manager.get_unique_equipment()
    if profile == "Bodyweight":
        return ["body weight", "assisted"]
    elif profile == "Home Gym":
        return ["body weight", "assisted", "dumbbell", "band", "kettlebell", "medicine ball", "stability ball"]
    else: 
        return all_eq

# Endpoints
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/options")
def get_options():
    return {
        "splits": list(workout_engine.splits.keys()),
        "volumes": ["Low", "Normal", "High"]
    }

@app.post("/generate")
def generate_workout_endpoint(request: WorkoutRequest):
    eq_list = get_equipment_list(request.equipment_profile)
    
    weekly_plan = workout_engine.generate_workout_plan(
        split_name=request.split_name,
        equipment_list=eq_list,
        volume_level=request.volume_level
    )

    if not weekly_plan:
        raise HTTPException(status_code=404, detail="Could not generate a plan.")

    return weekly_plan

@app.post("/swap")
def swap_exercise_endpoint(request: SwapRequest):
    eq_list = get_equipment_list(request.equipment_profile)
    
    alternative = workout_engine.get_smart_alternative(
        exercise_name=request.exercise_name,
        equipment_list=eq_list,
        current_exercises=request.current_day_exercises
    )

    if not alternative:
        raise HTTPException(status_code=404, detail="No suitable alternative found.")

    return alternative

@app.post("/analyze")
def analyze_workout_endpoint(weekly_plan: Dict[str, Any]):
    chart_image = visualizer.generate_volume_chart(weekly_plan)
    return {"chart": chart_image}

@app.post("/export-pdf")
def export_pdf_endpoint(weekly_plan: Dict[str, Any]):
    file_path = pdf_exporter.generate_pdf(weekly_plan)
    return {"download_url": f"/{file_path}"}
