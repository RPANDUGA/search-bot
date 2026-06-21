FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY search_bot.py .
COPY index.html .

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=search_bot.py
ENV FLASK_ENV=production

# Run the application
CMD ["python", "search_bot.py"]
