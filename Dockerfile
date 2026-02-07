FROM python:3.12-slim-bookworm

# Install uv (pinned version)
RUN pip install uv==0.9.26

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy dependency definitions
COPY pyproject.toml uv.lock ./

# Create the venv directory and give permissions to appuser
# We need to ensure appuser owns the directory where uv sync will write
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Install dependencies
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application
COPY --chown=appuser:appuser . .

# Run the application
CMD ["uv", "run", "python", "main.py"]
