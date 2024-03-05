from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class JobCreate(BaseModel):
    type: str = Field(
        ...,
        description="Job type: image_resize, send_email, or generate_report",
        examples=["image_resize"],
    )
    payload: dict[str, Any] = Field(
        ...,
        description="Job-specific payload data",
        examples=[{"image_url": "https://example.com/photo.jpg", "width": 800, "height": 600}],
    )


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    payload: str
    status: str
    result: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int


class MessageResponse(BaseModel):
    message: str
    job_id: Optional[str] = None
