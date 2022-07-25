from rest_framework.permissions import IsAuthenticated


class isStudent(IsAuthenticated):
	def has_permission(self, request, view):
		return super().has_permission(request, view) and request.user.user_type == 'Student'

	def has_object_permission(self, request, view, obj):
		return super().has_object_permission(request, view, obj) and request.user.user_type == 'Student' and request.user.id == obj.user.id

class isStaff(IsAuthenticated):
	def has_permission(self, request, view):
		return super().has_permission(request, view) and request.user.user_type == 'Staff'

	def has_object_permission(self, request, view, obj):
		return super().has_object_permission(request, view, obj) and request.user.user_type == 'Staff' and request.user.id == obj.user.id

class isParent(IsAuthenticated):
	def has_permission(self, request, view):
		return super().has_permission(request, view) and request.user.user_type == 'Parent'

	def has_object_permission(self, request, view, obj):
		return super().has_object_permission(request, view, obj) and request.user.user_type == 'Parent' and request.user.id == obj.user.id

class isStudentsParent(IsAuthenticated):
	def has_object_permission(self, request, view, obj):
		return super().has_object_permission(request, view, obj) and request.user.user_type == 'Parent' and request.user.id == obj.prnt.user.id

class isAdmin(IsAuthenticated):
	def has_permission(self, request, view):
		return super().has_permission(request, view) and request.user.user_type == 'Admin'

	def has_object_permission(self, request, view, obj):
		return super().has_object_permission(request, view, obj) and request.user.user_type == 'Admin'

class isCreator(IsAuthenticated):
	def has_object_permission(self, request, view, obj):
		return super().has_object_permission(request, view, obj) and request.user.id == obj.user_id

class isOwner(IsAuthenticated):
	def has_object_permission(self, request, view, obj):
		return super().has_object_permission(request, view, obj) and request.user.id == obj.student_id