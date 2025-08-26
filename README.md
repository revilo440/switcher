# Switcher - Smart Payment Engine

AI-powered credit card optimization for maximum rewards. Analyzes your purchases and recommends the best credit card to maximize cash back and points.

## Features

- **Natural Language Processing**: Describe purchases in plain English
- **Real-time Market Research**: Live credit card data via Brave Search API
- **AI-Powered Analysis**: Claude AI for intelligent recommendations
- **Interactive Demo Mode**: Try sample scenarios instantly
- **Financial Impact Projections**: See annual savings potential

## Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/revilo440/switcher.git
cd switcher
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure API Keys
Run this from the project root:
```bash
cp .env.example .env
# Edit .env with your API keys:
# - Claude API key from Anthropic
# - Brave Search API key from Brave
```
If you're already inside `backend/`, either go up one directory first or copy with a relative path:
```bash
# from backend/
cp ../.env.example ../.env
```

### 4. Run the Server
```bash
python main.py
```

### 5. Open Browser
Navigate to `http://localhost:8000` for the premium interface.

## API Keys Setup

### Claude API (Anthropic)
1. Sign up at [console.anthropic.com](https://console.anthropic.com)
2. Create an API key
3. Add to `.env` as `CLAUDE_API_KEY`

### Brave Search API
1. Sign up at [api.search.brave.com](https://api.search.brave.com)
2. Get your API key
3. Add to `.env` as `BRAVE_SEARCH_API_KEY`

## Demo Mode

The app works without API keys using fallback data. Enable Demo Mode in the UI to try sample scenarios.

## Architecture

- **Backend**: FastAPI with async processing
- **Frontend**: Vanilla JavaScript with modern UI
- **AI Services**: Claude for NLP, Brave Search for market data
- **Database**: SQLite for card data and transactions

## API Endpoints

- `POST /api/optimize` - Main optimization endpoint
- `GET /health` - Health check and API status
- `GET /` - Serve main application

## Development

The app includes comprehensive fallback responses when APIs are unavailable, making it fully functional for demos and development.

## License

MIT License
