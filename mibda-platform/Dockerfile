# Streamlit platform image (works on Hugging Face Spaces: Docker SDK, port 7860).
# Weights are NOT baked in: mount or copy models/best.pt and add `ultralytics` to run the detector.
FROM python:3.11-slim

# DejaVu has Arabic glyphs, needed for Arabic PDF reports.
RUN apt-get update && apt-get install -y --no-install-recommends fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 app
WORKDIR /home/app/or-intelligence
COPY --chown=app:app requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=app:app . .

USER app
ENV ORI_DATA_DIR=/home/app/or-intelligence/data \
    PYTHONUNBUFFERED=1
EXPOSE 7860
# Create demo accounts + (optionally) import a dataset mounted at /dataset before starting.
CMD ["sh", "-c", "python scripts/seed_demo.py ${ORI_DATASET:+--cholect50 $ORI_DATASET}; streamlit run app/main.py --server.port=7860 --server.address=0.0.0.0"]
