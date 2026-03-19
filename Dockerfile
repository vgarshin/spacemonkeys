FROM cr.yandex/crptfs8246iv37ojkorv/simbadsai:20250404v0

USER root

WORKDIR /home/jovyan/app

# Create cache directory with proper permissions
RUN mkdir -p /home/jovyan/cache/images && chown -R 1000:1000 /home/jovyan/cache

# Create upload directory (separate from data)
RUN mkdir -p /home/jovyan/app/upload && \
    chown -R 1000:1000 /home/jovyan/app/upload

USER 1000

# Copy project files (preserve ownership)
COPY --chown=1000:1000 requirements.txt .
COPY --chown=1000:1000 src/ ./src/
COPY --chown=1000:1000 data/ ./data/
COPY --chown=1000:1000 scripts/ ./scripts/

# Install Python dependencies (fail on error)
RUN pip install --no-cache-dir -r requirements.txt

# Default command (can be overridden)
CMD ["python", "scripts.run_pipeline_refactored"]