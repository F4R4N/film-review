from rest_framework.exceptions import ValidationError
DEFAULT_CONTACT_US_SETTINGS = {
	'APP_NAME': None,
	'SEND_MAIL': False,
	'MAIL_SUBJECT': " Contact Us ",
	'MESSAGE': "\nwe got your email. we will respond as soon as possible.\n\nBest Regards, "
}

try:
	from django.conf import settings
except ImportError:
	print("add CONTACT_US_SETTINGS to projects settings.py")
	exit()
fields = ["APP_NAME", "SEND_MAIL", "MAIL_SUBJECT", "MESSAGE"]

for field in fields:
	if field in settings.CONTACT_US_SETTINGS:
		DEFAULT_CONTACT_US_SETTINGS[field] = settings.CONTACT_US_SETTINGS[field]

try:
	from django.conf import settings
except ImportError:
	raise ValidationError(
		{"detail": "please add email backend in projects settings.py", "data":
			["EMAIL_USE_TLS", "EMAIL_HOST", "EMAIL_PORT", "EMAIL_HOST_USER",
				"EMAIL_HOST_PASSWORD"]})
