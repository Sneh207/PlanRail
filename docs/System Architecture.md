# PlanRail — System Architecture

## 1. Architecture Principle

Use a simple modular architecture.

Do not create unnecessary microservices.

Architecture:

React → FastAPI → Services → PostgreSQL/PostGIS

AI and optimization run as Python services inside the backend initially.

---

# 2. High-Level Architecture

```text
                    PLANRAIL
                       |
                 React Frontend
                       |
                    REST API
                       |
                  FastAPI Backend
                       |
        ┌──────────────┼──────────────┐
        |              |              |
     Database        AI Engine    Optimization
        |              |              |
   PostgreSQL       ML Models      OR-Tools
   + PostGIS
        |
   Railway Data
   Train Data
   Maintenance Data
```

---

# 3. Frontend

Technology:

* React
* Vite
* Tailwind CSS
* Recharts
* Leaflet

Responsibilities:

* UI
* Dashboard
* Tables
* Maps
* Charts
* Plan visualization
* What-if controls

The frontend must not contain business logic for AI or optimization.

---

# 4. Backend

Technology:

* Python
* FastAPI
* Pydantic
* SQLAlchemy

Responsibilities:

* API
* Validation
* Authentication
* Database communication
* AI inference
* Optimization
* Analytics

---

# 5. AI Layer

Components:

```text
Data preprocessing
        ↓
Feature engineering
        ↓
Priority model
        ↓
Risk model
        ↓
Traffic impact model
```

---

# 6. Optimization Layer

Use Google OR-Tools.

Inputs:

* Maintenance tasks
* Priority
* Risk
* Available windows
* Train schedules
* Section
* Duration
* Department
* Compatibility
* Crew availability

Output:

* Recommended blocks
* Tasks per block
* Block duration
* Conflicts
* Optimization metrics

---

# 7. Database

Use PostgreSQL.

Use PostGIS for:

* Section geometry
* Station locations
* Asset locations
* Spatial relationships

---

# 8. Data Flow

```text
Dataset
   ↓
Database
   ↓
FastAPI
   ↓
Feature Engineering
   ↓
AI Prediction
   ↓
Optimization
   ↓
Plan Validation
   ↓
API Response
   ↓
React Dashboard
```

---

# 9. Human-in-the-Loop

```text
AI Recommendation
        ↓
Controller Review
        ↓
Approve / Modify / Reject
        ↓
Final Plan
```

AI must never automatically claim that a railway block is operationally approved.

---

# 10. Deployment

Prototype:

* Local development

MVP:

* Frontend: Vercel
* Backend: Render/Railway
* Database: PostgreSQL/Supabase/Neon

Deployment provider can be changed without changing application architecture.
