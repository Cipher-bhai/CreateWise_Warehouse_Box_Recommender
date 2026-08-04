# CrateWise — Smart Shipping Box Recommender

A Django warehouse management app that recommends the cheapest shipping box
that fits a given order, explains the pick in plain English via a free-tier
AI model, and gates every screen behind role-based access control
(Admin / Manager / Staff).

Built following the *Smart Shipping Box Recommender* build guide, using
only free and open-source tools.

## Features

- **Role-based auth** — Admin / Manager / Staff, with signup, login,
  logout, and full password-reset flow. New signups always start as Staff;
  only an Admin can promote someone.
- **Product & Box CRUD** — search, pagination, form validation.
- **Order creation** with automatic box recommendation:
  must-fit rule → cheapest box wins → tie broken by smallest wasted volume
  → `None` if nothing fits.
- **AI explanations** — a one-sentence, human-readable explanation of every
  recommendation via Google Gemini's free tier, with an automatic
  rule-based fallback if no API key is set or the request fails.
- **Dashboard** with Chart.js charts (orders by status, most-recommended
  boxes) fed by live queryset aggregation.
- **REST API** (Django REST Framework) for Products, Boxes, and Orders.
- **Modern, animated landing page** — scroll-reveal sections, animated
  hero, live stat counters — pure CSS/JS, no external animation library.
- **36+ automated tests** covering models, the recommendation algorithm,
  auth, and CRUD permissions per role.
- Docker support and a GitHub Actions workflow that runs the test suite
  on every push.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Django 5 |
| Database | SQLite (dev) → PostgreSQL (prod) |
| Frontend | Bootstrap 5 + Django Templates |
| Forms | django-crispy-forms + crispy-bootstrap5 |
| API | Django REST Framework |
| Charts | Chart.js |
| AI | Google Gemini free tier (with offline fallback) |
| Static files | WhiteNoise |
| Testing | Django TestCase + coverage.py |

## Project structure

```
warehouse_project/
├── warehouse/          # project settings, urls, wsgi/asgi
├── accounts/           # custom User model with roles, auth, user management
├── core/                # Product/Box/Order models, recommendation engine,
│                        # AI service, CRUD views, REST API
├── templates/           # landing, auth, dashboard, CRUD templates
├── static/               # CSS (animations) and JS (scroll-reveal, charts)
├── requirements.txt
├── Dockerfile / docker-compose.yml
├── .github/workflows/tests.yml
├── README.md / AI_USAGE.md / TEST_OUTPUT.md
└── .env.example
```

## Getting started

> **A note on how this project was produced:** this codebase was written
> directly (not run) in an offline sandbox with no package-index access, so
> `pip install`, migrations, the dev server, and the test suite could not
> actually be executed here. The steps below are what you need to run
> yourself as the first real check that everything works — please don't
> skip `python manage.py test` before treating this as done.

### 1. Clone and set up a virtual environment

```bash
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env — at minimum set a real SECRET_KEY.
# GEMINI_API_KEY is optional; without it the app uses a rule-based
# fallback explanation instead of a live AI call.
```

### 3. Run migrations and create a superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

Or seed demo data (an admin, a manager, a staff user, plus sample products
and boxes) in one step:

```bash
python manage.py seed_demo_data
# admin / ChangeMe123!
# manager1 / ChangeMe123!
# staff1 / ChangeMe123!
```

### 4. Run the dev server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the landing page, or
`http://127.0.0.1:8000/accounts/login/` to log in directly.

### 5. Run tests

```bash
coverage run manage.py test
coverage report -m
coverage html   # open htmlcov/index.html for a visual report
```

## Roles

| Role | Can do |
|---|---|
| **Admin** | Everything — full catalog CRUD, order management, user role management |
| **Manager** | Full CRUD on Products, Boxes, and Orders — no user management |
| **Staff** | View catalog, create and view orders — cannot edit/delete catalog items or orders |

## Deployment (Render, free tier)

1. Push this repo to GitHub.
2. Create a free account at render.com → New → Web Service → connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn warehouse.wsgi:application`
5. Set environment variables in the Render dashboard (`SECRET_KEY`,
   `DEBUG=False`, `ALLOWED_HOSTS`, `GEMINI_API_KEY` if using live AI) —
   never commit them.
6. Render auto-deploys on every push to `main`.

Railway.app and PythonAnywhere also have free tiers that work well for a
project this size.

## Docker (optional, one-command local setup)

```bash
cp .env.example .env
docker-compose up --build
```

## Screenshots

_Add screenshots of the landing page, dashboard, and order detail page
here once you've run the app locally._
