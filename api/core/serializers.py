from rest_framework import serializers
from django.contrib.auth import get_user_model

# Custom User serializer
class UserCreationSerializer(serializers.ModelSerializer):
	class Meta:
		model = get_user_model()
		exclude = ('password',)

class UserUpdationSerializer(serializers.ModelSerializer):
	class Meta:
		model = get_user_model()
		fields = '__all__'
		extra_kwargs = {
			'password': {'write_only': True},
		}

	def update(self, instance, validated_data):
		if validated_data.get('password'):
			instance.set_password(validated_data['password'])
			validated_data.pop('password')

		return super().update(instance, validated_data)

class LoginSerializer(serializers.Serializer):
	id = serializers.CharField(max_length=10, required=False)
	email = serializers.EmailField(max_length=254, required=False)
	password = serializers.CharField(
		style={'input_type': 'password'},
		write_only=True,
		max_length=128,
	)
	
	def validate(self, data):
		id = data.get('id')
		email = data.get('email')

		if not id and not email:
			raise serializers.ValidationError('id or email is required')

		return data