# BusGo - Cloud Deployment & CI/CD: Bus Booking Platform

A bus booking web application with a complete DevOps workflow: containerised with Docker, tested and built automatically with GitHub Actions, and deployable to AWS EC2.

## Features
- Search buses by source, destination and date
- Seat selection with live availability per travel date
- Booking, booking history and cancellation
- Duplicate seat protection (database UNIQUE constraint)
- Health endpoint: `GET /api/health`

## Tech stack
Flask (Python), SQLite, HTML/CSS/JavaScript, Gunicorn, Docker, Docker Compose, GitHub Actions, AWS EC2

## Run locally
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000

## Run tests
```powershell
python -m unittest discover -s tests -v
```

## Run with Docker
```powershell
docker compose up -d --build
```
Open http://localhost:5000. Stop with `docker compose down`.

## API
| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/health | Health check |
| GET | /api/buses?source=&destination=&date= | Search buses |
| POST | /api/bookings | Book a seat |
| GET | /api/bookings | List bookings |
| DELETE | /api/bookings/{id} | Cancel a booking |

## CI/CD pipeline
On every push to `main`, GitHub Actions: checks out the code, installs dependencies, runs the unit tests, and builds the Docker image.

## AWS EC2 deployment
1. Launch an Ubuntu 24.04 EC2 instance (SSH from your IP, HTTP 80 open).
2. Install Docker: `sudo apt update && sudo apt install -y docker.io docker-compose-v2`
3. Clone the repo and run: `HOST_PORT=80 sudo -E docker compose up -d --build`

Live URL: _add your EC2 URL here_

## Screenshots
_Add screenshots here_
