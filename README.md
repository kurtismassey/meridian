# Meridian

![CI](https://github.com/kurtismassey/meridian/actions/workflows/ci.yml/badge.svg)
![Status](https://img.shields.io/badge/status-work%20in%20progress-yellow)

UK location NER library (local authority, region, postcode).

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

### Library

```python
from meridian import Meridian

meridian = Meridian()
result = meridian.recognise("Contact Manchester City Council about council tax")
for entity in result.entities:
    print(f"{entity.text} -> {entity.label}")
```

### API

```bash
uv sync --extra server   # or --extra dev
uv run fastapi dev api/main.py
```

Then visit http://localhost:8000/docs.

## Development

Run tests:

```bash
uv run pytest
```
