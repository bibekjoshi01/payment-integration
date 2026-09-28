# Django backend

From the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r dj_server/requirements.txt
.venv/bin/python dj_server/manage.py migrate
.venv/bin/python dj_server/manage.py runserver 127.0.0.1:8000
```

Defaults work without `.env`: mock mode, SQLite, localhost only. The runtime database is `dj_server/payment-demo.sqlite3`; the older tracked `db.sqlite3` is left untouched. To reset local payments, stop Django, remove only `payment-demo.sqlite3`, then migrate again.

For sandbox calls, copy `.env.example` to `.env` in this directory, set `PAYMENT_MODE=sandbox`, add test credentials, and restart. Configure only the providers you want to try. Never place backend secrets in a `VITE_` variable.

```sh
.venv/bin/python dj_server/manage.py check
.venv/bin/python dj_server/manage.py test checkout
.venv/bin/python dj_server/manage.py makemigrations --check --dry-run
```

The checkout API uses explicit JSON parsing and guest permissions, independent of the retained auth/subscription examples. It does not collect card numbers or store full provider payloads. [API requests](../docs/api.md), [provider guides](../README.md#try-provider-sandboxes), and [test cases](checkout/tests/) explain the intended integration path.

Public HTTPS tunnels for sandbox webhooks need their hostname in `DJANGO_ALLOWED_HOSTS`. `FRONTEND_BASE_URL` must match the browser address and is used for provider return URLs. If you tunnel the frontend, ensure its `/api` proxy still reaches Django. Keep the backend and frontend URLs separate when registering webhooks.
