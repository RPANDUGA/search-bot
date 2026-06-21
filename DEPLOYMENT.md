# Deployment Guide

## Local Development

### 1. Setup
```bash
# Clone the repository
git clone https://github.com/RPANDUGA/search-bot.git
cd search-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure (Optional)
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your GitHub token
# (Get one at https://github.com/settings/tokens)
```

### 3. Run Locally
```bash
# Terminal 1: Run backend
python search_bot.py
# Server runs on http://localhost:5000

# Terminal 2: Serve frontend
python -m http.server 8000
# Open http://localhost:8000 in browser
```

## Docker Deployment

### Build and Run
```bash
# Build image
docker build -t search-bot .

# Run container
docker run -p 5000:5000 \
  -e GITHUB_TOKEN=your_token_here \
  search-bot

# Or use docker-compose
docker-compose up
```

## Heroku Deployment

### 1. Install Heroku CLI
```bash
# https://devcenter.heroku.com/articles/heroku-cli
heroku login
```

### 2. Create Heroku App
```bash
heroku create your-search-bot-name
```

### 3. Add Buildpack (if needed)
```bash
heroku buildpacks:add heroku/python
```

### 4. Set Environment Variables
```bash
heroku config:set GITHUB_TOKEN=your_token_here
```

### 5. Create Procfile
```
web: gunicorn search_bot:app
```

### 6. Deploy
```bash
git push heroku main

# View logs
heroku logs --tail
```

## AWS Deployment (EC2)

### 1. Launch EC2 Instance
- Ubuntu 22.04 LTS
- Security group: Allow ports 80, 443, 5000

### 2. SSH into Instance
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

### 3. Install Dependencies
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git nginx
```

### 4. Clone and Setup
```bash
cd ~
git clone https://github.com/RPANDUGA/search-bot.git
cd search-bot

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### 5. Configure Nginx
```bash
sudo tee /etc/nginx/sites-available/search-bot > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/search-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. Run with Gunicorn
```bash
gunicorn -w 4 -b 127.0.0.1:5000 search_bot:app
```

### 7. Setup Systemd Service
```bash
sudo tee /etc/systemd/system/search-bot.service > /dev/null <<EOF
[Unit]
Description=Search Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/search-bot
ExecStart=/home/ubuntu/search-bot/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 search_bot:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable search-bot
sudo systemctl start search-bot
```

## Google Cloud Run

### 1. Setup
```bash
gcloud init
gcloud auth login
```

### 2. Create .gcloudignore
```
venv/
__pycache__/
.git/
.DS_Store
```

### 3. Deploy
```bash
gcloud run deploy search-bot \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 4. Set Environment Variables
```bash
gcloud run services update search-bot \
  --update-env-vars GITHUB_TOKEN=your_token_here \
  --region us-central1
```

## Performance Optimization

### 1. Add Caching Headers
Update `search_bot.py`:
```python
@app.after_request
def set_cache_headers(response):
    response.cache_control.max_age = 300
    return response
```

### 2. Add GZIP Compression
```bash
pip install Flask-Compress
```

```python
from flask_compress import Compress
Compress(app)
```

### 3. Use Redis for Caching
```bash
pip install redis
```

### 4. Load Balancing
- Use Nginx with multiple Gunicorn workers
- Deploy on multiple servers with load balancer

## Monitoring

### Application Monitoring
- Use Sentry for error tracking
- Use New Relic for performance monitoring
- Use DataDog for comprehensive monitoring

### Health Checks
```bash
# Test endpoint
curl http://localhost:5000/health
```

## Troubleshooting

### Issue: High Memory Usage
- Reduce RESULTS_PER_PAGE
- Implement database pagination
- Use Redis for caching

### Issue: Slow Wikipedia Searches
- Wikipedia API can be slow sometimes
- Results are cached for 5 minutes
- Consider adding rate limiting

### Issue: GitHub API Rate Limit
- Add GITHUB_TOKEN environment variable
- Rate limit increases from 60 to 5000 requests/hour
