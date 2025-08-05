import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from src.database.scripts.db_init import init_db
from src.routes import app_routes
from src.routes import event_routes
init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(app_routes.router, prefix="/api/app")
app.include_router(event_routes.router, tags=["Events"])


@app.get("/")
def read_root():
    return JSONResponse(content={"message": "Welcome to the Mini Audit Logger API!"})

@app.get("/health")
def health_check():
    return {"status": "ok"}

index_dir = "frontend"
if os.path.exists(index_dir):
    app.mount("/static", StaticFiles(
        directory=index_dir,
        html=True,
        check_dir=True
    ), name="static")
@app.get("/app")
def read_index():
    return FileResponse(f"{index_dir}/index.html")

