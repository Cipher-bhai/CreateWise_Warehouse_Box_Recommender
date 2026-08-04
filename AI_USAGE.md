# AI_USAGE.md

> **Before you submit this project:** the build guide explicitly asks you
> to write this file yourself — your own reflections on what AI did and
> what you personally reviewed. The table below is a factual record of
> what was generated in this specific session (useful as a starting
> point), but the "what I changed / verified" column and any narrative
> reflection should be rewritten in your own words once you've actually
> run the app, read the code, and run the tests yourself. Presenting an
> AI-generated reflection as your own defeats the point of the exercise.

## AI tools used in this build

| AI Tool | What it generated | What you changed / verified |
|---|---|---|
| Claude (claude.ai) | Full project scaffold: custom User model with roles, auth flows, Product/Box/Order models, `recommend_box()` algorithm, `explain_recommendation()` AI service with Gemini + fallback, CRUD views/forms/templates, DRF API, animated landing page, test suite, Docker/CI config | _Fill in after you've run `python manage.py migrate`, `python manage.py test`, and clicked through the app yourself_ |

## In-app AI feature (Step 8)

The app itself calls an AI model at runtime — this is separate from using
AI to help write the code. `core/ai_service.py` calls Google Gemini's
free tier (`gemini-1.5-flash`) to generate a one-sentence explanation of
why a given box was recommended for an order. If `GEMINI_API_KEY` isn't
set, or the request fails for any reason (offline, rate-limited, quota
exceeded), the app falls back to a deterministic, rule-based sentence
built from the same numbers — so the feature degrades gracefully rather
than breaking the order-creation flow.

## Verification status (honest, as of hand-off)

This project was written in a sandboxed environment with no access to
PyPI, so the following have **not** been executed by AI and need to be
your first checks:

- [ ] `pip install -r requirements.txt` succeeds
- [ ] `python manage.py migrate` applies cleanly
- [ ] `python manage.py test` passes (see `TEST_OUTPUT.md` for how to
      generate real output)
- [ ] `python manage.py runserver` and a manual click-through of
      signup → login → dashboard → create product/box → create order →
      see recommendation + AI explanation, for each of the three roles
- [ ] `coverage report -m` meets the >80% target

## Your own reflection (write this section)

_What surprised you about the AI-generated code? What did you have to
fix or rewrite? What would you do differently next time?_
