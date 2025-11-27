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
- [ ] **Extractor**: Implement Regex-based text parsing in `src/extractor.py`
- [ ] **Repository**: Implement DB operations in `src/repository.py`

### Phase 3: Integration
- [ ] **Pipeline**: Connect components in `main.py`
- [ ] **Testing**: Verify with sample text

## Current Status
- Project initialized.
- Schema designed.
- Ready to implement models.
