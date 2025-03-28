test:
  uv run pytest
  uv run mypy src/ tests/

alias ai := aider

aider:
  uv run aider

build:
  uv build

publish:
  export UV_PUBLISH_TOKEN=`op read --no-newline 'op://non-interactive/pypi.org_token/credential'` && \
  uv publish

publish-to-testpypi:
  export UV_PUBLISH_TOKEN=`op read --no-newline 'op://non-interactive/test.pypi.org_token/credential'` && \
  uv publish --index testpypi

test-package:
  uv run --with midi2cmd --no-project -- \
    python -c "import midi2cmd; print(midi2cmd.__version__)"

clean:
  rm dist/*
