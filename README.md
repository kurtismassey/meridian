# Meridian

![Status](https://img.shields.io/badge/status-work%20in%20progress-yellow)

UK Local Authority Named Entity Recognition system using spaCy.

## Overview

Meridian extracts UK geographic and administrative entities from text:

- **LOCAL_AUTHORITY**: UK councils (e.g., "Manchester City Council")
- **REGION**: UK regions (e.g., "North West", "London")
- **POSTCODE_AREA**: UK postcode areas (e.g., "M1", "SW1A")

## Installation

```bash
uv sync
uv sync --extra dev  # For development dependencies
```

## Usage

### API

```bash
uv run fastapi dev meridian/main.py
```

Then visit http://localhost:8000/docs for the API documentation.

### Python

```python
from meridian.services.extraction import get_extractor

extractor = get_extractor()

result = extractor.extract("Contact Manchester City Council about council tax")
for entity in result.entities:
    print(f"{entity.text} -> {entity.label}")
```

## Development

Run tests:

```bash
uv run pytest
```
