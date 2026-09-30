# Django backend

Run these commands from the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r dj_server/requirements.txt
.venv/bin/python dj_server/manage.py migrate
.venv/bin/python dj_server/manage.py runserver 127.0.0.1:8000
```

The backend starts in mock mode without API keys. For provider sandboxes, copy `dj_server/.env.example` to `dj_server/.env`, set `PAYMENT_MODE=sandbox`, add test credentials, and restart.

## Test

```sh
.venv/bin/python dj_server/manage.py check
.venv/bin/python dj_server/manage.py test checkout
```

See [API examples](../docs/api.md), [testing and troubleshooting](../docs/testing.md), and [architecture](../docs/architecture.md).
