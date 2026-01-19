# Dataset Metadata Service

This project is a simple backend service to manage dataset metadata,
track dataset lineage, and support basic search functionality.

## Features
- Store dataset and column metadata
- Track upstream and downstream lineage
- Prevent cyclic lineage
- Search datasets by keyword
- Health check endpoint

## Tech Stack
- Python
- FastAPI
- SQLAlchemy
- MySQL
- Docker & Docker Compose

## How to Run
1. Make sure Docker is installed
2. Run the following command:
   docker-compose up --build
3. The service will start on:
   http://localhost:8000

## Health Check
GET /health
