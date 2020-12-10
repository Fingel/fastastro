serve:
	uvicorn app.main:app --reload

test:
	PYTHONPATH=. EMAIL_BACKEND=TestEmailBackend pytest

smtpd:
	aiosmtpd -n

serve_smtp:
	EMAIL_BACKEND=SMTPEmailBackend uvicorn app.main:app --reload
