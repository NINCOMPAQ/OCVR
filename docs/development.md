# Development

Install an editable development environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,extract]"
pytest
ruff check .
```

The full datasets and models are deliberately excluded from tests. Unit tests use small generated fixtures; integration tests should be marked separately when added.

Do not silently replace an existing Qdrant collection. Build versioned or staging collections, verify them, and promote them explicitly.

