# AGENTS.md

## Build
- Install: `pip install -e ".[dev]"` or `npm install`
- Run: `uvicorn src.main:app --reload` or `npm run dev`
- Test: `pytest tests/ -v` or `npm test`
- Lint: `ruff check src/` or `npm run lint`
- Type check: `mypy src/` or `npm run typecheck`

## Constraints
- Test framework: pytest (Python) / vitest (JS) — do not switch
- Formatter: ruff (Python) / prettier (JS) — do not reconfigure
- Branch: never push directly to main
- Dependencies: pin exact versions in requirements.txt / package-lock.json
- Secrets: never hardcode; always use environment variables

## Architecture
- Pattern: Router → Service → Repository → Database
- Auth: JWT tokens, see src/core/auth.py
- Error handling: custom exceptions in src/core/exceptions.py
- Config: environment variables only, see src/core/config.py

## Testing
- Unit tests required for all service-layer functions
- Integration tests required for all API endpoints
- Minimum coverage: 70% (enforced by CI)
- Test data: use factories in tests/factories/, not hardcoded data