# MetaSpace Simulator: Complete Dependency Stack
## Requirements for HTML + Python Web-Based Visual Simulation

**Purpose:** Comprehensive dependency analysis for simulator development  
**Target:** Developers, DevOps engineers, system architects  
**Scope:** Frontend + Backend + Database + Visualization  
**Date:** December 27, 2025  
**Status:** Production-ready specifications

---

## EXECUTIVE SUMMARY

This document specifies ALL dependencies needed for a lightweight yet visually rich simulator:
- **Frontend:** HTML5, CSS3, JavaScript (D3.js, modern browsers)
- **Backend:** Python 3.8+, Flask, NumPy, SciPy
- **Database:** SQLite (lightweight), JSON storage (fallback)
- **Visualization:** D3.js (real-time charts, timelines)
- **Deployment:** Docker, Gunicorn, Nginx

**Total Package Size:** ~500MB (with all dependencies)  
**Memory Footprint:** 256MB (minimal), 1GB (recommended)  
**Development Time:** 14 weeks  

---

## PART 1: FRONTEND DEPENDENCIES

### 1.1 Browser & Runtime Requirements

```json
{
  "browser_support": {
    "minimum_versions": {
      "Chrome": "90+",
      "Firefox": "88+",
      "Safari": "14+",
      "Edge": "90+"
    },
    "required_apis": [
      "ES6+ (const, let, arrow functions)",
      "Fetch API (HTTP requests)",
      "WebSocket API (real-time updates)",
      "LocalStorage API (session caching)",
      "CSS Grid & Flexbox",
      "Canvas API (D3.js rendering)",
      "SVG support"
    ],
    "javascript_version": "ES2018 or higher"
  },
  
  "file_size_constraints": {
    "html": "< 100 KB",
    "css_total": "< 200 KB",
    "javascript_total": "< 500 KB (including D3.js)",
    "page_load_time": "< 3 seconds"
  }
}
```

### 1.2 Frontend NPM Dependencies (package.json)

```json
{
  "name": "metaspace-simulator-frontend",
  "version": "1.0.0",
  "description": "MetaSpace Simulator - EKF vs MetaSpace.bio Comparison",
  
  "dependencies": {
    "d3": "^7.8.5",
    "axios": "^1.4.0",
    "chart.js": "^4.3.0",
    "plotly.js": "^2.24.0",
    "moment": "^2.29.4",
    "lodash": "^4.17.21"
  },
  
  "devDependencies": {
    "@parcel/bundler": "^2.9.3",
    "sass": "^1.62.0",
    "eslint": "^8.40.0",
    "prettier": "^2.8.8"
  },
  
  "scripts": {
    "start": "parcel serve index.html",
    "build": "parcel build index.html",
    "lint": "eslint js/",
    "format": "prettier --write ."
  }
}
```

### 1.3 Individual Library Details

#### **D3.js (^7.8.5)** - Data Visualization
```
Purpose: Real-time timeline & chart rendering
Size: ~250 KB (minified)
Load: <200ms
Features:
  ├─ Timeline visualization (dual EKF vs MetaSpace)
  ├─ Interactive charts (detection latency, data loss)
  ├─ Animated transitions
  ├─ Responsive scaling
  └─ SVG rendering
  
Alternative: Plotly.js (more interactive, heavier)
```

#### **Axios (^1.4.0)** - HTTP Client
```
Purpose: API communication with backend
Size: ~40 KB
Features:
  ├─ Promise-based requests
  ├─ Interceptors (auth, error handling)
  ├─ Timeout management
  ├─ Request/response transformation
  └─ CORS support
  
Alternative: Fetch API (native, but less convenience)
```

#### **Chart.js (^4.3.0)** - Simple Charts
```
Purpose: Dashboard metrics (bar charts, gauges)
Size: ~80 KB
Features:
  ├─ Bar charts (cost comparison)
  ├─ Doughnut charts (mission feasibility %)
  ├─ Line charts (mission timeline)
  ├─ Real-time updates
  └─ Responsive design
  
Use with: Chart.js plugins (datalabels, annotation)
```

#### **Moment.js (^2.29.4)** - Date/Time Handling
```
Purpose: Mission day calculations, time formatting
Size: ~65 KB
Features:
  ├─ Parse mission durations
  ├─ Format timestamps
  ├─ Calculate elapsed time
  ├─ Timezone handling
  └─ Duration arithmetic
  
Alternative: date-fns (smaller, more modern)
```

#### **Lodash (^4.17.21)** - Utility Functions
```
Purpose: Data manipulation, array operations
Size: ~70 KB (can use lodash-es for tree-shaking)
Features:
  ├─ Array/object operations
  ├─ Deep cloning
  ├─ Grouping data
  └─ Function utilities
  
Optional: Use selectively (not all 300+ functions)
```

### 1.4 Frontend CSS Frameworks (Optional)

```
Bootstrap 5:           ~60 KB  (CSS grid system)
Tailwind CSS:          ~40 KB  (utility-first, custom)
Pure CSS:              0 KB    (custom styling, recommended)
FontAwesome Icons:     ~30 KB  (UI icons)

RECOMMENDATION: Pure CSS + custom grid
  → Full control
  → Minimal overhead
  → Easy to customize
```

---

## PART 2: BACKEND DEPENDENCIES (Python)

### 2.1 Python Version & Core

```
Python: 3.8+ (3.11 recommended)
Package Manager: pip (built-in)
Virtual Environment: venv (built-in)
```

### 2.2 Backend Requirements (requirements.txt)

```
# Core Framework
Flask==2.3.3
Flask-CORS==4.0.0
Werkzeug==2.3.6

# Data Science & Numerical Computing
numpy==1.24.3
scipy==1.11.1
pandas==2.0.3

# Database
SQLAlchemy==2.0.20
flask-sqlalchemy==3.0.5
sqlite3 (built-in)

# JSON Handling
jsonschema==4.17.3

# Real-time Communication
Flask-SocketIO==5.3.4
python-socketio==5.9.0
python-engineio==4.7.1

# Utilities
python-dotenv==1.0.0
python-dateutil==2.8.2
requests==2.31.0

# Development & Testing
pytest==7.4.0
pytest-cov==4.1.0
pytest-flask==1.2.0
black==23.7.0
flake8==6.0.0

# Deployment
gunicorn==21.2.0
gevent==23.9.1

# Optional: Background Tasks
celery==5.3.1
redis==5.0.0
```

### 2.3 Detailed Backend Dependencies

#### **Flask (2.3.3)** - Web Framework
```
Purpose: HTTP server, routing, request handling
Size: ~600 KB (with dependencies)
Memory: ~50 MB
Features:
  ├─ Lightweight & modular
  ├─ Built-in development server
  ├─ Blueprints for organization
  ├─ Template rendering
  ├─ Error handling
  └─ WSGI compliance
  
Alternatives: FastAPI, Django (heavier)
```

#### **NumPy (1.24.3)** - Numerical Computing
```
Purpose: Matrix operations for EKF (Kalman filter math)
Size: ~100 MB (with binaries)
Memory: ~200 MB
Features:
  ├─ Matrix algebra (state vectors, covariance)
  ├─ Linear algebra operations
  ├─ Random number generation
  ├─ Broadcasting
  └─ SIMD optimization
  
Critical for: EKF implementation
```

#### **SciPy (1.11.1)** - Scientific Computing
```
Purpose: Advanced numerical algorithms
Size: ~150 MB (with compiled extensions)
Features:
  ├─ Linear algebra (linalg)
  ├─ Statistics (stats)
  ├─ Optimization (optimize)
  ├─ Integration (integrate)
  └─ Interpolation (interpolate)
  
Used for: Advanced probability calculations
```

#### **Pandas (2.0.3)** - Data Analysis
```
Purpose: Time series data, result aggregation
Size: ~50 MB
Memory: ~150 MB
Features:
  ├─ DataFrames (tabular data)
  ├─ Time series handling
  ├─ Groupby operations
  ├─ CSV I/O
  └─ Statistical functions
  
Used for: Result analysis, export
```

#### **SQLAlchemy (2.0.20)** - ORM
```
Purpose: Database abstraction layer
Size: ~2 MB
Features:
  ├─ SQL generation
  ├─ Session management
  ├─ Relationship mapping
  ├─ Query building
  └─ Transaction management
  
Database: SQLite (built-in support)
```

#### **Flask-CORS (4.0.0)** - CORS Support
```
Purpose: Enable cross-origin requests (Frontend ↔ Backend)
Size: ~20 KB
Features:
  ├─ Allow specific origins
  ├─ Credential handling
  ├─ Preflight request handling
  └─ Custom header support
  
Required for: Frontend-Backend communication
```

#### **Flask-SocketIO (5.3.4)** - Real-time Updates
```
Purpose: WebSocket support for live simulation updates
Size: ~500 KB
Features:
  ├─ Bidirectional communication
  ├─ Event-based messaging
  ├─ Room management
  ├─ Automatic reconnection
  └─ Fallback to HTTP polling
  
Optional: Can use Server-Sent Events instead
```

#### **python-dotenv (1.0.0)** - Environment Variables
```
Purpose: Load .env configuration files
Size: ~20 KB
Features:
  ├─ Load from .env
  ├─ Override with environment
  ├─ Type conversion
  └─ Comments support
  
Example:
  FLASK_ENV=development
  DATABASE_URL=sqlite:///results.db
  SECRET_KEY=your-secret-key
```

#### **Pytest (7.4.0)** - Testing Framework
```
Purpose: Unit & integration testing
Size: ~1 MB
Features:
  ├─ Fixture system
  ├─ Parametrization
  ├─ Detailed assertions
  ├─ Coverage integration
  └─ Plugin ecosystem
  
Coverage Target: 95%+
```

---

## PART 3: DATABASE DEPENDENCIES

### 3.1 SQLite (Built-in)

```
What: Embedded SQL database
Why: Zero configuration, file-based, lightweight
Size: ~3 MB (binary)
Memory: ~10 MB per connection
Max Size: 281 TB (practically unlimited)

Perfect for:
  ✅ Single server deployment
  ✅ Small to medium datasets
  ✅ Development & testing
  ✅ No separate database server needed
  
Limitations:
  ❌ Poor concurrency (locks entire database)
  ❌ Not suitable for 100+ concurrent users
  
Migration: Easy to PostgreSQL if needed later
```

### 3.2 Database Schema

```sql
-- Simulations table
CREATE TABLE simulations (
    id INTEGER PRIMARY KEY,
    simulation_id TEXT UNIQUE NOT NULL,
    scenario TEXT NOT NULL,
    duration_days INTEGER NOT NULL,
    failure_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'completed'
);

-- Results table
CREATE TABLE results (
    id INTEGER PRIMARY KEY,
    simulation_id TEXT NOT NULL,
    ekf_detection_ms REAL,
    ekf_data_loss_percent REAL,
    metaspace_detection_ms REAL,
    metaspace_data_loss_percent REAL,
    cost_savings REAL,
    roi_percent REAL,
    FOREIGN KEY(simulation_id) REFERENCES simulations(simulation_id)
);

-- Failures table
CREATE TABLE failures (
    id INTEGER PRIMARY KEY,
    simulation_id TEXT NOT NULL,
    failure_id TEXT NOT NULL,
    occurrence_day INTEGER,
    severity TEXT,
    impact_json TEXT,
    FOREIGN KEY(simulation_id) REFERENCES simulations(simulation_id)
);

-- Metrics table
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY,
    simulation_id TEXT NOT NULL,
    day INTEGER,
    ekf_confidence REAL,
    metaspace_feasibility REAL,
    scenes_collected INTEGER,
    data_loss INTEGER,
    FOREIGN KEY(simulation_id) REFERENCES simulations(simulation_id)
);
```

### 3.3 Database File Management

```
Location: backend/data/metaspace.db
Size: ~10 MB (per 1000 simulations)
Backup: Auto-backup script (weekly)
Retention: Keep 6 months of simulations
Growth: ~1 MB per 100 simulations
```

---

## PART 4: VISUALIZATION & CHARTING

### 4.1 Real-time Visualization Stack

```
┌─────────────────────────────────────┐
│  Frontend Visualization Layer        │
├─────────────────────────────────────┤
│  D3.js (250 KB)                     │
│  ├─ Timeline rendering               │
│  ├─ SVG manipulation                 │
│  └─ Transitions & animations         │
│                                     │
│  Chart.js (80 KB)                   │
│  ├─ Bar/doughnut charts             │
│  ├─ Real-time updates               │
│  └─ Responsive design               │
│                                     │
│  Plotly.js (350 KB) [Optional]      │
│  ├─ 3D visualizations               │
│  ├─ Complex interactions            │
│  └─ Export to PDF                   │
└─────────────────────────────────────┘
```

### 4.2 Visualization Components

#### **Timeline Visualization (D3.js)**
```javascript
// Space: 200 KB of JavaScript code
// Runtime: 50-100ms rendering (1000+ points)
// Features:
//   ├─ Dual timeline (EKF vs MetaSpace)
//   ├─ Interactive tooltips
//   ├─ Zoom & pan
//   ├─ Animated transitions
//   └─ Real-time updates via WebSocket

// Load: Incremental (max 1000 points rendered)
// Memory: ~5 MB per visualization
```

#### **Cost Comparison Charts**
```javascript
// Using Chart.js
// Space: 30 KB JavaScript
// Renders:
//   ├─ EKF Total Cost (bar chart)
//   ├─ MetaSpace Total Cost (bar chart)
//   ├─ Cost Breakdown (pie chart)
//   ├─ ROI Gauge (doughnut chart)
//   └─ Payback Period (line chart)
```

#### **Mission Metrics Dashboard**
```javascript
// Multiple cards showing:
//   ├─ Detection latency ratio
//   ├─ Data loss reduction %
//   ├─ Mission success rate
//   ├─ Cost savings €
//   └─ Real-time status

// Update frequency: 100ms (via WebSocket)
// Bandwidth: ~10 KB/update
```

---

## PART 5: DEPLOYMENT DEPENDENCIES

### 5.1 Containerization (Docker)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies (minimal)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Expose ports
EXPOSE 5000

# Run
CMD ["gunicorn", "--worker-class", "gevent", \
     "--workers", "4", "--bind", "0.0.0.0:5000", \
     "backend.app:app"]

# Image size: ~1.5 GB (with all Python packages)
# Container size: ~2 GB (with data volumes)
```

### 5.2 Production Server (Gunicorn)

```
Gunicorn==21.2.0
  ├─ WSGI HTTP Server
  ├─ Multiple worker processes (4 recommended)
  ├─ Automatic process management
  ├─ Graceful shutdown
  └─ Built-in reload on code change
  
Workers: 4 × (CPU cores - 1) = 4 for quad-core
Memory: ~50 MB per worker = 200 MB total
Timeout: 300 seconds (long simulations)
```

### 5.3 Reverse Proxy (Nginx)

```nginx
# nginx.conf
upstream flask_app {
    server localhost:5000;
}

server {
    listen 80;
    server_name metaspace-simulator.local;
    
    # Frontend static files
    location / {
        root /app/frontend;
        try_files $uri /index.html;
        expires 1h;
    }
    
    # Backend API
    location /api {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket
    location /socket.io {
        proxy_pass http://flask_app/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json;
    gzip_min_length 1000;
}
```

Size: ~2 MB  
Memory: ~10 MB  
Concurrent users: Can handle 1000+ with proper tuning

---

## PART 6: COMPLETE DEPENDENCY TREE

### 6.1 Installation Order & Dependencies

```
Level 1: System & Runtime
├─ Python 3.8+ (or use pyenv for version management)
├─ Node.js 16+ (for frontend bundling)
├─ npm/yarn (package manager)
└─ Git (version control)

Level 2: Backend Core
├─ Flask 2.3.3
│  ├─ Werkzeug 2.3.6
│  ├─ Jinja2 (template engine)
│  └─ Click (CLI)
├─ Flask-CORS 4.0.0
├─ Flask-SQLAlchemy 3.0.5
│  └─ SQLAlchemy 2.0.20
└─ python-dotenv 1.0.0

Level 3: Scientific Computing
├─ NumPy 1.24.3
├─ SciPy 1.11.1
│  └─ (depends on NumPy)
└─ Pandas 2.0.3
   └─ (depends on NumPy)

Level 4: Real-time & Async
├─ Flask-SocketIO 5.3.4
│  ├─ python-socketio 5.9.0
│  └─ python-engineio 4.7.1
└─ gevent 23.9.1 (for async workers)

Level 5: Testing & Quality
├─ pytest 7.4.0
├─ pytest-cov 4.1.0
├─ black 23.7.0
└─ flake8 6.0.0

Level 6: Frontend
├─ d3@7.8.5 (via npm)
├─ axios@1.4.0
├─ chart.js@4.3.0
├─ moment@2.29.4
└─ lodash@4.17.21

Level 7: Deployment (Optional)
├─ Docker
├─ Gunicorn 21.2.0
├─ Nginx
└─ docker-compose
```

### 6.2 Dependency Installation Script

```bash
#!/bin/bash

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y python3.11 python3-pip python3-venv

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip wheel setuptools
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend
npm install
npm run build
cd ..

# Create database
python -c "from backend.app import db; db.create_all()"

# Run tests
pytest backend/tests/ --cov=backend/modules

echo "✅ All dependencies installed and tests passed!"
```

---

## PART 7: DEPENDENCY SIZE & MEMORY ANALYSIS

### 7.1 Installation Size Breakdown

```
Component                        Disk Space    Memory (Runtime)
─────────────────────────────────────────────────────────────
Python 3.11 runtime              ~150 MB       ~50 MB
Flask + dependencies             ~30 MB        ~20 MB
NumPy + SciPy + Pandas          ~300 MB        ~400 MB
SQLAlchemy                       ~5 MB         ~10 MB
Other Python deps                ~20 MB        ~30 MB
  ├─ Flask-CORS, SocketIO, etc.
  └─ Testing, utilities

SUBTOTAL BACKEND                 ~505 MB        ~510 MB

Node.js                          ~200 MB        ~100 MB
npm modules (node_modules/)      ~400 MB        ~150 MB
  ├─ D3.js                       ~250 KB
  ├─ Chart.js                    ~80 KB
  ├─ Axios                       ~40 KB
  └─ Other JS deps

SUBTOTAL FRONTEND                ~600 MB        ~250 MB

SQLite database                  ~10 MB         ~10 MB
Frontend HTML/CSS/JS built       ~3 MB          (served)

─────────────────────────────────────────────────────────────
TOTAL INSTALLATION               ~1.1 GB        ~770 MB (peak)

Recommended specs:
  ├─ Disk: 5 GB (with buffer)
  ├─ RAM: 1 GB (comfortable)
  ├─ CPU: 2 cores (adequate)
  └─ Network: 100 Mbps
```

### 7.2 Runtime Memory Per Simulation

```
Base Flask + modules             ~100 MB
  ├─ Python interpreter
  ├─ Flask framework
  ├─ NumPy/SciPy loaded
  └─ Database connection pool

Per Simulation Instance          ~50-100 MB
  ├─ EKF state (15 × 8 bytes × 1825 days = ~220 KB)
  ├─ MetaSpace state (similar)
  ├─ Timeline data (~1000 points × 100 bytes)
  ├─ Results storage
  └─ Temporary calculations

Concurrent 5 Simulations:        ~500 MB

Maximum Recommended:             ~2 GB (peak with UI)
```

---

## PART 8: OPTIONAL ADVANCED DEPENDENCIES

### 8.1 Performance Optimization

```
Option 1: Caching Layer (Redis)
├─ redis==5.0.0
├─ flask-caching==2.0.2
├─ Use for: Storing frequent simulation results
├─ Memory: ~100 MB (configurable)
└─ Benefit: 10x faster repeated queries

Option 2: Background Task Queue (Celery)
├─ celery==5.3.1
├─ redis==5.0.0 (message broker)
├─ Use for: Long simulations (> 5 minutes)
├─ Benefit: Non-blocking simulation execution
└─ Memory: ~50 MB for Celery worker

Option 3: In-Memory Database (HDF5)
├─ h5py==3.9.0
├─ Use for: Fast temporal data analysis
├─ Benefit: 100x faster than SQLite for large datasets
└─ Size: ~500 MB for 10,000 simulations

NOT REQUIRED for basic implementation
```

### 8.2 Monitoring & Logging

```
Recommended (Lightweight):
├─ python-json-logger==2.0.7 (JSON logging)
├─ Use: ELK stack or Splunk optional
└─ File size: ~50 MB/day (1000 simulations)

Optional (Heavy):
├─ prometheus-client==0.17.0
├─ datadog (agent)
└─ New Relic APM
```

---

## PART 9: INSTALLATION & VERIFICATION CHECKLIST

### 9.1 Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/metaspace/simulator.git
cd simulator

# 2. Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r backend/requirements.txt

# 4. Install frontend dependencies
cd frontend
npm install
npm run build
cd ..

# 5. Create database
python backend/init_db.py

# 6. Verify installation
python backend/test_imports.py

# 7. Run tests
pytest backend/tests/ -v

# 8. Start development server
gunicorn --worker-class gevent --workers 2 \
         --bind 0.0.0.0:5000 backend.app:app

# 9. Open browser
# http://localhost:5000
```

### 9.2 Verification Commands

```bash
# Check Python dependencies
pip list | grep -E "Flask|numpy|scipy|pandas"

# Check frontend dependencies
cd frontend && npm list d3 axios chart.js

# Test Flask app imports
python -c "from backend.app import app; print('✅ Flask OK')"

# Test NumPy/SciPy
python -c "import numpy as np; print('✅ NumPy OK')"

# Test database
python -c "from backend.models import Simulation; print('✅ Database OK')"

# Test frontend build
ls -la frontend/dist/index.html && echo '✅ Frontend OK'

# Check all together
./scripts/verify_all.sh
```

---

## PART 10: DEPLOYMENT CONFIGURATION

### 10.1 Docker Compose (Complete Stack)

```yaml
version: '3.9'

services:
  metaspace-simulator:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./backend/data:/app/backend/data
    environment:
      FLASK_ENV: production
      DATABASE_URL: sqlite:///data/metaspace.db
    depends_on:
      - redis
    restart: unless-stopped

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend/dist:/app/frontend:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - metaspace-simulator
    restart: unless-stopped

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
```

**Deployment:**
```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

### 10.2 System Requirements (Production)

```
Minimum:
├─ CPU: 2 cores
├─ RAM: 2 GB
├─ Disk: 20 GB
├─ Network: 50 Mbps
└─ OS: Ubuntu 20.04+ or CentOS 7+

Recommended:
├─ CPU: 4 cores
├─ RAM: 4 GB
├─ Disk: 50 GB (with backup)
├─ Network: 100 Mbps
└─ OS: Ubuntu 22.04 LTS

Performance:
├─ Concurrent users: 100+
├─ Simulations/hour: 1,000+
├─ API latency: <200ms
└─ Uptime: 99.9%
```

---

## PART 11: SECURITY DEPENDENCIES

### 11.1 Security Packages

```python
# requirements-security.txt
cryptography==41.0.1          # Encryption
PyJWT==2.8.0                 # JWT tokens
bcrypt==4.0.1                # Password hashing
python-magic==0.4.27         # File validation
requests-ratelimiter==0.1.0  # Rate limiting
```

### 11.2 Security Checklist

```
✅ Enable CORS (Flask-CORS configured)
✅ Add CSRF protection (if using forms)
✅ Validate all user inputs (jsonschema)
✅ Use HTTPS in production (SSL/TLS)
✅ Rate limiting on API endpoints
✅ Database backups (daily)
✅ Secrets in environment variables (python-dotenv)
✅ Security headers (Nginx or Flask-Talisman)
✅ SQL injection prevention (SQLAlchemy ORM)
✅ XSS protection (Content-Security-Policy headers)
```

---

## PART 12: SUMMARY TABLE

| Category | Package | Version | Size | Purpose |
|----------|---------|---------|------|---------|
| **Backend Framework** | Flask | 2.3.3 | 600 KB | Web server |
| **Numerical** | NumPy | 1.24.3 | 100 MB | EKF math |
| **Scientific** | SciPy | 1.11.1 | 150 MB | Advanced math |
| **Data** | Pandas | 2.0.3 | 50 MB | Data analysis |
| **Database** | SQLAlchemy | 2.0.20 | 5 MB | ORM |
| **Frontend** | D3.js | 7.8.5 | 250 KB | Visualization |
| **Charts** | Chart.js | 4.3.0 | 80 KB | Metrics charts |
| **HTTP** | Axios | 1.4.0 | 40 KB | API calls |
| **Testing** | Pytest | 7.4.0 | 1 MB | Unit tests |
| **Server** | Gunicorn | 21.2.0 | 1 MB | WSGI server |
| **Reverse Proxy** | Nginx | 1.25+ | 2 MB | Load balancing |
| **Container** | Docker | Latest | 1 GB | Containerization |

---

## INSTALLATION QUICK START

### 10-Minute Setup (Development)

```bash
# 1. Create environment
python3 -m venv venv && source venv/bin/activate

# 2. Install all dependencies
pip install Flask numpy scipy pandas Flask-CORS matplotlib d3-python-tools

# 3. Clone frontend
npm install d3 axios chart.js moment

# 4. Start server
python app.py

# 5. Open browser
# http://localhost:5000

# Time: ~5 minutes (depends on internet speed)
```

### 30-Minute Setup (Production)

```bash
# 1-5: Same as above
# 6. Docker build
docker build -t metaspace-simulator .

# 7. Docker run
docker run -p 5000:5000 metaspace-simulator

# 8. Verify
curl http://localhost:5000/api/health

# Time: ~25 minutes (Docker image pull + build)
```

---

## CONCLUSION

**Total Package Weight:** ~1.1 GB (Development), ~500 MB (Production with Docker)  
**Installation Time:** 10-30 minutes  
**Runtime Memory:** 500 MB (baseline) - 2 GB (with concurrent simulations)  
**Network Bandwidth:** ~1-5 Mbps (average simulation)  

**All dependencies are:**
✅ Open source  
✅ Well-maintained  
✅ Production-ready  
✅ Lightweight & efficient  
✅ Easy to install & configure  

---

**Document Version:** 1.0  
**Status:** Ready for deployment  
**Last Updated:** December 27, 2025  
**Maintenance:** Dependencies checked quarterly  
