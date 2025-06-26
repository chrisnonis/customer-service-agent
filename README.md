# OpenAI CS Agents Demo

A demonstration of a multi-agent system for UK sports information using OpenAI's Agent SDK, with grounding capabilities via Google Custom Search.

## Features

- **Multi-Agent System**: Triage, Premier League, Championship, Boxing, and Sports News agents
- **Grounding with Google Custom Search**: Get up-to-date information when AI knowledge is outdated
- **Real-time Sports Information**: Current fixtures, transfers, standings, and news
- **Modern UI**: Built with Next.js and Tailwind CSS

## Setup

### Prerequisites

- Python 3.8+
- Node.js 18+
- Google API Key (for Gemini)
- Google Custom Search API Key
- Google Custom Search Engine ID

### Environment Configuration

Create a `.env` file in the `python-backend` folder with the following variables:

```bash
# Google API Keys
GOOGLE_API_KEY=your_gemini_api_key_here

# Google Custom Search Configuration
GOOGLE_CUSTOM_SEARCH_API_KEY=your_google_custom_search_api_key_here
GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your_google_custom_search_engine_id_here
```

#### Setting up Google Custom Search

1. **Get Google Custom Search API Key**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the "Custom Search API"
   - Create credentials (API Key)

2. **Create Google Custom Search Engine**:
   - Go to [Google Programmable Search Engine](https://programmablesearchengine.google.com/)
   - Click "Create a search engine"
   - Enter your site or use "Search the entire web"
   - Get your Search Engine ID (cx parameter)

3. **Configure Search Engine** (Optional):
   - Add sports websites to your search engine for better results
   - Recommended sites: BBC Sport, Sky Sports, Premier League, etc.

### Installation

#### Backend Setup

```bash
cd python-backend
python -m venv .venv
.venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

#### Frontend Setup

```bash
cd ui
npm install
```

## Running the Application

### Run the backend only

From the `python-backend` folder, run:

```bash
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

The backend will be available at: [http://localhost:8000](http://localhost:8000)

#### Run the UI & backend simultaneously

From the `ui` folder, run:

```bash
npm run dev
```

The frontend will be available at: [http://localhost:3000](http://localhost:3000)

This command will also start the backend.

## Deployment

### GitHub Setup

1. **Create a new GitHub repository**:
   ```bash
   # Remove the current origin (if it points to the original demo repo)
   git remote remove origin
   
   # Add your new GitHub repository as origin
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   
   # Commit and push your changes
   git add .
   git commit -m "Initial commit for deployment"
   git push -u origin main
   ```

2. **Create a new repository on GitHub**:
   - Go to [GitHub](https://github.com) and create a new repository
   - Don't initialize with README, .gitignore, or license (since you already have these)
   - Copy the repository URL and use it in the commands above

### Vercel Deployment

1. **Install Vercel CLI** (optional):
   ```bash
   npm install -g vercel
   ```

2. **Deploy to Vercel**:
   - Go to [Vercel](https://vercel.com) and sign up/login
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will automatically detect the Next.js app in the `ui` folder

3. **Configure Environment Variables**:
   In your Vercel project settings, add these environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `GOOGLE_CSE_ID`: Your Google Custom Search Engine ID
   - `GOOGLE_API_KEY`: Your Google API key for Custom Search

4. **Deploy**:
   - Vercel will automatically deploy your app
   - The frontend will be served from the root domain
   - The Python backend will be available at `/api/*` endpoints

### Alternative: Manual Vercel Deployment

If you prefer to deploy manually:

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Follow the prompts to configure your project
```

## Testing

### Test Google Custom Search

```bash
cd python-backend
python test_search.py
```

This will test:
- Google Custom Search API connectivity
- Sports grounding functionality
- Grounding detection logic

## How Grounding Works

The system uses a two-stage approach:

1. **Primary Response**: Gemini AI responds to user queries using its knowledge
2. **Grounding Check**: The system checks if the response needs current information
3. **Search Integration**: If needed, Google Custom Search finds recent information
4. **Enhanced Response**: Gemini incorporates the search results into a final response

### When Grounding is Triggered

- Queries containing time-sensitive terms (2025, 2026, "latest", "recent")
- When Gemini indicates it doesn't have current information
- Questions about upcoming fixtures, transfers, or breaking news

## Customization

This app is designed for demonstration purposes. Feel free to update the agent prompts, guardrails, and tools to fit your own customer service workflows or experiment with new use cases! The modular structure makes it easy to extend or modify the orchestration logic for your needs.

## Demo Flows

### Demo flow #1 - Current Information

1. **Ask about current fixtures**:
   - User: "What are the Premier League fixtures for 2025/26?"
   - The system will use grounding to find the latest fixture information

2. **Transfer news**:
   - User: "What are the latest Arsenal transfers?"
   - Grounding will search for recent transfer news

3. **Breaking news**:
   - User: "What's the latest sports news?"
   - The system will find current sports headlines

### Demo flow #2 - Historical Information

1. **Ask about past events**:
   - User: "Who won the Premier League in 2023/24?"
   - Gemini will answer using its knowledge (no grounding needed)

2. **Player information**:
   - User: "Tell me about Erling Haaland"
   - Gemini provides comprehensive player information
