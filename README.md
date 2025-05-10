# DevOps Project

[![CI](https://github.com/ChrisM922/devops-portfolio-api/actions/workflows/ci.yml/badge.svg)](https://github.com/ChrisM922/devops-portfolio-api/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/ChrisM922/devops-portfolio-api/branch/main/graph/badge.svg)](https://codecov.io/gh/ChrisM922/devops-portfolio-api)
[![Python Version](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![Flask Version](https://img.shields.io/badge/flask-3.1.0-blue.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Flask-based web application with PostgreSQL database, containerized using Docker.

## 🚀 Features

- Flask web application
- PostgreSQL database
- Docker containerization
- Development environment with hot-reloading
- SQLAlchemy ORM for database operations
- Observability and monitoring
  - Structured logging
  - Prometheus metrics
  - Health checks

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for local development)
- Git

## 🛠️ Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd <project-directory>
```

2. Using Docker (Recommended):

```bash
docker-compose up --build
```

3. For local development:

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Configuration

The application uses the following environment variables:

- `FLASK_ENV`: Set to 'development' for development mode
- `DATABASE_URL`: PostgreSQL connection string (default: postgresql://postgres:postgres@db:5432/tasks_db)

## 🏃‍♂️ Running the Application

### Using Docker

```bash
# Start all services
docker-compose up

# Run in detached mode
docker-compose up -d

# Stop all services
docker-compose down
```

### Local Development

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run Flask application
flask run
```

The application will be available at `http://localhost:5000`

## 📁 Project Structure

```
.
├── app/                    # Application source code
├── .venv/                  # Python virtual environment
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## 🛠️ Development

- The application uses Flask for the web framework
- PostgreSQL is used as the database
- SQLAlchemy is used as the ORM
- Docker is used for containerization

## Live Demo

The application is deployed at: [https://devops-portfolio-api.onrender.com](https://devops-portfolio-api.onrender.com)

## Observability

### Logging

The application uses Python's built-in logging module with structured formatting:

- Logs are written to stdout for container platforms
- Log level: INFO for development, WARNING/ERROR for production
- Log format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

View logs:

- Development: Console output
- Production: Render dashboard logs
- Metrics: `/metrics` endpoint (Prometheus format)

### Monitoring

The application exposes Prometheus metrics at `/metrics`:

- Request counts and latencies
- Task operation counts
- Database connection status
- Application version info

### Health Checks

A health check endpoint is available at `/health`:

- Database connection status
- Application status
- Returns 200 if healthy, 500 if unhealthy

## Monitoring Setup

1. View application logs in the Render dashboard
2. Access Prometheus metrics at `/metrics`
3. Monitor application health at `/health`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
