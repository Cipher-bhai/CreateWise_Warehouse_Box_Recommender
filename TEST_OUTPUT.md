# TEST_OUTPUT.md

> **This file has not been generated yet.** Because this project was
> built in a sandbox without access to PyPI, the test suite could not
> actually be installed or run here — so pasting fabricated "passing"
> output below would be dishonest. Run the commands yourself and replace
> this file's contents with the real output, exactly as the build guide
> asks ("paste the raw output ... so the interviewer can see real,
> passing results").

## How to generate this file for real

```bash
python manage.py test > TEST_OUTPUT.md
echo "" >> TEST_OUTPUT.md
coverage run manage.py test
coverage report -m >> TEST_OUTPUT.md
```

## What the suite covers

`accounts/tests.py` and `core/tests.py` together contain 30+ tests:

- **Model tests** — `Product`, `Box`, `Order` field behavior, `volume()`,
  `__str__()`.
- **`recommend_box()` tests** — lowest-cost-wins, weight-limit exclusion,
  tie-break by smallest wasted volume, returns `None` when nothing fits
  or the box queryset is empty.
- **`combined_requirements()` tests** — multi-product bounding box math,
  empty-product-list handling.
- **AI service tests** — the fallback explanation always returns usable
  text, with or without a box match, and never raises.
- **Auth tests** — login/logout, anonymous users redirected (not 403'd)
  from protected views.
- **CRUD permission tests per role** — Staff can view but not
  create/edit/delete catalog items or orders (403); Manager and Admin
  can; Admin can manage users, Manager/Staff get 403 on user management.
- **End-to-end order flow** — creating an order through the view runs
  `recommend_box()` and `explain_recommendation()` and persists both the
  box and explanation on the `Order`.
- **Dashboard test** — renders with chart context data present.
- **API tests** — DRF endpoints require authentication and creating an
  order via the API triggers the same recommendation logic as the UI.

If you add new views or business logic, add tests alongside them before
you consider a feature "done" — that's the standard this suite is meant
to model.
