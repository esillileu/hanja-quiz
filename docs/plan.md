# Project Plan: Hanja Extraction & Dictionary MVP

## Goal
Extract Hanja characters and words from documents, creating a local SQLite database containing character details (sound, meaning, radical) and usage examples. Ultimately, serve this data via a FastAPI backend for a web application.

## Architecture
- **Language**: Python
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Entry Point**: `main.py` (CLI), `src/api.py` (FastAPI)
- **Source Directory**: `src/`

## Roadmap

### Phase 1: Setup & Design
- [x] Initialize project structure (`src`, `docs`)
- [x] Define dependencies (`pyproject.toml`)
- [x] Design database schema (`docs/schema.md`)
- [x] Create project plan (`docs/plan.md`)

### Phase 2: Core Implementation
- [x] **Models**: Implement SQLAlchemy models in `src/models.py`
- [x] **Dictionary**: Implement Hanja info lookup (sound, meaning, radical) in `src/dictionary.py`
- [x] **Extractor**: Implement Regex-based text parsing in `src/extractor.py`
- [x] **Repository**: Implement DB operations in `src/repository.py`

### Phase 3: Integration
- [x] **Pipeline**: Connect components in `main.py`
- [x] **Testing**: Verify with sample text

### Phase 4: Multi-Source Support
- [x] **File Reader**: Create `src/reader.py` to handle various file inputs.
- [x] **Text Loader**: Implement plain text (`.txt`) file reading.
- [x] **PDF Loader**: Implement PDF (`.pdf`) text extraction using `pypdf`.
- [x] **CLI Arguments**: Update `main.py` to accept file paths via command line arguments (using `argparse`).

### Phase 5: Advanced Data Management
- [x] **Schema Refactoring**: `Document`, `RefHanja`, `DocumentHanja`, `DocumentWord`.
- [x] **Dictionary Loader**: CSV loader to pre-seed `RefHanja`.
- [x] **Idempotency Logic**: Prevent duplicate file processing.
- [x] **Migration & Processing**: Reprocess all sample PDF files.

### Phase 6: Backend API (New)
- [ ] **FastAPI Setup**: Add `fastapi` and `uvicorn`.
- [ ] **API Structure**: Create `src/api.py` or `src/routers/` for endpoints.
- [ ] **Endpoint: Hanja Analysis**:
    - `GET /analysis/hanja`: Top frequent characters with pagination.
    - `GET /analysis/radicals`: Top frequent radicals with pagination.
    - `GET /analysis/words`: Top frequent characters in words with pagination.
- [ ] **Endpoint: Search**: Simple search for character or word.
- [ ] **Response Models**: Define Pydantic models for clear API responses.

## Current Status
- Data processing pipeline complete and verified.
- DB fully populated with exam data.
- Ready to build FastAPI backend (Phase 6).