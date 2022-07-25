from .models import Parent
from rest_framework import serializers

from django.contrib.auth import get_user_model
from core.serializers import UserUpdationSerializer

from django.db.models.signals import pre_save
from django.dispatch import receiver
import os

# Parent serializer
class ParentDefaultSerializer(serializers.ModelSerializer):
	id = serializers.CharField(source='user.id')
	email = serializers.EmailField(source='user.email')
	name = serializers.CharField(source='user.name')

	class Meta:
		model = Parent
		fields = ('id', 'image', 'email', 'name', 'student', 'phone')

	def create(self, validated_data):
		user = get_user_model().objects.create_user(
			id=validated_data['user']['id'],
			email=validated_data['user']['email'],
			name=validated_data['user']['name'],
			user_type='Parent'
		)

		return Parent.objects.create(
			user=user,
			image=validated_data.get('image'),
			student=validated_data.get('student'),
			phone=validated_data.get('phone'))

	def update(self, instance, validated_data):
		if validated_data.get('user'):
			user_data = validated_data.get('user')
			user_serializer = UserUpdationSerializer(data=user_data, instance=instance.user, partial=True)

			if user_serializer.is_valid():
				user_serializer.update(validated_data = validated_data['user'], instance=instance.user).save()

			else: raise serializers.ValidationError(user_serializer.errors)

			validated_data.pop('user')

		return super().update(instance, validated_data)


class ParentUpdationSerializer_Parent(ParentDefaultSerializer):
	password = serializers.CharField(
		source = 'user.password',
		style={'input_type': 'password'},
		write_only=True,
		max_length=128
	)
	password_confirm = serializers.CharField(
		style={'input_type': 'password'},
		write_only=True,
		max_length=128
	)
	old_password = serializers.CharField(
		style={'input_type': 'password'},
		write_only=True,
		max_length=128
	)

	class Meta:
		model = Parent
		fields = ('id', 'image', 'email', 'name', 'phone', 'old_password', 'password', 'password_confirm')
		restricted = ('id', 'student')
		extra_kwargs = {
			'student': {'read_only': True, 'required': False},
			'image': {'required': False}
		}

	def update(self, instance, validated_data):
		password = validated_data.get('user', {}).get('password')
		if password:
			if not validated_data.get('old_password'):
				raise serializers.ValidationError({'old_password': 'Old password is required'})

			if instance.user.check_password(validated_data.get('old_password')):
				if not validated_data.get('password_confirm'):
					raise serializers.ValidationError({'password_confirm': 'Password confirmation is required'})

				if password == validated_data.get('password_confirm'):
					return super().update(instance, validated_data)

				else: raise serializers.ValidationError({'__all__': 'Password and Confirm Password do not match.'})

			else: raise serializers.ValidationError({'old_password': 'Incorrect current password.'})

		else: return super().update(instance, validated_data)

class ParentUpdationSerializer_Admin(ParentDefaultSerializer):
	email = None
	phone = None

	class Meta:
		model = Parent
		fields = ('id', 'name', 'student')
		restricted = ('id', 'image', 'email', 'phone', 'password')


class ParentQuerySerializer(ParentDefaultSerializer):
	email = serializers.CharField(max_length=254)
	branch = serializers.CharField(max_length=200)

	class Meta:
		model = Parent
		exclude = ('image',)


# delete old image when adding new image
@receiver(pre_save, sender=Parent)
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