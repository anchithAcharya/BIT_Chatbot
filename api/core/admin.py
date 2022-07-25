from django.contrib import admin
from core.models import User, PasswordResetRequest, ChatbotProblemQuery

from django.contrib.auth.models import Group


admin.site.register(User)
admin.site.register(PasswordResetRequest)
admin.site.register(ChatbotProblemQuery)

admin.site.unregister(Group)