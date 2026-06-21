# 🔍 Search Bot

A full-featured search bot built with GitHub and Wikipedia API integration, advanced filtering, sorting, and pagination.

## Features

✅ **Multi-Source Search**
- Local database search
- GitHub repositories search
- Wikipedia articles search

✅ **Advanced Features**
- Real-time search with debouncing
- Filtering by source (GitHub, Wikipedia, Local)
- Sorting (Relevance, Date, Stars/Views)
- Pagination (10 results per page)
- Responsive design
- Error handling & loading states

✅ **Performance**
- Cached API responses
- Minimal API calls
- Fast filtering and sorting

## Quick Start

### 1. Install Dependencies
```bash
pip install flask flask-cors requests
```

### 2. Run Backend
```bash
python search_bot.py
```

Server runs on `http://localhost:5000`

### 3. Open Frontend
Simply open `index.html` in your browser (or serve with a local server):
```bash
python -m http.server 8000
# Then visit http://localhost:8000
```

## API Endpoints

### POST `/search`
Search across all sources

**Request:**
```json
{
  "query": "python",
  "source": "all",
  "sort": "relevance",
  "page": 1
}
```

**Response:**
```json
{
  "query": "python",
  "count": 15,
  "total_pages": 2,
  "current_page": 1,
  "results": [
    {
      "id": "1",
      "title": "Python Tutorial",
      "source": "local",
      "url": "https://python.org",
      "description": "Learn Python",
      "tags": ["python", "tutorial"],
      "timestamp": "2026-06-21T10:00:00"
    }
  ]
}
```

### GET `/health`
Health check endpoint

## Configuration

### GitHub API
Set your GitHub token (optional, for higher rate limits):
```python
GITHUB_TOKEN = "your_token_here"
```

### Results Per Page
Edit in `search_bot.py`:
```python
RESULTS_PER_PAGE = 10
```

## File Structure
```
search-bot/
├── search_bot.py          # Backend API
├── index.html             # Frontend UI
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── .env.example           # Environment variables template
```

## Customization

### Add More Local Data
Edit the `LOCAL_DATA` array in `search_bot.py`:
```python
LOCAL_DATA = [
    {
        "id": "custom-1",
        "title": "Your Title",
        "url": "https://example.com",
        "description": "Description",
        "tags": ["tag1", "tag2"],
        "timestamp": "2026-06-21T10:00:00"
    }
]
```

### Integrate More APIs
Add new search functions in `search_bot.py`:
```python
def search_custom_api(query):
    # Your API integration here
    pass
```

Then add to the search pipeline in the `/search` endpoint.

## Performance Tips

1. **Cache responses** - API results are cached for 5 minutes
2. **Limit results** - Wikipedia returns max 5 results per search
3. **Rate limits** - GitHub has 60 req/hour (authenticated: 5000/hour)
4. **Pagination** - Always use pagination for large result sets

## Troubleshooting

**Issue: Backend connection error**
- Ensure `search_bot.py` is running on port 5000
- Check firewall settings

**Issue: No GitHub results**
- GitHub API might be rate limited
- Add your GitHub token for higher limits

**Issue: Slow searches**
- Wikipedia API can be slow sometimes
- Results are cached, so second searches are faster

## Deploy to Production

### Heroku
```bash
heroku create your-app-name
git push heroku main
```

### Docker
```bash
docker build -t search-bot .
docker run -p 5000:5000 search-bot
```

## License

MIT License - Feel free to use and modify!

## Credits

Built with Flask, GitHub API, and Wikipedia API
