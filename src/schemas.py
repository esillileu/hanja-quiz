from typing import List, Optional
from pydantic import BaseModel

class HanjaReadingResponse(BaseModel):
    sound: str
    meaning: Optional[str] = None

    class Config:
        from_attributes = True

class HanjaInfoResponse(BaseModel):
    id: int
    char: str
    radical: Optional[str] = None
    strokes: Optional[int] = None
    readings: List[HanjaReadingResponse] = []

    class Config:
        from_attributes = True

class HanjaFrequencyResponse(BaseModel):
    hanja: HanjaInfoResponse
    frequency: int

    class Config:
        from_attributes = True

class PaginatedHanjaResponse(BaseModel):
    total: int
    items: List[HanjaFrequencyResponse]
    page: int
    size: int

class RadicalFrequencyResponse(BaseModel):
    radical: Optional[str]
    frequency: int
    # We might want to include a list of Hanja chars here or just count
    # For now, let's keep it simple
    
    class Config:
        from_attributes = True

class PaginatedRadicalResponse(BaseModel):
    total: int
    items: List[RadicalFrequencyResponse]
    page: int
    size: int

class WordCharFrequencyResponse(BaseModel):
    char: str
    frequency: int
    hanja_info: Optional[HanjaInfoResponse] = None

class PaginatedWordCharResponse(BaseModel):
    total: int
    items: List[WordCharFrequencyResponse]
    page: int
    size: int
