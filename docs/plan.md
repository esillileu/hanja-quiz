# Project Plan: Hanja Extraction & Dictionary MVP

## Goal
Extract Hanja characters and words from documents, creating a local SQLite database containing character details (sound, meaning, radical) and usage examples. Ultimately, serve this data via a Streamlit web application for analysis and learning.

## Architecture
- **Language**: Python
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Frontend**: Streamlit
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

### Phase 6: Backend API & Analysis
- [x] **FastAPI Setup**: Add `fastapi` and `uvicorn`.
- [x] **API Structure**: Create `src/api.py`.
- [x] **Analysis Logic**: Implement top hanja/radical/word analysis.

### Phase 7: Enhanced UI & Quiz Mode
- [x] **Streamlit Layout**: Implement Sidebar navigation (Analysis vs Quiz).
- [x] **Quiz Logic Upgrade (`src/quiz.py`)**: Weighted random, radical filtering, various question types.
- [x] **Quiz UI**: Interactive quiz interface.

### Phase 8: Incorrect Answer Note (Mistake Tracker)
- [x] **Schema Update**: Create `WrongAnswer` table.
- [x] **Repository Update**: Add methods to record wrong answers (`record_mistake`).
- [x] **Quiz Logic Upgrade**: Add "Mistake Review" mode.
- [x] **UI Update**: Add "오답노트" tab and "오답 복습" quiz mode.

### Phase 9: Importance-based Learning (New)
- [ ] **Schema Update**: Create `UserProgress` table (hanja_id, word_id, importance_level).
- [ ] **Repository Update**: Add `update_importance(id, delta)` method.
- [ ] **Quiz Logic Upgrade**:
    - Modify `generate_quiz` to support filtering/weighting by `importance_level`.
    - Add "Importance Review" mode.
- [ ] **UI Update**:
    - Display importance level in quiz and list views.
    - Add quiz option to select importance level range.
    - Visual feedback for importance change (+1/-1).

## Current Status
- Mistake tracking implemented.
- Ready to implement Importance-based Learning (Phase 9).
