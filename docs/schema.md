# Database Schema Design

## Overview
SQLite database intended to store individual Hanja characters with their properties and usage examples (words).

## Tables

### 1. `hanja_info`
Stores individual Hanja characters and their metadata.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Auto-increment | Unique identifier |
| `char` | String(1) | Unique, Not Null | The Hanja character itself |
| `sound` | String | Not Null | The Korean pronunciation (음) |
| `meaning` | String | | The meaning (뜻) |
| `radical` | String | | The radical (부수) |
| `strokes` | Integer | | Total stroke count (획수) |

### 2. `usage_examples`
Stores words consisting of 2 or more consecutive Hanja characters.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Auto-increment | Unique identifier |
| `word` | String | Unique, Not Null | The word (2+ Hanja chars) |
| `sound` | String | | Pronunciation of the word |
| `frequency` | Integer | Default 1 | Occurrence count in processed docs |

## Relationships
- Currently designed as independent tables for MVP.
- Future optimization could link `usage_examples` to `hanja_info` via a junction table if detailed character analysis within words is needed.
