test:
  uv run pytest
  uv run mypy src/ tests/

alias ai := aider

aider:
  uv run aider
