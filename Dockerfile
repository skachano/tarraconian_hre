FROM python:3.12-slim-bookworm

LABEL maintainer="Tarraconian Imperial Chancellery"
LABEL description="Containerized CK3 Save Game & Landed Title Extraction Engine"

WORKDIR /workspace

# rakaly can be mounted from host /tmp or installed
ENTRYPOINT ["python3", "/workspace/scripts/extract_save_phase1.py"]
