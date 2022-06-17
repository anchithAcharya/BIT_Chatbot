from .models import Student
from rest_framework import serializers

from django.contrib.auth import get_user_model
from core.serializers import UserUpdationSerializer

from django.db.models.signals import pre_save
from django.dispatch import receiver
import os

# Student serializer
class StudentDefaultSerializer(serializers.ModelSerializer):
	id = serializers.CharField(source='user.id')
	email = serializers.EmailField(source='user.email')
	name = serializers.CharField(source='user.name')
	current_sem = serializers.IntegerField(required=False)

	class Meta:
		model = Student
		fields = ('id', 'image', 'email', 'name', 'current_sem', 'branch', 'phone')

	def create(self, validated_data):
		user = get_user_model().objects.create_user(
			id=validated_data['user']['id'],
			email=validated_data['user']['email'],
			name=validated_data['user']['name']
		)

		return Student.objects.create(
			user=user,
			image=validated_data['image'],
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


class StudentUpdationSerializer_Student(StudentDefaultSerializer):
	password = serializers.CharField(
		source = 'user.password',
		style={'input_type': 'password'},
		write_only=True,
		max_length=128
	)

	class Meta:
		model = Student
		fields = ('id', 'image', 'email', 'name', 'phone', 'password')
		restricted = ('id', 'branch', 'current_sem')
		extra_kwargs = {
			'branch': {'read_only': True, 'required': False},
			'current_sem': {'read_only': True, 'required': False}
		}

	def update(self, instance, validated_data):
		return super().update(instance, validated_data)

class StudentUpdationSerializer_Admin(StudentDefaultSerializer):
	email = None
	phone = None

	class Meta:
		model = Student
		fields = ('id', 'image', 'name', 'current_sem', 'branch')
		restricted = ('id', 'email', 'phone', 'password')


# delete old image when adding new image
@receiver(pre_save, sender=Student)
def delete_old_image(sender, instance, **kwargs):
    # on creation, signal callback won't be triggered 
    if instance._state.adding and not instance.pk:
        return False
    
    try:
        old_image = sender.objects.get(pk=instance.pk).image
    except sender.DoesNotExist:
        return False
    
    # comparing the new image with the old one
    image = instance.image
    if old_image and old_image != image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)