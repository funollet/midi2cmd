test:
  uv run pytest
  uv run mypy src/ tests/

alias ai := aider

aider:
  uv run aider

build:
  uv build

publish:
  uv publish

publish-to-testpypi:
  uv publish --index testpypi --token ${UV_PUBLISH_TOKEN_TESTPYPI}

test-package:
  uv run --with midi2cmd --no-project -- \
    python -c "import midi2cmd; print(midi2cmd.__version__)"

clean:
  rm dist/*
