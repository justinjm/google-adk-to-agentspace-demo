# Use a specific Python version for reproducibility.
# The project's README mentions Python 3.12+.
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install uv, the package manager used by the project.
# We'll use pip to install uv itself.
RUN pip install uv

# Copy only the dependency definition files first to leverage Docker's layer caching.
# This assumes pyproject.toml and an optional uv.lock are in the `src/data-science` directory.
COPY pyproject.toml uv.lock* ./

# Install project dependencies using uv.
# The --system flag installs packages into the global Python environment,
# which is standard practice for containers.
# The --no-cache flag reduces image size.
RUN uv sync --system --no-cache

# Copy the rest of the application source code.
# This includes your agent logic, prompts, and other utilities.
COPY . .

# Create a non-root user for enhanced security and give it ownership of the app files.
RUN adduser --disabled-password --gecos "" myuser && \
    chown -R myuser:myuser /app

# Switch to the non-root user.
USER myuser

# Cloud Run automatically sets the PORT environment variable.
# The ADK web server needs to listen on this port.
# We use sh -c to substitute the $PORT variable at runtime.
# The --host 0.0.0.0 makes the server accessible from outside the container.
CMD ["sh", "-c", "adk web --host 0.0.0.0 --port $PORT"]

