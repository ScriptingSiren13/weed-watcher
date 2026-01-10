from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from ultralytics import YOLO
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

# Load YOLO model only once
MODEL_PATH = Path("App/final_model.pt")
model = YOLO(MODEL_PATH)

# Initialize FastAPI app
app = FastAPI()

#  Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Basic health check
@app.get("/")
def read_root():
    return {"message": "Weed Detection backend is running."}

# Prediction endpoint
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    upload_dir = "backend/uploads"
    result_dir = "backend/results"
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(result_dir, exist_ok=True)

    # Save uploaded file
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Run inference
    results = model(file_path)

    # Save result image with bounding boxes
    result_image_path = os.path.join(result_dir, file.filename)
    results[0].save(filename=result_image_path)

    # Extract predictions
    predictions = []
    boxes = results[0].boxes
    if boxes is not None:
        for box in boxes:
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            xyxy = box.xyxy[0].tolist()
            predictions.append({
                "class_id": cls_id,
                "confidence": round(conf, 3),
                "box": [round(x, 2) for x in xyxy]
            })

    return {
        "filename": file.filename,
        "detections": predictions,
        "image_url": f"/results/{file.filename}",
        "message": "Inference completed successfully." if predictions else "No weeds detected."
    }

# Serve saved result image to frontend
@app.get("/results/{filename}")
def get_result_image(filename: str):
    file_path = os.path.join("backend/results", filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type="image/jpeg")
    return {"error": "File not found"}



# Mount the "backend/results" folder at the "/results" URL path
app.mount("/results", StaticFiles(directory="backend/results"), name="results")

