from django.contrib import admin
from core.models import User, PasswordResetRequest

from django.contrib.auth.models import Group


admin.site.register(User)
admin.site.register(PasswordResetRequest)

admin.site.unregister(Group)