# # backend/main.py
from fastapi import FastAPI, UploadFile, File
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional ,Any
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

import subprocess
from pathlib import Path

from threading import Thread,Event
import time
from collections import deque
from pydantic import BaseModel
from fastapi import Query
import hashlib
import socket
import asyncio
import sys

from fastapi.middleware.cors import CORSMiddleware
import random

from InferenceManager.runInferenceInBatches import run_batch_inference_concurrently

from Backend.processMyActivity import extract_queries

from Backend.google_snapshot import fetch_google_snapshot
import uvicorn

import logging


logger = logging.getLogger("uvicorn")

def print(*args, **kwargs):
    """Redirect print() to Uvicorn’s logger"""
    msg = " ".join(map(str, args))
    logger.info(msg)



load_dotenv()
    
MYACTIVITY_JSON_FILE = os.getenv("MYACTIVITY_JSON_FILE","")

stop_event = Event()  # 👈 shared flag to stop worker loop
worker_thread = Thread()
DATABASE_URL: str = ""
engine: Any = None



DEVICE_CACHE: dict[str, int] = {} # fingerprint -> device_id

def make_fingerprint(user: str, name: str, platform: str, browser: str) -> str:
    raw = f"{user}:{name}:{platform}:{browser}"
    return hashlib.sha256(raw.encode()).hexdigest()


app = FastAPI(title="Internet Usage Tracker")


# ---------- CORS SETUP ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- MODELS ----------

class Device(SQLModel, table=True):  # type: ignore[misc]
    id: Optional[int] = Field(default=None, primary_key=True)

    # Auto-detected from extension (Option A)
    fingerprint: str  # UUID generated and persisted by extension
    platform: str     # e.g. "MacOS", "Windows", "Linux"
    browser: str      # e.g. "Chrome-124.0.0"

    # User-supplied info (Option B)
    device_name: str         # friendly name: "My MacBook Pro"
    user_name: str         # logical owner (could be your username, or account name)

    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_seen: Optional[str] = None  # updated whenever a query comes in


class SearchEvent(SQLModel, table=True):  # type: ignore[misc]
    id: Optional[int] = Field(default=None, primary_key=True)
    query: str
    timestamp: datetime
    category: Optional[str] = None  # to be filled by inference
    device_id: Optional[int] = Field(default=None, foreign_key="device.id")



# ---- Queue and worker ----
queue = deque()
MIN_BATCH_SIZE = 100
MAX_WAIT_TIME = 10  # seconds

def inference_worker(stop_event: Event):
    """Continuously checks queue and processes batches."""
    while not stop_event.is_set():
        if len(queue) >= MIN_BATCH_SIZE:
            batch = [queue.popleft() for _ in range(MIN_BATCH_SIZE)]
            print(f"🧠 Processing new batch of size {len(batch)}")
            try:
                # if process_batch is async, run it in the event loop thread
                asyncio.run(process_batch(batch))
            except Exception as e:
                print(f"❌ Error while processing batch: {e}")
        else:
            time.sleep(1)  # sleep a bit
            # Optional: if queue has items but MAX_WAIT_TIME exceeded, process anyway
            
    print("👋 Inference worker shutting down gracefully.")

async def process_batch(batch):
    """Send batch to InferenceManager and update DB."""
    temp_file = Path("temp_batch.json")
    output_file = Path("classified_temp.json")
    
    try:
        data = {"queries": batch}
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=2)  

        # Call your InferenceManager
        await run_batch_inference_concurrently(temp_file, output_file, "InferenceManager/prompts/system_prompt.txt")

        # Load classified results and save to DB (similar to /events/push/ logic)
        with open(output_file, "r") as f:
            data = json.load(f)

        classified_events = (
            data.get("event") or
            data.get(f"Filtered_queries", []) or
            next(iter(data.values()), [])
        )

        newEntries = []
        with Session(engine) as session:
            for entry in classified_events:
                query = entry.get("query")
                timestamp_str = entry.get("timestamp")
                category = entry.get("category")
                device_id = entry.get("device_id")
                if not query or not timestamp_str:
                    continue

                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                ev = SearchEvent(
                    query=query,
                    timestamp=timestamp,
                    device_id=device_id, 
                    category=category
                )
                session.add(ev)
                newEntries.append(ev)
            session.commit()
            print(f"✅ Added {len(newEntries)} search events into the DB.")
    finally:
        # Always clean up temp files, success or fail
        if temp_file.exists():
            os.remove(temp_file)
        if output_file.exists():
            os.remove(output_file)
# ---------- DB INIT ----------

async def init_db() -> None:
    db_path = ""
    if DATABASE_URL.startswith("sqlite:///"):
        db_path = DATABASE_URL.replace("sqlite:///", "", 1)
    else : raise OSError("Database Url not in the expected sqlalchemy schema")
    
    if db_path and not os.path.exists(db_path):
        extract_queries(MYACTIVITY_JSON_FILE,"queries_extracted.json")
        # Define seed paths
        input_file = Path("queries_extracted.json")
        output_file = Path("queries_classified.json")
        prompt_file = Path("InferenceManager/prompts/system_prompt.txt")
        
        try:
            
            print("📀 Creating new DB...")
            SQLModel.metadata.create_all(engine)

            # Ensure input file exists (could be dummy queries if you want)
            if not input_file.exists():
                with open(input_file, "w") as f:
                    json.dump({"queries": []}, f)   # or provide seed data here

            # 1️⃣ Run InferenceManager in-process
            print("🤖 Running InferenceManager to classify initial queries...")
            await run_batch_inference_concurrently(input_file, output_file, prompt_file)

            if not output_file.exists():
                raise FileNotFoundError("❌ InferenceManager output file not found!")

            # 2️⃣ Load results
            print("📥 Populating DB from classified output...")
            with open(output_file, "r") as f:
                data = json.load(f)

            classified_events = (
                data.get("event") or
                data.get(f"Filtered_queries", []) or
                next(iter(data.values()), [])
            )

            imported = []
            with Session(engine) as session:
                for entry in classified_events:
                    query = entry.get("query")
                    timestamp_str = entry.get("timestamp")
                    category = entry.get("category")
                    if not query or not timestamp_str:
                        continue

                    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    ev = SearchEvent(
                        query=query,
                        timestamp=timestamp,
                        device_id=1,  # 🔧 placeholder, can pull from DEVICE_CACHE
                        category=category
                    )
                    session.add(ev)
                    imported.append(ev)
                session.commit()

            print(f"✅ Imported {len(imported)} search events into the DB.")
        finally : 
            # Always clean up temp files, success or fail
            if input_file.exists():
                os.remove(input_file)
            if output_file.exists():
                os.remove(output_file)

    else:
        print("📂 Using existing DB...")


# ---------- ROUTES ----------

def validate_environment() -> None:
    """Validate that required environment variables are set."""
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise OSError("OPENAI_API_KEY not set in environment or .env file")
    model = os.getenv("MODEL_NAME")
    if not model:
        raise OSError("model name  not specified")
    myactivity_json_file = os.getenv("MYACTIVITY_JSON_FILE")
    if not myactivity_json_file:
        raise OSError("my activity json file  not specified")
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url or db_url.strip()=="":
        db_url = f"sqlite:///{os.getcwd()}/usage.db"
        os.environ["DATABASE_URL"] = db_url 
        print(f"DEBUG: ⚠️ No DATABASE_URL provided, defaulting to {db_url}")


    # Optional: if sqlite, check if the file exists (strip prefix)
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "", 1)
        if db_path and not os.path.exists(db_path):
            print(f"⚠️ Database file not found at {db_path}, will create new one.")

    
    print("✅ Environment validation passed")
    
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't need to be reachable
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

@app.on_event("startup")
async def on_startup() -> None:
    global engine,DATABASE_URL
    validate_environment()
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    engine = create_engine(DATABASE_URL, echo=True)
    await init_db()
    with Session(engine) as session:
        devices = session.exec(select(Device)).all()
        for d in devices:
            DEVICE_CACHE[d.fingerprint] = d.id
        print(f"✅ Loaded {len(DEVICE_CACHE)} devices into cache")
    # Start worker thread
    global stop_event,worker_thread
    stop_event = Event()
    worker_thread = Thread(target=inference_worker,args=(stop_event,), daemon=True)
    worker_thread.start()
    ip = get_local_ip()
    port = 8000  # or whatever port your backend uses
    print(f"🚀 Backend running at: http://{ip}:{port}")
    print(f"Enter this url, right here 👉 http://{ip}:{port} 👈 in your frontend app to connect to backend. ")

@app.on_event("shutdown")
def on_shutdown():
    print("🛑 Shutdown signal received. Stopping worker...")
    stop_event.set()          # Signal the worker to stop
    worker_thread.join(5.0)   # Wait up to 5 seconds
    print("✅ Worker stopped.")
    
@app.get("/ping")
async def ping():
    return {"message": "pong", "status": "ok"}

class DeviceValidationRequest(BaseModel):
    device_id: int

@app.post("/validate-device/")
def validate_device(request: DeviceValidationRequest):
    """
    Validates if a device_id exists in the current database.
    Returns validation status to help extensions determine if re-registration is needed.
    """
    with Session(engine) as session:
        device = session.exec(
            select(Device).where(Device.id == request.device_id)
        ).first()
        
        if device:
            # Device exists, also check if it's in cache
            if request.device_id not in DEVICE_CACHE.values():
                # Device exists in DB but not in cache, add it back
                DEVICE_CACHE[device.fingerprint] = device.id
                print(f"✅ Restored device {device.id} to cache")
            
            return {
                "status": "valid", 
                "device_id": request.device_id,
                "device_info": {
                    "user_name": device.user_name,
                    "device_name": device.device_name
                }
            }
        else:
            # Device doesn't exist in database
            print(f"❌ Device {request.device_id} not found in database")
            return {
                "status": "invalid", 
                "reason": "device not found in database"
            }

class DeviceRegisterRequest(BaseModel):
    platform: str
    browser: str
    device_name: str
    user_name: str


@app.post("/devices/")
def register_device(payload: DeviceRegisterRequest):
    # Generate deterministic fingerprint
    fingerprint = make_fingerprint(payload.user_name, payload.device_name, payload.platform, payload.browser)

    # Check in cache first (fast path)
    if fingerprint in DEVICE_CACHE:
        return {"device_id": DEVICE_CACHE[fingerprint]}

    with Session(engine) as session:
        # Check DB if fingerprint already exists
        existing = session.exec(
            select(Device).where(Device.fingerprint == fingerprint)
        ).first()

        if existing:
            DEVICE_CACHE[fingerprint] = existing.id
            return {"device_id": existing.id}

        # Create new device
        device = Device(
            device_name=payload.device_name,
            user_name=payload.user_name,
            platform=payload.platform,
            browser=payload.browser,
            fingerprint=fingerprint
        )
        session.add(device)
        session.commit()
        session.refresh(device)

        if device.id is None:
            raise RuntimeError("Device ID is None after commit/refresh — something went wrong")
        # Update cache
        DEVICE_CACHE[fingerprint] = device.id
        print(f"✅ Registered New Device")
        return {"device_id": device.id}


class EventRequest(BaseModel):
    query: str
    timestamp: str
    device_id: int

@app.post("/events/")
def push_event(event: EventRequest):
    if event.device_id not in DEVICE_CACHE.values():
        return {"status": "error", "reason": "unregistered device"}
    print(f"queued {event.query}")
    queue.append(event.model_dump())
    return {"status": "queued", "queue_size": len(queue)}

@app.get("/analytics/")
def get_analytics(period: str = Query("day", regex="^(day|week|month|year)$")) -> dict[str, Any]:
    """
    Returns query counts and category distribution for a given period.
    Period can be: day, week, month, year.
    """
    now = datetime.utcnow()
    if period == "day":
        start_time = now - timedelta(days=1)
    elif period == "week":
        start_time = now - timedelta(weeks=1)
    elif period == "month":
        start_time = now - timedelta(days=30)
    elif period == "year":
        start_time = now - timedelta(days=365)

    with Session(engine) as session:
        results = session.exec(
            select(SearchEvent)
            .where(SearchEvent.timestamp >= start_time)
        ).all()

        total_queries = len(results)

        # Count by category
        category_counts = {}
        for event in results:
            cat = event.category or "uncategorized"
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "period": period,
            "total_queries": total_queries,
            "category_distribution": category_counts,
        }

# ---------- RANDOM QUERY ENDPOINT ----------

TAXONOMY_CATEGORIES = [
    "Lexis",
    "History",
    "Biography",
    "Science",
    "Technology",
    "Culture",
    "Society",
    "Health",
    "Gooning",
    "Miscellaneous"
]

# Cache & Cursor trackers
CATEGORY_CACHE: dict[str, list[SearchEvent]] = {}
CATEGORY_CURSOR: dict[str, int] = {}

@app.get("/random-query")
def get_random_query(
    category: str = Query(...),
    limit: int = Query(100),
    force_refresh: bool = Query(False)
) -> list[str] : 
    """
    Returns next `limit` SearchEvent items in cyclic order for the given category.
    Only refetches from DB when:
    - cache is empty,
    - fully cycled, or
    - force_refresh=True
    """
    key = category

    # Initialize defaults
    if key not in CATEGORY_CURSOR:
        CATEGORY_CURSOR[key] = 0
    if key not in CATEGORY_CACHE:
        CATEGORY_CACHE[key] = []

    # Check if we need to refetch
    cache_empty = len(CATEGORY_CACHE[key]) == 0
    fully_cycled = CATEGORY_CURSOR[key] == 0 and not cache_empty
    
    if cache_empty or fully_cycled or force_refresh:
        with Session(engine) as session:
            events = session.exec(
                select(SearchEvent)
                .where(SearchEvent.category == key)
                .order_by(SearchEvent.id)
            ).all()

        CATEGORY_CACHE[key] = events
        CATEGORY_CURSOR[key] = 0

    all_events = CATEGORY_CACHE[key]

    if not all_events:
        return []

    start = CATEGORY_CURSOR[key]
    end = min(start + limit, len(all_events))
    selected = all_events[start:end]

    # Move cursor; if we reached the end, reset to 0 to trigger refetch next time
    if end >= len(all_events):
        CATEGORY_CURSOR[key] = 0
    else:
        CATEGORY_CURSOR[key] = end

    return [s.query for s in selected]

async def get_random_query_with_snapshots(
    category: str = Query(...),
    limit: int = Query(100),
    force_refresh: bool = Query(False)
) -> list[dict[str, str]] : 
    """
    Returns next `limit` SearchEvent items in cyclic order for the given category.
    Only refetches from DB when:
    - cache is empty,
    - fully cycled, or
    - force_refresh=True
    """
    key = category

    # Initialize defaults
    if key not in CATEGORY_CURSOR:
        CATEGORY_CURSOR[key] = 0
    if key not in CATEGORY_CACHE:
        CATEGORY_CACHE[key] = []

    # Check if we need to refetch
    cache_empty = len(CATEGORY_CACHE[key]) == 0
    fully_cycled = CATEGORY_CURSOR[key] == 0 and not cache_empty
    
    if cache_empty or fully_cycled or force_refresh:
        with Session(engine) as session:
            events = session.exec(
                select(SearchEvent)
                .where(SearchEvent.category == key)
                .order_by(SearchEvent.id)
            ).all()

        CATEGORY_CACHE[key] = events
        CATEGORY_CURSOR[key] = 0

    all_events = CATEGORY_CACHE[key]

    if not all_events:
        return []

    start = CATEGORY_CURSOR[key]
    end = min(start + limit, len(all_events))
    selected = all_events[start:end]

    # Move cursor; if we reached the end, reset to 0 to trigger refetch next time
    CATEGORY_CURSOR[key] = 0 if end >= len(all_events) else end
    
    # Concurrently fetch Google snapshots for each query
    tasks = [fetch_google_snapshot(s.query) for s in selected]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    enriched = []
    for i in range(len(selected)):
        s = selected[i]
        r = results[i]

        if isinstance(r, Exception):
            print(f"❌ Error fetching snapshot for {s.query}: {r}")
            enriched.append({
                "query": s.query,
                "snapshot": None,
                "html": None
            })
        else:
            enriched.append({
                "query": s.query,
                "snapshot": r.get("snapshot") if isinstance(r, dict) else None,
                "html":r.get("html") if isinstance(r, dict) else None
            })

    return enriched

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)