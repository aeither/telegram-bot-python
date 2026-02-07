FROM python:3.12-slim-bookworm

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency definitions
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application
COPY . .

# Run the application
CMD ["uv", "run", "python", "main.py"]
