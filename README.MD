
# Tibiantis-Bot

A Discord bot and API service for the Tibiantis game server, providing character tracking, death notifications, and player statistics.

## Overview

Tibiantis-Bot is a dual-component application consisting of:

1. **Discord Bot**: Monitors character deaths, notifies about enemy kills, and provides game-related information
2. **FastAPI Server**: Provides REST API endpoints for accessing character data and game statistics

## Setup Instructions

### Prerequisites

- Python 3.8+
- Git
- SQLite (default) or PostgreSQL

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/Tibiantis-Bot.git
   cd Tibiantis-Bot
   ```

2. **Create and activate a virtual environment:**

   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/macOS
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   Create a `.env` file in the project root with the following variables:

   ```
   # Database Configuration
   DATABASE_URL=sqlite:///./database.db
   
   # Discord Bot Configuration
   DISCORD_BOT_TOKEN=your_discord_bot_token
   DISCORD_CHANNEL_ID=your_discord_channel_id
   ENEMY_KILLS_CHANNEL_ID=your_enemy_kills_channel_id
   TABLE_REFRESH_INTERVAL=3
   
   # API Configuration (optional)
   API_HOST=127.0.0.1
   API_PORT=8000
   API_RELOAD=True
   
   # Logging Configuration
   LOG_LEVEL=INFO
   BOT_LOG_LEVEL=INFO
   API_LOG_LEVEL=INFO
   DB_LOG_LEVEL=WARNING
   SCRAPER_LOG_LEVEL=INFO
   ```

5. **Initialize the database:**

   ```bash
   alembic upgrade head
   ```

## Running the Application

The application can be started with a single command:

```bash
python run.py
```

This will start both the Discord bot and the FastAPI server in separate processes.

### API Documentation

Once the application is running, you can access the API documentation at:

```
http://127.0.0.1:8000/docs
```

## Project Structure

```
Tibiantis-Bot/
├── alembic/                  # Database migration scripts
├── app/                      # Main application code
│   ├── api/                  # API endpoints
│   ├── bot/                  # Discord bot code
│   ├── db/                   # Database models and session management
│   │   ├── models/           # SQLAlchemy ORM models
│   │   └── schemas/          # Pydantic schemas for API
│   ├── repositories/         # Data access layer
│   ├── scrapers/             # Web scraping utilities
│   ├── tasks/                # Background tasks
│   └── utils/                # Utility functions
├── docs/                     # Documentation
├── logs/                     # Log files
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
└── run.py                    # Application entry point
```

## Features

### Discord Bot

- **Death Checker**: Monitors character deaths and reports when high-level characters are killed by enemy players
- **Player Tracking**: Tracks online players and their statistics
- **Notifications**: Sends formatted tables to Discord channels with relevant information

### API

- **Character Endpoints**: Access character information and statistics
- **Enemy Character Endpoints**: Information about enemy characters and their kills

## Development

### Database Migrations

After making changes to database models:

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Code Style

This project follows PEP 8 style guidelines. Key principles:

- Use descriptive variable and function names
- Add docstrings to all functions and classes
- Include type hints for function parameters and return values
- Follow the repository pattern for database operations

### Error Handling

- Use appropriate HTTP status codes in API responses
- Log errors with sufficient context for debugging
- Use the base classes (BaseTask, BaseRepository) for common functionality

## Logging

Logs are stored in the `logs` directory. Log levels can be configured through environment variables in the `.env` file.

## License

This project is licensed under the [MIT License](LICENSE).