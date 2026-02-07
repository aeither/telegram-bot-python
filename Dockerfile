FROM python:3.12-slim

# The Dockerfile runs as root to avoid permission errors on Railway.
# This ensures that commands like `WORKDIR /app`, `RUN uv sync`, and the final `CMD`
# can manage files and dependencies without ownership conflicts.
#
# If switching to a non-root user (e.g., USER appuser), ensure ownership is correct:
# RUN useradd -m appuser && chown -R appuser:appuser /app
# USER appuser

# Set working directory
WORKDIR /app

# Install uv
RUN pip install --no-cache-dir --upgrade pip uv==0.5.29

# Set UV environment variables for Railway
ENV UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_SYNC=1

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev, skip project itself)
RUN uv sync --locked --no-dev --no-install-project

# Copy application code
COPY . .

# Install the project in non-editable mode
RUN uv sync --locked --no-dev --no-editable

# Run bot
CMD ["uv", "run", "main.py"]
