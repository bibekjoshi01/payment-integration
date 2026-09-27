PYTHON ?= python3
VENV = .venv/bin/python

.PHONY: setup backend frontend test frontend-check browser-install browser-test
setup:
	$(PYTHON) -m venv .venv
	$(VENV) -m pip install -r dj_server/requirements.txt
	$(VENV) dj_server/manage.py migrate --noinput
	cd frontend && npm ci

backend:
	$(VENV) dj_server/manage.py runserver 127.0.0.1:8000

frontend:
	cd frontend && npm run dev

test:
	$(VENV) dj_server/manage.py test checkout

frontend-check:
	cd frontend && npm run lint && npm run build

browser-install:
	cd frontend && npx playwright install chromium

browser-test:
	cd frontend && npm test
