# BusGo: Cloud Deployment & CI/CD Bus Booking Platform

A bus booking web application with a complete DevOps workflow. The app is containerised with Docker, tested and built automatically with GitHub Actions, and deployed on AWS EC2.

**Author:** Anjali Mishra
**Track:** DevOps & Cloud Engineering

## Features

- Search buses by source, destination and travel date
- City suggestions to avoid spelling mistakes
- Seat selection with live availability for each travel date
- Booking, booking history and cancellation
- Duplicate seat protection using a database UNIQUE constraint
- Health check endpoint for monitoring

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite |
| Production server | Gunicorn |
| Containers | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Cloud | AWS EC2 (Ubuntu 24.04) |

## Project structure

    .
    |-- app.py                  Flask backend and API
    |-- templates/index.html    Website
    |-- static/style.css        Styling
    |-- tests/test_app.py       Automated tests
    |-- Dockerfile              Container image
    |-- docker-compose.yml      Container configuration
    |-- requirements.txt        Python dependencies
    `-- .github/workflows/      CI pipeline

## Run locally

    python -m venv venv
    source venv/Scripts/activate      # Git Bash on Windows
    pip install -r requirements.txt
    python app.py

Open http://localhost:5000

## Run the tests

    python -m unittest discover -s tests -v

The tests cover the health check, bus search, booking, duplicate seat rejection and cancellation.

## Run with Docker

    docker compose up -d --build
    docker ps
    curl http://localhost:5000/api/health
    docker compose down

Booking data is stored in a Docker volume, so it survives container restarts.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/health | Health check |
| GET | /api/buses?source=&destination=&date= | Search buses |
| POST | /api/bookings | Book a seat |
| GET | /api/bookings | List bookings |
| DELETE | /api/bookings/{id} | Cancel a booking |

## CI/CD pipeline

On every push to the main branch, GitHub Actions runs these steps:

1. Check out the code
2. Install Python dependencies
3. Run the automated tests
4. Build the Docker image

## AWS EC2 deployment

1. Launch an Ubuntu 24.04 EC2 instance.
2. Open port 22 (SSH) for your IP only and port 80 (HTTP) for everyone.
3. Install Docker on the server.
4. Clone this repository and start the app with Docker Compose.


