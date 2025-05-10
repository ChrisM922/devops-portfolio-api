# DevOps Project

A Flask-based web application with PostgreSQL database, containerized using Docker.

## 🚀 Features

- Flask web application
- PostgreSQL database
- Docker containerization
- Development environment with hot-reloading
- SQLAlchemy ORM for database operations

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
