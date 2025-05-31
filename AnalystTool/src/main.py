from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import datetime
from src.analyticstool import AnalyticsTools
from contextlib import asynccontextmanager

# Initialize scheduler
scheduler = BackgroundScheduler()

# Initialize analytics
analytics = AnalyticsTools()

# Function to run as a scheduled job
def run_weekly_report():
    analytics.weeklyReport(datetime(2025, 1, 27),datetime.now())
    print("Weekly Report updated:" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Schedule the function to run 4 times a day
scheduler.add_job(run_weekly_report, "cron", hour="0,6,12,18")  # Runs at 00:00, 06:00, 12:00, 18:00

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting scheduler...")
    scheduler.start()  # Start the scheduler when FastAPI starts
    yield  # Yield control back to FastAPI
    print("Shutting down scheduler...")
    scheduler.shutdown()  # Shutdown the scheduler when FastAPI stops

# Initialize FastAPI
app = FastAPI(lifespan=lifespan)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("DASHBOARD_URL")],  # Dashboard
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Define API endpoints
@app.get("/summary")
def get_weekly():
    summary = analytics.getSummary()
    return {"Summary": summary}

@app.get("/weeklychange")
def get_change():
    change = analytics.getWeeklyChange()
    return {"Change": change}

@app.get("/questions")
def aggregate():
    questions = analytics.getAggregate()
    return {"Questions": questions}

@app.get("/alive")
def update():
    return {"alive": "yes"}
