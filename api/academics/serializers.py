from rest_framework import serializers
from academics.models import Marks, Attendance, Subject
from student.models import Student

# Custom User serializer
class MarksSerializer(serializers.ModelSerializer):
	student = serializers.CharField(source='student.user.id')
	subject = serializers.CharField(source='subject.code')

	class Meta:
		model = Marks
		exclude = ('id',)
		extra_kwargs = {
			'test1Marks': {'required': False},
			'test2Marks': {'required': False},
			'test3Marks': {'required': False},
			'assignment1Marks': {'required': False},
			'assignment2Marks': {'required': False},
			'externalMarks': {'required': False},
		}

	def create(self, validated_data):
		try:
			student = Student.objects.get(user_id=validated_data.get('student', {}).get('user', {}).get('id'))
		except Student.DoesNotExist:
			raise serializers.ValidationError('Student with given id does not exist')

		try:
			subject = Subject.objects.get(code=validated_data.get('subject', {}).get('code'))
		except Subject.DoesNotExist:
			raise serializers.ValidationError('Subject with given code does not exist')

		validated_data['student'] = student
		validated_data['subject'] = subject

		return super().create(validated_data)

	def update(self, instance, validated_data):
		try:
			student = Student.objects.get(user_id=validated_data.get('student', {}).get('user', {}).get('id'))
		except Student.DoesNotExist:
			raise serializers.ValidationError('Student with given id does not exist')

		try:
			subject = Subject.objects.get(code=validated_data.get('subject', {}).get('code'))
		except Subject.DoesNotExist:
			raise serializers.ValidationError('Subject with given code does not exist')

		validated_data['student'] = student
		validated_data['subject'] = subject

		return super().update(instance, validated_data)


class AttendanceSerializer(serializers.ModelSerializer):
	student = serializers.CharField(source='student.user.id')
	subject = serializers.CharField(source='subject.code')

	class Meta:
		model = Attendance
		exclude = ('id',)
		extra_kwargs = {
			'student': {'read_only': True},
			'subject': {'read_only': True},
			'test1Attendance': {'required': False},
			'test2Attendance': {'required': False},
			'test3Attendance': {'required': False}
		}

	def create(self, validated_data):
		try:
			student = Student.objects.get(user_id=validated_data.get('student', {}).get('user', {}).get('id'))
		except Student.DoesNotExist:
			raise serializers.ValidationError('Student with given id does not exist')

		try:
			subject = Subject.objects.get(code=validated_data.get('subject', {}).get('code'))
		except Subject.DoesNotExist:
			raise serializers.ValidationError('Subject with given code does not exist')

		validated_data['student'] = student
		validated_data['subject'] = subject

		return super().create(validated_data)

	def update(self, instance, validated_data):
		try:
			student = Student.objects.get(user_id=validated_data.get('student', {}).get('user', {}).get('id'))
		except Student.DoesNotExist:
			raise serializers.ValidationError('Student with given id does not exist')

		try:
			subject = Subject.objects.get(code=validated_data.get('subject', {}).get('code'))
		except Subject.DoesNotExist:
			raise serializers.ValidationError('Subject with given code does not exist')

		validated_data['student'] = student
		validated_data['subject'] = subject

		return super().update(instance, validated_data)
