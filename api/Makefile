serve:
	uvicorn app.main:app --reload

test:
	PYTHONPATH=. EMAIL_BACKEND=TestEmailBackend pytest -s

smtpd:
	aiosmtpd -n
