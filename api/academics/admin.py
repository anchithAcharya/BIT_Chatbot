from django.contrib import admin
from academics.models import Branch, Subject, Marks, Attendance

# Register your models here.
admin.site.register(Branch)
admin.site.register(Subject)
admin.site.register(Marks)
admin.site.register(Attendance)