# PlanRail — Coding Guidelines

## 1. General Rule

Write simple, readable code.

Do not over-engineer.

---

# 2. Backend Structure

```text
backend/
│
├── main.py
├── config.py
│
├── api/
│   ├── routes/
│   └── dependencies.py
│
├── models/
├── schemas/
├── services/
│   ├── ai_service.py
│   ├── optimization_service.py
│   └── analytics_service.py
│
├── optimizer/
├── ai/
├── database/
└── utils/
```

---

# 3. Frontend Structure

```text
frontend/
│
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── hooks/
│   ├── utils/
│   └── types/
```

---

# 4. Naming

Python:

```text
snake_case
```

React:

```text
PascalCase components
camelCase functions
```

Database:

```text
snake_case
```

---

# 5. API Rule

Routes should not contain complex business logic.

Bad:

```text
route → 300 lines of optimization
```

Good:

```text
route
 ↓
service
 ↓
optimizer
```

---

# 6. AI Rule

Models should be separated from API code.

```text
ai/
  preprocessing.py
  priority_model.py
  risk_model.py
```

---

# 7. Optimization Rule

All OR-Tools logic should remain inside:

```text
optimizer/
```

---

# 8. Git

Use feature branches:

```text
main
dev
feature/frontend-dashboard
feature/ai-risk
feature/optimizer
feature/api
```

Never directly push experimental code to main.

---

# 9. Commit Messages

Use:

```text
feat: add maintenance API
feat: add block optimizer
fix: resolve train conflict bug
ui: improve dashboard
data: add synthetic maintenance dataset
docs: update architecture
```

---

# 10. Environment Variables

Never commit:

```text
password
API keys
database URLs
secret keys
```

Use:

```text
.env
.env.example
```

---

# 11. Code Rule for AI Coding Tools

Before modifying code, AI coding tools must:

1. Read all project documentation.
2. Understand existing architecture.
3. Reuse existing components.
4. Avoid introducing new technologies.
5. Avoid changing database schema without updating documentation.
6. Avoid changing API contracts without updating API specification.
7. Explain major architectural changes before implementing them.

---

# 12. Definition of Done

A feature is complete only when:

* Code works
* API works
* UI works
* Errors are handled
* Documentation is updated
* Git commit exists
