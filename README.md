# PDF Text Capture and AI Processing Project

A Python project for capturing text from PDF files and processing text with AI agents.

## Overview

The project consists of four modules:

1. **MODULE 1** – Upload files from local `upload/` folder to Yandex Object Storage bucket `cosmo-gsom-check-data`, preserving directory structure.
2. **MODULE 2** – Download PDFs from object storage, convert them to images, and extract text using Yandex OCR.
3. **MODULE 3** – First AI agent that uses a pre‑defined prompt to detect AI‑generated text and returns a score.
4. **MODULE 4** – Second AI agent that estimates quality and grades text work, updates a CSV file with grades, and saves results to object storage `cosmo-gsom-result-data`.

## Project Structure

```
.
├── src/
│   ├── module1_upload/          # Upload local files to S3
│   ├── module2_ocr/             # PDF → images → OCR
│   ├── module3_ai_detect/       # AI‑generated text detection
│   ├── module4_ai_grade/        # Text quality grading
│   ├── utils/                   # Shared utilities (S3, OCR, LLM, logging, CSV updater)
│   └── config/                  # Configuration settings
├── tests/                       # Unit tests
├── data/                        # Credentials and configuration JSONs
├── logs/                        # Application logs
├── cache/                       # Temporary images and caches
├── upload/                      # Folder containing PDFs to upload and process
├── scripts/                     # Pipeline runner scripts
├── requirements.txt             # Python dependencies
└── README.md
```

## Installation

1. Clone the repository.
2. Install Python 3.9+.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Place your credentials in `data/credentials.json` (see `data/credentials.example.json`).
5. Place PDF files to process in the `upload/` folder.

## Docker & Docker Compose

The project includes Docker support for easy deployment and execution.

### Quick Start

1. Ensure Docker and Docker Compose are installed.
2. Build and run the pipeline with:

```bash
docker-compose up --build
```

This will:
- Build the image from `Dockerfile` (based on a custom Yandex Cloud base image)
- Mount local directories (`data/`, `logs/`, `cache/`, `upload/`) into the container
- Set environment variables (`PYTHONPATH`, `LOG_LEVEL`)
- Execute the full pipeline (`scripts/run_pipeline_refactored.py`)
- Restart the container on failure

### Docker Compose Configuration

The `docker-compose.yml` defines a single service `pdf-ai` with the following features:

- **Volumes**:
  - `./data:/home/jovyan/app/data:ro` – read‑only credentials and configuration
  - `./logs:/home/jovyan/app/logs` – log output
  - `./cache:/home/jovyan/app/cache` – cached OCR images and intermediate files
  - `./upload:/home/jovyan/app/upload:ro` – PDF files to process (read‑only)
  - External directory with case solutions (mounted read‑only)

- **Environment**:
  - `PYTHONPATH=/home/jovyan/app` – ensures module imports work
  - `LOG_LEVEL=INFO` – controls logging verbosity

- **Restart policy**: `on-failure` – automatic restart if the pipeline fails.

### Docker Images

- **Production image**: Built from `Dockerfile`. Installs dependencies from `requirements.txt` and sets the default command to run the pipeline.
- **Debug image**: `Dockerfile.debug` is provided for inspecting the base image and installed packages. It can be used for troubleshooting.

### Running Custom Commands

To run a different script or start an interactive shell inside the container:

```bash
docker-compose run --rm pdf-ai python -m scripts.verify
```

or

```bash
docker-compose run --rm pdf-ai /bin/bash
```

### Notes

- The container runs as user `1000` (non‑root) for security.
- The pipeline expects credentials in `data/credentials.json` (mounted from the host).
- Logs are written both to `logs/app.log` (host) and stdout.
- The `upload/` folder must contain PDF files to be processed; sub‑directories are preserved.

### Add‑ons & Extensions

The Docker Compose setup can be extended with additional services and features:

- **Health checks**: Add a `healthcheck` directive to the service definition to monitor container health.
- **Logging drivers**: Configure Docker logging drivers (e.g., `json-file`, `syslog`, `journald`) for centralized log management.
- **Monitoring**: Integrate with Prometheus and Grafana by exposing metrics endpoints and adding sidecar containers.
- **CI/CD**: Use the Docker image in CI/CD pipelines (GitHub Actions, GitLab CI) for automated testing and deployment.
- **Multi‑stage builds**: Optimize image size by splitting build and runtime stages in the Dockerfile.

These add‑ons are not included by default but can be added as needed.

## Configuration

Edit `src/config/settings.py` to adjust paths, bucket names, API endpoints, etc.

Credentials are stored in `data/credentials.json`:

```json
{
    "s3": {
        "access_key_id": "...",
        "secret_access_key": "...",
        "bucket": "cosmo-gsom-check-data",
        "endpoint": "https://storage.yandexcloud.net"
    },
    "yandex": {
        "folder_id": "...",
        "ocr_api_key": "...",
        "llm_api_key": "...",
        "ocr_api_id": "..."
    }
}
```

## Usage

### Module 1: Upload files

```python
from src.module1_upload.uploader import upload_all_files

uploaded = upload_all_files()
print(f"Uploaded {uploaded} files.")
```

### Module 2: Process PDFs with OCR

```python
from src.module2_ocr.pdf_ocr import process_all_pdfs

results = process_all_pdfs()
```

### Module 3: Detect AI‑generated text

```python
from src.module3_ai_detect.ai_detector import detect_ai_generated

text = "Some text to analyze..."
response = detect_ai_generated(text)
```

### Module 4: Grade text quality

```python
from src.module4_ai_grade.ai_grader import grade_text_quality

grade = grade_text_quality(text)
```

### CSV Grading Update

The pipeline automatically downloads a CSV file from the S3 check bucket, updates it with extracted grades, and uploads the updated CSV to the result bucket. The CSV file is expected to have a `Group` column that matches the group names extracted from PDF filenames. The CSV updater utilities are located in `src/utils/csv_updater.py`.

### Running the full pipeline

A sample pipeline script is provided in `scripts/run_pipeline_refactored.py`.

## Logging

Logs are written to `logs/app.log` and printed to stdout. Configure logging in `src/utils/logging_config.py`.

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## Requirements

See `requirements.txt` for a full list of dependencies.

## License

Proprietary.