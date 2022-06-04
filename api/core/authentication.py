from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

class ExpiringTokenAuthentication(TokenAuthentication):
	validity_time = timezone.timedelta(hours=24)

	def authenticate_credentials(self, key):
		model = self.get_model()

		try:
			token = model.objects.get(key=key)
		except model.DoesNotExist:
			raise exceptions.AuthenticationFailed('Invalid token')

		if not token.user.is_active:
			raise exceptions.AuthenticationFailed('User inactive or deleted')

		utc_now = timezone.now()

		if token.created < utc_now - ExpiringTokenAuthentication.validity_time:
			raise exceptions.AuthenticationFailed('Token has expired')

		return (token.user, token)