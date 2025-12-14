# 🚀 AI Financial Coach - Setup & Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [PostgreSQL Configuration](#postgresql-configuration)
4. [API Keys Setup](#api-keys-setup)
5. [Running the Application](#running-the-application)
6. [Production Deployment](#production-deployment)
7. [Docker Deployment](#docker-deployment)
8. [Troubleshooting](#troubleshooting)
9. [Performance Optimization](#performance-optimization)
10. [Backup & Maintenance](#backup--maintenance)

---

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: Version 3.9, 3.10, 3.11, or 3.12
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Disk Space**: Minimum 5GB free space
- **PostgreSQL**: Version 12 or higher

### Required Accounts
1. **OpenRouter Account** - https://openrouter.ai/
   - Sign up for an account
   - Add credits (minimum $5 recommended)
   - Generate API key

2. **OpenAI Account** - https://platform.openai.com/
   - Create account
   - Add payment method
   - Generate API key

3. **PostgreSQL Database**
   - Local installation OR
   - Cloud hosted (ElephantSQL, Supabase, AWS RDS, etc.)

---

## Local Development Setup

### Step 1: Install Python

**Windows:**
```bash
# Download from python.org
# Ensure "Add Python to PATH" is checked during installation
python --version
```

**macOS:**
```bash
# Using Homebrew
brew install python@3.11

# Verify installation
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
python3.11 --version
```

### Step 2: Install PostgreSQL

**Windows:**
```bash
# Download installer from postgresql.org
# Run installer and remember the password you set
```

**macOS:**
```bash
# Using Homebrew
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Step 3: Clone Repository

```bash
# Using HTTPS
git clone https://github.com/yourusername/fincoach.git
cd fincoach

# OR using SSH
git clone git@github.com:yourusername/fincoach.git
cd fincoach
```

### Step 4: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal.

### Step 5: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

**Common Installation Issues:**

**Issue 1: psycopg2 compilation error**
```bash
# Solution: Use binary version
pip uninstall psycopg2
pip install psycopg2-binary
```

**Issue 2: ChromaDB installation fails**
```bash
# Solution: Install build tools
# Windows: Install Visual C++ Build Tools
# Linux: sudo apt install build-essential
# macOS: xcode-select --install
```

---

## PostgreSQL Configuration

### Step 1: Create Database

**Method 1: Using psql (Command Line)**
```bash
# Login to PostgreSQL
sudo -u postgres psql  # Linux/Mac
psql -U postgres       # Windows

# In PostgreSQL prompt
CREATE DATABASE fincoach_db;
CREATE USER fincoach_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE fincoach_db TO fincoach_user;
\q
```

**Method 2: Using pgAdmin (GUI)**
1. Open pgAdmin
2. Right-click Databases → Create → Database
3. Name: `fincoach_db`
4. Owner: Create new role `fincoach_user`
5. Save

### Step 2: Test Database Connection

```bash
# Test connection
psql -h localhost -U fincoach_user -d fincoach_db

# If successful, you'll see:
# fincoach_db=>
```

### Step 3: Configure Connection String

Format:
```
postgresql+psycopg2://username:password@host:port/database_name
```

Examples:
```bash
# Local database
DATABASE_URL=postgresql+psycopg2://fincoach_user:password123@localhost:5432/fincoach_db

# Cloud database (ElephantSQL example)
DATABASE_URL=postgresql+psycopg2://user:pass@tiny.db.elephantsql.com:5432/database

# AWS RDS example
DATABASE_URL=postgresql+psycopg2://admin:pass@mydb.xxxxxx.us-east-1.rds.amazonaws.com:5432/fincoach

# Supabase example
DATABASE_URL=postgresql+psycopg2://postgres:pass@db.xxxxx.supabase.co:5432/postgres
```

---

## API Keys Setup

### Step 1: Create .env File

Create a file named `.env` in the project root directory:

```bash
# Navigate to project root
cd fincoach

# Create .env file
# Windows
type nul > .env

# Linux/Mac
touch .env
```

### Step 2: Configure Environment Variables

Edit `.env` file with your favorite text editor:

```env
# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DATABASE_URL=postgresql+psycopg2://fincoach_user:your_password@localhost:5432/fincoach_db

# ============================================================================
# API KEYS
# ============================================================================
# OpenRouter API Key (for Claude 3.5 Sonnet)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI API Key (for embeddings)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================
APP_NAME=AI Financial Coach
SECRET_KEY=your-super-secret-key-change-this-in-production-minimum-32-characters
DEBUG=False

# ============================================================================
# STREAMLIT SETTINGS (Optional)
# ============================================================================
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# ============================================================================
# VECTOR STORE SETTINGS
# ============================================================================
CHROMA_PERSIST_DIRECTORY=./chroma_db
EMBEDDING_MODEL=text-embedding-3-small

# ============================================================================
# FILE UPLOAD SETTINGS
# ============================================================================
MAX_UPLOAD_SIZE_MB=50
UPLOAD_DIRECTORY=./uploads
ALLOWED_EXTENSIONS=pdf,xlsx,csv,xls,doc,docx

# ============================================================================
# AGENT SETTINGS
# ============================================================================
DEFAULT_AGENT_MODEL=anthropic/claude-3.5-sonnet
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=2000
```

### Step 3: Generate Secure Secret Key

**Python Method:**
```python
import secrets
print(secrets.token_urlsafe(32))
# Copy the output to SECRET_KEY in .env
```

**OpenSSL Method:**
```bash
openssl rand -hex 32
```

### Step 4: Protect .env File

**Add to .gitignore:**
```bash
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "chroma_db/" >> .gitignore
echo "uploads/" >> .gitignore
```

---

## Running the Application

### Step 1: Initialize Database

```bash
# Make sure virtual environment is activated
# (venv) should be visible in terminal

# Initialize database tables
python -m database.models

# You should see: "Database tables created successfully!"
```

### Step 2: Create Required Directories

```bash
# Create necessary directories
mkdir -p uploads
mkdir -p chroma_db

# Verify creation
ls -la
```

### Step 3: Start Streamlit Application

**Development Mode:**
```bash
streamlit run app.py
```

**Custom Port:**
```bash
streamlit run app.py --server.port 8080
```

**Network Access:**
```bash
streamlit run app.py --server.address 0.0.0.0
```

**With Logging:**
```bash
streamlit run app.py --logger.level debug > app.log 2>&1
```

### Step 4: Access Application

Open browser and navigate to:
```
http://localhost:8501
```

### Step 5: Create First User

1. Click on "Register" tab
2. Fill in details:
   - Username: admin
   - Email: admin@fincoach.com
   - Password: (minimum 8 characters)
3. Click Register
4. Login with credentials

---

## Production Deployment

### Option 1: Streamlit Cloud

1. **Push to GitHub:**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy on Streamlit Cloud:**
   - Visit https://streamlit.io/cloud
   - Connect GitHub repository
   - Select `app.py` as main file
   - Add environment variables (from .env)
   - Deploy

3. **Configure Secrets:**
   - Go to App Settings → Secrets
   - Add all .env variables
   - Format:
   ```toml
   DATABASE_URL = "postgresql://..."
   OPENROUTER_API_KEY = "sk-or-..."
   OPENAI_API_KEY = "sk-..."
   ```

### Option 2: Heroku Deployment

1. **Install Heroku CLI:**
```bash
# Download from heroku.com/cli
heroku --version
```

2. **Login:**
```bash
heroku login
```

3. **Create App:**
```bash
heroku create fincoach-app
```

4. **Add PostgreSQL:**
```bash
heroku addons:create heroku-postgresql:mini
```

5. **Set Environment Variables:**
```bash
heroku config:set OPENROUTER_API_KEY=your_key
heroku config:set OPENAI_API_KEY=your_key
heroku config:set SECRET_KEY=your_secret
```

6. **Create Procfile:**
```bash
echo "web: sh setup.sh && streamlit run app.py" > Procfile
```

7. **Create setup.sh:**
```bash
cat > setup.sh << 'EOF'
mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
EOF
```

8. **Deploy:**
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Option 3: AWS EC2 Deployment

1. **Launch EC2 Instance:**
   - Ubuntu 22.04 LTS
   - t2.medium or larger
   - Open ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)

2. **Connect to Instance:**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. **Install Dependencies:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv nginx postgresql
```

4. **Setup Application:**
```bash
git clone https://github.com/yourusername/fincoach.git
cd fincoach
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Configure Nginx:**
```nginx
# /etc/nginx/sites-available/fincoach
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

6. **Enable Site:**
```bash
sudo ln -s /etc/nginx/sites-available/fincoach /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

7. **Create Systemd Service:**
```bash
# /etc/systemd/system/fincoach.service
[Unit]
Description=AI Financial Coach
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/fincoach
Environment="PATH=/home/ubuntu/fincoach/venv/bin"
ExecStart=/home/ubuntu/fincoach/venv/bin/streamlit run app.py --server.port 8501

[Install]
WantedBy=multi-user.target
```

8. **Start Service:**
```bash
sudo systemctl enable fincoach
sudo systemctl start fincoach
sudo systemctl status fincoach
```

---

## Docker Deployment

### Step 1: Create Dockerfile

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p uploads chroma_db

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: fincoach_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: fincoach_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fincoach_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  fincoach:
    build: .
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql+psycopg2://fincoach_user:${DB_PASSWORD}@postgres:5432/fincoach_db
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    ports:
      - "8501:8501"
    volumes:
      - ./uploads:/app/uploads
      - ./chroma_db:/app/chroma_db
    restart: unless-stopped

volumes:
  postgres_data:
```

### Step 3: Create .env.docker

```env
DB_PASSWORD=your_secure_password
OPENROUTER_API_KEY=your_key
OPENAI_API_KEY=your_key
SECRET_KEY=your_secret_key
```

### Step 4: Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Troubleshooting

### Issue 1: Database Connection Failed

**Error:** `could not connect to server`

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# Check connection
psql -h localhost -U fincoach_user -d fincoach_db

# Verify DATABASE_URL in .env
echo $DATABASE_URL
```

### Issue 2: Import Errors

**Error:** `ModuleNotFoundError: No module named 'xxx'`

**Solution:**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Check virtual environment is activated
which python  # should show venv path
```

### Issue 3: ChromaDB Errors

**Error:** `Failed to initialize ChromaDB`

**Solution:**
```bash
# Delete and recreate
rm -rf chroma_db
mkdir chroma_db

# Restart application
```

### Issue 4: OpenRouter API Errors

**Error:** `Authentication failed`

**Solution:**
```bash
# Check API key in .env
# Verify credits at openrouter.ai
# Test API key:
curl https://openrouter.ai/api/v1/auth/key \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

---

## Performance Optimization

### 1. Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_user_id ON documents(user_id);
CREATE INDEX idx_financial_user_id ON financial_data(user_id);
CREATE INDEX idx_chat_user_id ON chat_history(user_id);
CREATE INDEX idx_document_type ON documents(document_type);
```

### 2. Streamlit Caching

Add to pages:
```python
@st.cache_data
def load_user_data(user_id):
    # Expensive operations
    pass

@st.cache_resource
def initialize_agents():
    # Initialize once
    pass
```

### 3. Environment Variables

```env
# In .streamlit/config.toml
[server]
maxUploadSize = 50
enableCORS = false
enableXsrfProtection = true

[runner]
fastReruns = true
```

---

## Backup & Maintenance

### Database Backup

```bash
# Backup database
pg_dump -U fincoach_user fincoach_db > backup_$(date +%Y%m%d).sql

# Restore database
psql -U fincoach_user fincoach_db < backup_20240101.sql
```

### Automated Backup (Cron)

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * pg_dump -U fincoach_user fincoach_db > /backups/fincoach_$(date +\%Y\%m\%d).sql
```

### Update Dependencies

```bash
# Check outdated packages
pip list --outdated

# Update specific package
pip install --upgrade streamlit

# Update all (carefully!)
pip install --upgrade -r requirements.txt
```

---

## Monitoring & Logs

### View Application Logs

```bash
# Streamlit logs
tail -f ~/.streamlit/logs/streamlit.log

# System service logs
sudo journalctl -u fincoach -f

# Docker logs
docker-compose logs -f fincoach
```

### Monitor Resources

```bash
# CPU/Memory usage
htop

# Database connections
SELECT count(*) FROM pg_stat_activity;

# Disk usage
df -h
```

---

**For additional support, refer to the main README.md or create an issue on GitHub.**
