#!/usr/bin/env python3
"""
Deployment Configuration for Brahmakaal Enterprise API
Free hosting options and deployment instructions
"""

import os
import json
from datetime import datetime

def create_deployment_configs():
    """Create deployment configuration files"""
    
    print("🚀 Creating Deployment Configurations...")
    print("=" * 60)
    
    # 1. Railway.app Configuration
    railway_config = {
        "name": "brahmakaal-api",
        "description": "Vedic Astronomy Enterprise API",
        "build": {
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": "python start_api.py"
        },
        "env": {
            "PORT": "8000",
            "ENVIRONMENT": "production",
            "DATABASE_URL": "${{Postgres.DATABASE_URL}}",
            "JWT_SECRET_KEY": "your-super-secret-jwt-key-change-this-in-production",
            "EMAIL_ENABLED": "true",
            "SMTP_HOST": "smtp.zoho.in",
            "SMTP_PORT": "465",
            "SMTP_USER": "aham@brah.ma",
            "SMTP_PASS": "6whrzKc*@brahma",
            "SMTP_SECURE": "true",
            "EMAIL_FROM": "aham@brah.ma",
            "WEBHOOK_ENABLED": "true",
            "CORS_ORIGINS": "*"
        }
    }
    
    with open("railway.json", "w") as f:
        json.dump(railway_config, f, indent=2)
    
    # 2. Render.com Configuration
    render_config = {
        "services": [
            {
                "type": "web",
                "name": "brahmakaal-api",
                "env": "python",
                "plan": "free",
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "python start_api.py",
                "envVars": [
                    {"key": "PORT", "value": "8000"},
                    {"key": "ENVIRONMENT", "value": "production"},
                    {"key": "JWT_SECRET_KEY", "value": "your-super-secret-jwt-key-change-this"},
                    {"key": "EMAIL_ENABLED", "value": "true"},
                    {"key": "SMTP_HOST", "value": "smtp.zoho.in"},
                    {"key": "SMTP_PORT", "value": "465"},
                    {"key": "SMTP_USER", "value": "aham@brah.ma"},
                    {"key": "SMTP_PASS", "value": "6whrzKc*@brahma"},
                    {"key": "WEBHOOK_ENABLED", "value": "true"}
                ]
            }
        ],
        "databases": [
            {
                "name": "brahmakaal-postgres",
                "plan": "free"
            }
        ]
    }
    
    with open("render.yaml", "w") as f:
        json.dump(render_config, f, indent=2)
    
    # 3. Heroku Configuration
    procfile_content = "web: python start_api.py"
    with open("Procfile", "w") as f:
        f.write(procfile_content)
    
    # 4. Docker Configuration
    dockerfile_content = """# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start the application
CMD ["python", "start_api.py"]
"""
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    # 5. Docker Compose for local development
    docker_compose_content = """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/brahmakaal
      - JWT_SECRET_KEY=dev-secret-key
      - EMAIL_ENABLED=true
      - SMTP_HOST=smtp.zoho.in
      - SMTP_PORT=465
      - SMTP_USER=aham@brah.ma
      - SMTP_PASS=6whrzKc*@brahma
      - WEBHOOK_ENABLED=true
    depends_on:
      - db
    volumes:
      - .:/app

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=brahmakaal
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""
    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose_content)
    
    # 6. Production start script
    start_script_content = """#!/usr/bin/env python3
import os
import uvicorn
from kaal_engine.api.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    uvicorn.run(
        "kaal_engine.api.app:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
"""
    with open("start_production.py", "w") as f:
        f.write(start_script_content)
    
    print("✅ Configuration files created:")
    print("   📁 railway.json - Railway.app deployment")
    print("   📁 render.yaml - Render.com deployment")
    print("   📁 Procfile - Heroku deployment")
    print("   📁 Dockerfile - Docker containerization")
    print("   📁 docker-compose.yml - Local development")
    print("   📁 start_production.py - Production server")

def print_deployment_guide():
    """Print deployment guide for free hosting options"""
    
    print("\n" + "=" * 80)
    print("🌐 FREE HOSTING OPTIONS FOR BRAHMAKAAL API")
    print("=" * 80)
    
    print("\n🚀 **OPTION 1: RAILWAY.APP (RECOMMENDED)**")
    print("-" * 50)
    print("✅ Free Plan: 512MB RAM, $5 credit monthly")
    print("✅ PostgreSQL database included")
    print("✅ Automatic deployments from GitHub")
    print("✅ Custom domains supported")
    print("\n📋 Setup Steps:")
    print("1. Push code to GitHub repository")
    print("2. Sign up at railway.app with GitHub")
    print("3. Create new project from GitHub repo")
    print("4. Add PostgreSQL service")
    print("5. Deploy automatically!")
    print("\n🔗 URL: https://railway.app")
    
    print("\n🌟 **OPTION 2: RENDER.COM**")
    print("-" * 50)
    print("✅ Free Plan: 512MB RAM, sleeps after 15min")
    print("✅ PostgreSQL database (90 days free)")
    print("✅ Automatic SSL certificates")
    print("✅ GitHub integration")
    print("\n📋 Setup Steps:")
    print("1. Push code to GitHub")
    print("2. Sign up at render.com")
    print("3. Create Web Service from repo")
    print("4. Add PostgreSQL database")
    print("5. Configure environment variables")
    print("\n🔗 URL: https://render.com")
    
    print("\n☁️ **OPTION 3: HEROKU**")
    print("-" * 50)
    print("✅ Free Plan: 512MB RAM (with credit card)")
    print("✅ PostgreSQL addon available")
    print("✅ Easy CLI deployment")
    print("✅ Extensive documentation")
    print("\n📋 Setup Steps:")
    print("1. Install Heroku CLI")
    print("2. heroku create brahmakaal-api")
    print("3. heroku addons:create heroku-postgresql:mini")
    print("4. git push heroku main")
    print("\n🔗 URL: https://heroku.com")
    
    print("\n🐳 **OPTION 4: DOCKER + FREE VPS**")
    print("-" * 50)
    print("✅ Oracle Cloud: Always free tier")
    print("✅ Google Cloud: $300 credit")
    print("✅ AWS: 12 months free tier")
    print("✅ Full control over environment")
    print("\n📋 Setup Steps:")
    print("1. Get free VPS (Oracle/GCP/AWS)")
    print("2. Install Docker and Docker Compose")
    print("3. git clone your repository")
    print("4. docker-compose up -d")
    
    print("\n💡 **RECOMMENDATION FOR TESTING:**")
    print("-" * 50)
    print("🥇 **Railway.app** - Best for quick deployment")
    print("   • No sleep mode unlike Render")
    print("   • Good performance on free tier")
    print("   • Postgres included")
    print("   • Your API will be at: https://brahmakaal-api.railway.app")
    
    print("\n⚙️ **ENVIRONMENT VARIABLES NEEDED:**")
    print("-" * 50)
    print("DATABASE_URL=postgresql://...")
    print("JWT_SECRET_KEY=your-secret-key")
    print("EMAIL_ENABLED=true")
    print("SMTP_HOST=smtp.zoho.in")
    print("SMTP_PORT=465")
    print("SMTP_USER=aham@brah.ma")
    print("SMTP_PASS=6whrzKc*@brahma")
    print("WEBHOOK_ENABLED=true")
    print("CORS_ORIGINS=*")
    
    print("\n🔑 **YOUR NEVER-EXPIRING TOKEN:**")
    print("-" * 50)
    print("Run: python generate_never_expiring_token.py")
    print("Use the token for all API testing")
    print("Token never expires - perfect for testing!")

if __name__ == "__main__":
    create_deployment_configs()
    print_deployment_guide()
