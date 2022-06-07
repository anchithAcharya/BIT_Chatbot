from rest_framework.permissions import IsAuthenticated


class isAdmin(IsAuthenticated):
	def has_permission(self, request, view):
		return super().has_permission(request, view) and request.user.is_superuser

	def has_object_permission(self, request, view, obj):
		return super().has_object_permission(request, view, obj) and request.user.is_superuser

class isOwner(IsAuthenticated):
	def has_object_permission(self, request, view, obj):
		return super().has_object_permission(request, view, obj) and request.user.id == obj.user_id