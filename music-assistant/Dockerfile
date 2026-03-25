FROM python:3.12-slim

LABEL maintainer="house-bot homelab"
LABEL description="Local music assistant — history to playlists"

# Non-root user for safety
RUN groupadd -r muser && useradd -r -g muser -d /app -s /sbin/nologin muser

WORKDIR /app

# Install Python deps first (layer cached unless requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Stub data directories — real data comes from volume mounts at runtime.
# Pre-creating them here ensures the container starts cleanly in smoke tests
# even without mounts, and avoids permission surprises.
RUN mkdir -p /data/input /data/library /data/output/playlists \
    && chown -R muser:muser /data /app

USER muser

# Default: show help. Override with a subcommand in compose or docker run.
ENTRYPOINT ["python", "-m", "app.cli"]
CMD ["--help"]
