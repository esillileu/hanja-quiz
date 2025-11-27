from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from collections import Counter

from src.models import init_db, HanjaInfo, DocumentHanja, DocumentWord, UsageExample
from src.schemas import (
    PaginatedHanjaResponse, 
    HanjaFrequencyResponse, 
    PaginatedRadicalResponse, 
    RadicalFrequencyResponse,
    PaginatedWordCharResponse,
    WordCharFrequencyResponse
)

app = FastAPI(title="Hanja Analysis API")

# Dependency
def get_db():
    SessionLocal = init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/analysis/hanja", response_model=PaginatedHanjaResponse)
def get_top_hanja(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get most frequent Hanja characters with pagination.
    """
    offset = (page - 1) * size
    
    # Query for total count (of unique hanjas that appeared)
    total = db.query(DocumentHanja.hanja_id).distinct().count()
    
    # Query for items
    results = db.query(
        HanjaInfo, 
        func.sum(DocumentHanja.frequency).label('total_freq')
    ).join(DocumentHanja).group_by(HanjaInfo.id).order_by(desc('total_freq')).offset(offset).limit(size).all()
    
    items = []
    for hanja, freq in results:
        items.append(HanjaFrequencyResponse(hanja=hanja, frequency=freq))
        
    return {
        "total": total,
        "items": items,
        "page": page,
        "size": size
    }

@app.get("/analysis/radicals", response_model=PaginatedRadicalResponse)
def get_top_radicals(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get most frequent radicals with pagination.
    """
    offset = (page - 1) * size
    
    # Total unique radicals that appeared
    total = db.query(HanjaInfo.radical).join(DocumentHanja).distinct().count()
    
    # Group by radical and sum frequency
    results = db.query(
        HanjaInfo.radical,
        func.sum(DocumentHanja.frequency).label('radical_freq')
    ).join(DocumentHanja).filter(HanjaInfo.radical != None).group_by(HanjaInfo.radical).order_by(desc('radical_freq')).offset(offset).limit(size).all()
    
    items = []
    for radical, freq in results:
        items.append(RadicalFrequencyResponse(radical=radical, frequency=freq))
        
    return {
        "total": total,
        "items": items,
        "page": page,
        "size": size
    }

@app.get("/analysis/words/chars", response_model=PaginatedWordCharResponse)
def get_top_hanja_in_words(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get most frequent characters appearing WITHIN words (calculated in memory for now).
    Note: Pagination here is simulated on the full result set because calculation is complex.
    For very large datasets, this needs optimization (pre-calculation table).
    """
    # 1. Get all words and frequencies
    words = db.query(UsageExample, func.sum(DocumentWord.frequency).label('total_freq')).join(DocumentWord).group_by(UsageExample.id).all()
    
    char_counter = Counter()
    for word_obj, freq in words:
        for char in word_obj.word:
            char_counter[char] += freq
            
    # 2. Sort and Paginate in memory
    sorted_chars = char_counter.most_common()
    total = len(sorted_chars)
    
    start = (page - 1) * size
    end = start + size
    paged_data = sorted_chars[start:end]
    
    # 3. Enrich with HanjaInfo
    items = []
    for char, freq in paged_data:
        hanja_info = db.query(HanjaInfo).filter_by(char=char).first()
        items.append(WordCharFrequencyResponse(char=char, frequency=freq, hanja_info=hanja_info))
        
    return {
        "total": total,
        "items": items,
        "page": page,
        "size": size
    }
