# Project Plan: Hanja Extraction & Dictionary MVP

## Goal
Extract Hanja characters and words from documents, creating a local SQLite database containing character details (sound, meaning, radical) and usage examples.

## Architecture
- **Language**: Python
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Entry Point**: `main.py`
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

## Current Status
- Multi-source support implemented and verified with text files.
- PDF reading logic in place (requires PDF file for testing).
- Project is fully functional for defined scope.
