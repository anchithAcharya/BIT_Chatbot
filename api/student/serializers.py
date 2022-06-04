from .models import Student
from rest_framework import serializers

from django.contrib.auth import get_user_model
from core.serializers import UserUpdationSerializer

# Student serializer
class StudentCreationSerializer(serializers.ModelSerializer):
	id = serializers.CharField(source='user.id')
	email = serializers.EmailField(source='user.email')
	name = serializers.CharField(source='user.name')
	current_sem = serializers.IntegerField(required=False)

	class Meta:
		model = Student
		fields = ('id', 'email', 'name', 'current_sem', 'branch', 'phone')

	def create(self, validated_data):
		user = get_user_model().objects.create_user(
			id=validated_data['user']['id'],
			email=validated_data['user']['email'],
			name=validated_data['user']['name']
		)

		return Student.objects.create(
			user=user,
			current_sem=validated_data['current_sem'],
			branch=validated_data['branch'])

	def update(self, instance, validated_data):
		if validated_data.get('user'):
			user_data = validated_data.get('user')
			user_serializer = UserUpdationSerializer(data=user_data, instance=instance.user, partial=True)

			if user_serializer.is_valid():
				user_serializer.update(validated_data = validated_data['user'], instance=instance.user).save()

			else: raise serializers.ValidationError(user_serializer.errors)

			validated_data.pop('user')

		return super().update(instance, validated_data)

class StudentUpdationSerializer_Student(StudentCreationSerializer):
	password = serializers.CharField(
		source = 'user.password',
		style={'input_type': 'password'},
		write_only=True,
		trim_whitespace=False,
		max_length=128,
	)

	class Meta:
		model = Student
		fields = ('id', 'email', 'name', 'phone', 'password')
		extra_kwargs = {
			'branch': {'read_only': True, 'required': False},
			'current_sem': {'read_only': True, 'required': False}
		}

	def update(self, instance, validated_data):
		return super().update(instance, validated_data)

class StudentUpdationSerializer_Admin(StudentCreationSerializer):
	email = None
	phone = None

	class Meta:
		model = Student
		fields = ('id', 'name', 'current_sem', 'branch')