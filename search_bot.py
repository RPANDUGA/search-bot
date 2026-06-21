from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
import json
from urllib.parse import quote
import os

app = Flask(__name__)
CORS(app)

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")  # Optional: Set for higher rate limits
RESULTS_PER_PAGE = 10
CACHE_DURATION = 300  # 5 minutes

# Simple in-memory cache
cache = {}

# Local database
LOCAL_DATA = [
    {
        "id": "local-1",
        "title": "Python Tutorial",
        "source": "local",
        "url": "https://docs.python.org",
        "description": "Official Python documentation and tutorials",
        "tags": ["python", "tutorial", "programming"],
        "timestamp": "2026-06-21T10:00:00",
        "relevance_score": 0
    },
    {
        "id": "local-2",
        "title": "JavaScript Guide",
        "source": "local",
        "url": "https://javascript.info",
        "description": "Modern JavaScript guide and reference",
        "tags": ["javascript", "web", "programming"],
        "timestamp": "2026-06-20T10:00:00",
        "relevance_score": 0
    },
    {
        "id": "local-3",
        "title": "Web Development Roadmap",
        "source": "local",
        "url": "https://roadmap.sh/frontend",
        "description": "Complete roadmap for web development",
        "tags": ["web", "development", "learning"],
        "timestamp": "2026-06-19T10:00:00",
        "relevance_score": 0
    },
    {
        "id": "local-4",
        "title": "GitHub Documentation",
        "source": "local",
        "url": "https://docs.github.com",
        "description": "Official GitHub help and documentation",
        "tags": ["github", "version-control", "git"],
        "timestamp": "2026-06-18T10:00:00",
        "relevance_score": 0
    },
    {
        "id": "local-5",
        "title": "React Documentation",
        "source": "local",
        "url": "https://react.dev",
        "description": "React library documentation and guides",
        "tags": ["react", "javascript", "frontend"],
        "timestamp": "2026-06-17T10:00:00",
        "relevance_score": 0
    }
]

def is_cache_valid(cache_key):
    """Check if cache entry is still valid"""
    if cache_key not in cache:
        return False
    timestamp, _ = cache[cache_key]
    return datetime.now() - timestamp < timedelta(seconds=CACHE_DURATION)

def get_cache(cache_key):
    """Get value from cache if valid"""
    if is_cache_valid(cache_key):
        return cache[cache_key][1]
    return None

def set_cache(cache_key, value):
    """Set cache value with timestamp"""
    cache[cache_key] = (datetime.now(), value)

def calculate_relevance(item, query):
    """Calculate relevance score for an item"""
    query_lower = query.lower()
    score = 0
    
    # Title match (highest priority)
    if query_lower in item["title"].lower():
        score += 100
    
    # Description match
    if query_lower in item["description"].lower():
        score += 50
    
    # Tag matches
    if any(query_lower in tag.lower() for tag in item["tags"]):
        score += 25
    
    # Partial word matches in title
    title_words = item["title"].lower().split()
    if any(query_lower in word for word in title_words):
        score += 10
    
    return score

def search_local(query):
    """Search in local database"""
    results = []
    
    for item in LOCAL_DATA:
        score = calculate_relevance(item, query)
        if score > 0:
            item["relevance_score"] = score
            results.append(item)
    
    return results

def search_github(query):
    """Search GitHub repositories"""
    cache_key = f"github_{query}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    
    try:
        headers = {}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
        
        url = f"https://api.github.com/search/repositories?q={quote(query)}&sort=stars&order=desc&per_page=5"
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        results = []
        
        for repo in data.get("items", []):
            results.append({
                "id": f"github-{repo['id']}",
                "title": repo["name"],
                "source": "github",
                "url": repo["html_url"],
                "description": repo["description"] or "No description",
                "tags": [repo["language"].lower() if repo["language"] else "programming", "repository"],
                "timestamp": repo["updated_at"],
                "stars": repo["stargazers_count"],
                "relevance_score": calculate_relevance({
                    "title": repo["name"],
                    "description": repo["description"] or "",
                    "tags": [repo["language"] or "programming"]
                }, query)
            })
        
        set_cache(cache_key, results)
        return results
    except Exception as e:
        print(f"GitHub search error: {e}")
        return []

def search_wikipedia(query):
    """Search Wikipedia articles"""
    cache_key = f"wikipedia_{query}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 5
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        results = []
        
        for article in data.get("query", {}).get("search", []):
            # Get full article URL
            article_url = f"https://en.wikipedia.org/wiki/{quote(article['title'].replace(' ', '_'))}"
            
            results.append({
                "id": f"wiki-{article['pageid']}",
                "title": article["title"],
                "source": "wikipedia",
                "url": article_url,
                "description": article["snippet"].replace("<span class='searchmatch'>", "").replace("</span>", ""),
                "tags": ["wikipedia", "article", "reference"],
                "timestamp": datetime.now().isoformat(),
                "relevance_score": calculate_relevance({
                    "title": article["title"],
                    "description": article["snippet"],
                    "tags": ["article"]
                }, query)
            })
        
        set_cache(cache_key, results)
        return results
    except Exception as e:
        print(f"Wikipedia search error: {e}")
        return []

def combine_and_filter(results, source_filter="all"):
    """Combine results from all sources and apply filters"""
    all_results = results
    
    # Filter by source
    if source_filter != "all":
        all_results = [r for r in all_results if r["source"] == source_filter]
    
    return all_results

def sort_results(results, sort_by="relevance"):
    """Sort results based on specified criteria"""
    if sort_by == "relevance":
        return sorted(results, key=lambda x: x.get("relevance_score", 0), reverse=True)
    elif sort_by == "date":
        return sorted(results, key=lambda x: x.get("timestamp", ""), reverse=True)
    elif sort_by == "stars":
        return sorted(results, key=lambda x: x.get("stars", 0), reverse=True)
    else:
        return results

def paginate_results(results, page=1, per_page=RESULTS_PER_PAGE):
    """Paginate results"""
    total = len(results)
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    
    # Ensure page is valid
    page = max(1, min(page, total_pages if total_pages > 0 else 1))
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    return {
        "items": results[start_idx:end_idx],
        "current_page": page,
        "total_pages": total_pages,
        "total_count": total,
        "per_page": per_page
    }

@app.route("/search", methods=["POST"])
def search():
    """Main search endpoint"""
    try:
        data = request.json or {}
        query = data.get("query", "").strip()
        source = data.get("source", "all").lower()  # all, local, github, wikipedia
        sort_by = data.get("sort", "relevance").lower()  # relevance, date, stars
        page = data.get("page", 1)
        
        # Validate inputs
        if not query or len(query) < 2:
            return jsonify({"error": "Query must be at least 2 characters"}), 400
        
        if not isinstance(page, int) or page < 1:
            page = 1
        
        if source not in ["all", "local", "github", "wikipedia"]:
            source = "all"
        
        if sort_by not in ["relevance", "date", "stars"]:
            sort_by = "relevance"
        
        # Perform searches
        results = []
        
        if source in ["all", "local"]:
            results.extend(search_local(query))
        
        if source in ["all", "github"]:
            results.extend(search_github(query))
        
        if source in ["all", "wikipedia"]:
            results.extend(search_wikipedia(query))
        
        # Apply sorting
        results = sort_results(results, sort_by)
        
        # Apply pagination
        paginated = paginate_results(results, page)
        
        return jsonify({
            "query": query,
            "source": source,
            "sort": sort_by,
            "count": len(paginated["items"]),
            "total_count": paginated["total_count"],
            "current_page": paginated["current_page"],
            "total_pages": paginated["total_pages"],
            "results": paginated["items"]
        })
    
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route("/stats", methods=["GET"])
def stats():
    """Get search statistics"""
    return jsonify({
        "local_items": len(LOCAL_DATA),
        "cache_size": len(cache),
        "cache_duration_seconds": CACHE_DURATION,
        "results_per_page": RESULTS_PER_PAGE,
        "timestamp": datetime.now().isoformat()
    })

@app.route("/", methods=["GET"])
def index():
    """Serve API documentation"""
    return jsonify({
        "name": "Search Bot API",
        "version": "1.0.0",
        "endpoints": {
            "POST /search": "Search across all sources",
            "GET /health": "Health check",
            "GET /stats": "API statistics"
        },
        "documentation": "https://github.com/RPANDUGA/search-bot"
    })

if __name__ == "__main__":
    print("🚀 Search Bot API starting on http://localhost:5000")
    print("📖 Open http://localhost:8000 to access the frontend")
    print("💡 Set GITHUB_TOKEN environment variable for higher API limits")
    app.run(debug=True, port=5000)