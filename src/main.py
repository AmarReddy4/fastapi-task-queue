import json
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from .database import get_db, init_db
from .models import Job
from .schemas import JobCreate, JobListResponse, JobResponse, MessageResponse

VALID_JOB_TYPES = {"image_resize", "send_email", "generate_report", "data_export"}

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


def enqueue_job(job_id: str, job_type: str, payload: dict) -> None:
    """Enqueue a job to the Redis queue. Fails silently if Redis is unavailable."""
    try:
        import redis as redis_lib
        from rq import Queue

        conn = redis_lib.from_url(REDIS_URL)
        q = Queue(connection=conn)

        from .tasks import process_job

        q.enqueue(process_job, job_id, job_type, payload)
    except Exception:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Task Queue API",
    description="Async task processing API with Redis-backed job queue",
    version="0.1.0",
    lifespan=lifespan,
)


@app.post("/api/jobs", response_model=JobResponse, status_code=201)
def create_job(job_data: JobCreate, db: Session = Depends(get_db)):
    """Submit a new job for async processing."""
    if job_data.type not in VALID_JOB_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid job type. Must be one of: {', '.join(VALID_JOB_TYPES)}",
        )

    payload_json = json.dumps(job_data.payload)

    job = Job(type=job_data.type, payload=payload_json, status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)

    enqueue_job(job.id, job.type, job_data.payload)

    return job


@app.get("/api/jobs", response_model=JobListResponse)
def list_jobs(
    status: str | None = Query(None, description="Filter by job status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List all jobs with optional status filter."""
    query = db.query(Job)

    if status:
        query = query.filter(Job.status == status)

    total = query.count()
    jobs = query.order_by(Job.created_at.desc()).offset(offset).limit(limit).all()

    return JobListResponse(jobs=jobs, total=total)


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get the status and result of a specific job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.delete("/api/jobs/{job_id}", response_model=MessageResponse)
def cancel_job(job_id: str, db: Session = Depends(get_db)):
    """Cancel a pending job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status '{job.status}'. Only pending jobs can be cancelled.",
        )

    job.status = "cancelled"
    db.commit()

    return MessageResponse(message="Job cancelled successfully", job_id=job.id)
