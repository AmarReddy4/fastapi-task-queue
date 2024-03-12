# FastAPI Task Queue

Async task processing API built with FastAPI and Redis Queue (rq).

## Features

- Submit background jobs via REST API
- Redis-backed job queue with rq workers
- Job status tracking with SQLite persistence
- Support for multiple job types: image resize, email sending, report generation

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

Start Redis (via Docker):

```bash
docker-compose up -d
```

Start the API server:

```bash
uvicorn src.main:app --reload
```

Start a worker:

```bash
python -m src.worker
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/jobs` | Submit a new job |
| GET | `/api/jobs` | List all jobs |
| GET | `/api/jobs/{id}` | Get job status/result |
| DELETE | `/api/jobs/{id}` | Cancel a pending job |

## Example

```bash
# Submit a job
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{"type": "image_resize", "payload": {"image_url": "https://example.com/photo.jpg", "width": 800}}'

# Check job status
curl http://localhost:8000/api/jobs/{job_id}
```

## Tech Stack

- Python 3.11
- FastAPI 0.109.x
- Redis + rq (Redis Queue)
- SQLAlchemy 2.0 + SQLite
- Pydantic v2
