FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv
RUN pip install --no-cache-dir --upgrade pip uv

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
