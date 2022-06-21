from rest_framework import serializers
from django.contrib.auth import get_user_model

# Custom User serializer
class UserCreationSerializer(serializers.ModelSerializer):
	class Meta:
		model = get_user_model()
		exclude = ('password', 'user_type')

class UserUpdationSerializer(serializers.ModelSerializer):
	class Meta:
		model = get_user_model()
		exclude = ('user_type',)
		extra_kwargs = {
			'password': {'write_only': True},
		}

	def update(self, instance, validated_data):
		if validated_data.get('password'):
			instance.set_password(validated_data['password'])
			validated_data.pop('password')

		return super().update(instance, validated_data)