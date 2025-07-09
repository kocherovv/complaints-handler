from pydantic import BaseModel
from pydantic import Field
from typing import List


class ComplaintRequest(BaseModel):
    text: str = Field(max_length=1000)


class ComplaintResponse(BaseModel):
    id: int
    status: str
    sentiment: str
    category: str


class ComplaintDetailResponse(BaseModel):
    id: int
    text: str
    status: str
    timestamp: int
    sentiment: str
    category: str

    class Config:
        from_attributes = True


class CloseComplaintRequest(BaseModel):
    complaint_id: int


class GetComplaintsRequest(BaseModel):
    status: str
    hours: int
