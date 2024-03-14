import json
import time
import random
import logging
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)


def _update_job_status(job_id: str, status: str, result: str | None = None):
    """Update job status in the database."""
    from src.models import Job

    session = Session()
    try:
        job = session.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = status
            if result:
                job.result = result
            if status in ("completed", "failed"):
                job.completed_at = datetime.utcnow()
            session.commit()
    finally:
        session.close()


def image_resize(job_id: str, payload: dict) -> dict:
    """Simulate image resizing."""
    logger.info(f"Starting image resize for job {job_id}")
    _update_job_status(job_id, "processing")

    image_url = payload.get("image_url", "unknown")
    width = payload.get("width", 800)
    height = payload.get("height", 600)

    # Simulate processing time
    time.sleep(random.uniform(2, 5))

    result = {
        "original_url": image_url,
        "resized_url": f"https://cdn.example.com/resized/{job_id}.jpg",
        "dimensions": {"width": width, "height": height},
        "file_size_kb": random.randint(50, 500),
    }

    logger.info(f"Completed image resize for job {job_id}")
    return result


def send_email(job_id: str, payload: dict) -> dict:
    """Simulate sending an email."""
    logger.info(f"Starting email send for job {job_id}")
    _update_job_status(job_id, "processing")

    to = payload.get("to", "user@example.com")
    subject = payload.get("subject", "No Subject")

    # Simulate sending
    time.sleep(random.uniform(1, 3))

    result = {
        "to": to,
        "subject": subject,
        "message_id": f"msg_{job_id[:8]}@example.com",
        "delivered": True,
    }

    logger.info(f"Email sent for job {job_id}")
    return result


def data_export(job_id: str, payload: dict) -> dict:
    """Simulate data export."""
    logger.info(f"Starting data export for job {job_id}")
    _update_job_status(job_id, "processing")

    table = payload.get("table", "users")
    format_type = payload.get("format", "csv")

    time.sleep(random.uniform(2, 6))

    result = {
        "table": table,
        "format": format_type,
        "rows": random.randint(100, 10000),
        "download_url": f"https://cdn.example.com/exports/{job_id}.{format_type}",
    }

    logger.info(f"Data export completed for job {job_id}")
    return result


def generate_report(job_id: str, payload: dict) -> dict:
    """Simulate report generation."""
    logger.info(f"Starting report generation for job {job_id}")
    _update_job_status(job_id, "processing")

    report_type = payload.get("report_type", "summary")
    date_range = payload.get("date_range", "last_30_days")

    # Simulate heavy processing
    time.sleep(random.uniform(5, 10))

    result = {
        "report_type": report_type,
        "date_range": date_range,
        "download_url": f"https://cdn.example.com/reports/{job_id}.pdf",
        "pages": random.randint(5, 50),
        "generated_at": datetime.utcnow().isoformat(),
    }

    logger.info(f"Report generated for job {job_id}")
    return result


TASK_HANDLERS = {
    "image_resize": image_resize,
    "send_email": send_email,
    "generate_report": generate_report,
    "data_export": data_export,
}


def process_job(job_id: str, job_type: str, payload: dict):
    """Main entry point for processing a job."""
    logger.info(f"Processing job {job_id} (type={job_type})")

    handler = TASK_HANDLERS.get(job_type)
    if not handler:
        _update_job_status(job_id, "failed", json.dumps({"error": f"Unknown job type: {job_type}"}))
        return

    try:
        result = handler(job_id, payload)
        _update_job_status(job_id, "completed", json.dumps(result))
        logger.info(f"Job {job_id} completed successfully")
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        _update_job_status(job_id, "failed", json.dumps({"error": str(e)}))
