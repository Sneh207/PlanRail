# PlanRail — Technology Stack

## Frontend

### React + Vite

Use for the web application.

### Tailwind CSS

Use for styling.

### Recharts

Use for:

* KPI charts
* Risk charts
* Before/after comparison
* Department analytics

### Leaflet

Use for railway network visualization.

---

# Backend

### Python

Primary backend/AI language.

### FastAPI

REST API framework.

### Pydantic

Request/response validation.

### SQLAlchemy

Database ORM.

---

# Database

### PostgreSQL

Primary database.

### PostGIS

Geospatial extension.

Use it for:

* railway sections
* stations
* asset coordinates
* spatial queries

---

# AI/ML

Start simple.

### Priority Model

Initially use weighted scoring.

Then optionally use:

* XGBoost
* Random Forest

### Risk Model

Use XGBoost/Random Forest initially.

### Traffic Model

Use statistical/ML prediction depending on available data.

Do not introduce deep learning unless it provides measurable benefit.

---

# Optimization

### Google OR-Tools

Use CP-SAT for block scheduling.

Do NOT use an LLM for optimization.

---

# Data Processing

* Pandas
* NumPy
* Scikit-learn
* XGBoost

---

# Development

* Git
* GitHub
* VS Code/Cursor
* Python virtual environment
* npm

---

# Technology Rules

Do not introduce:

* Next.js
* Django
* Node.js backend
* MongoDB
* Firebase
* Kubernetes
* Docker microservices

unless the entire team explicitly agrees and the change is documented.

The default architecture must remain:

React + FastAPI + PostgreSQL + Python.
