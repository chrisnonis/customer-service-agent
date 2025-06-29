# How to Preview Your UK Sports Agent System

## Quick Start

### 1. Set Up Environment Variables

First, create your `.env` file in the `python-backend` folder:

```bash
cd python-backend
cp .env.example .env
```

Edit the `.env` file and add your API keys:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
GOOGLE_CUSTOM_SEARCH_API_KEY=your_google_custom_search_api_key_here
GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your_google_custom_search_engine_id_here
```

### 2. Install Dependencies

**Backend:**
```bash
cd python-backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd ui
npm install
```

### 3. Test Your Setup

**Test environment variables:**
```bash
cd python-backend
python check_environment.py
```

**Test the complete system:**
```bash
cd python-backend
python test_system.py
```

### 4. Run the Application

**Option A: Run both together (recommended):**
```bash
cd ui
npm run dev
```

**Option B: Run separately:**

Terminal 1 (Backend):
```bash
cd python-backend
python run_backend.py
```

Terminal 2 (Frontend):
```bash
cd ui
npm run dev:next
```

## Access Points

- **Frontend:** http://localhost:3000
- **Backend API:** http://127.0.0.1:8000
- **Health Check:** http://127.0.0.1:8000/health
- **API Docs:** http://127.0.0.1:8000/docs

## Testing the System

### Sample Queries to Try:

1. **Premier League Knowledge:**
   - "What's the current Premier League table?"
   - "Tell me about Arsenal's history"
   - "Who is Erling Haaland?"

2. **Championship Information:**
   - "Which teams are in the Championship promotion race?"
   - "Tell me about Leicester City"

3. **Boxing Knowledge:**
   - "Who is Tyson Fury?"
   - "What are the heavyweight divisions?"

4. **Current Information (triggers grounding):**
   - "What are Chelsea's fixtures for 2025/26?"
   - "Latest Arsenal transfers"
   - "Recent boxing news"

5. **Sports News:**
   - "What's the latest sports news?"
   - "Any recent transfer news?"

## Troubleshooting

### Common Issues:

1. **"Missing environment variables"**
   - Make sure your `.env` file is in the `python-backend` folder
   - Check that all three API keys are set

2. **"Rate limit exceeded"**
   - You've hit the Gemini API quota
   - Wait for quota reset or upgrade your plan

3. **"Backend not available"**
   - Make sure the Python backend is running on port 8000
   - Check the terminal for error messages

4. **"Search not working"**
   - Verify your Google Custom Search API key and Engine ID
   - Make sure the Custom Search API is enabled in Google Cloud Console

### Debug Commands:

```bash
# Check environment
cd python-backend && python check_environment.py

# Test system functionality
cd python-backend && python test_system.py

# Test search functionality
cd python-backend && python test_search.py

# Test enhanced scraping
cd python-backend && python enhanced_scraping.py
```

## What's New in the Improved Version

### 🚀 Performance Improvements:
- Caching layer for search results
- Better error handling with retry logic
- Connection pooling and timeouts

### 🛡️ Enhanced Security:
- Input validation and sanitization
- Request size limits
- Better CORS configuration

### 📊 Better Monitoring:
- Comprehensive logging
- Health check endpoints
- Performance metrics

### 🗄️ Persistent Storage:
- SQLite database for conversations
- Automatic cleanup of old conversations
- Better state management

### 🤖 Smarter AI:
- Improved grounding detection
- Context-aware responses
- Better agent routing

## Production Deployment

For production deployment, see the main README.md file for Vercel deployment instructions.

The improved system is more robust and production-ready!