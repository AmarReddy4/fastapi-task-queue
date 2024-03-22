"""
Redis Queue worker for processing background jobs.

Usage:
    python -m src.worker

The worker connects to Redis, listens on the default queue,
and processes jobs as they arrive.
"""

import os
import sys
import logging

import redis
from rq import Worker, Queue, Connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUES = os.getenv("WORKER_QUEUES", "default").split(",")


def run_worker():
    """Start the rq worker."""
    conn = redis.from_url(REDIS_URL)

    try:
        conn.ping()
        logger.info(f"Connected to Redis at {REDIS_URL}")
    except redis.ConnectionError:
        logger.error(f"Cannot connect to Redis at {REDIS_URL}")
        sys.exit(1)

    with Connection(conn):
        queues = [Queue(name) for name in QUEUES]
        worker = Worker(queues)
        logger.info(f"Worker started, listening on queues: {', '.join(QUEUES)}")
        worker.work()


if __name__ == "__main__":
    run_worker()
