from django.contrib import admin

from .models import Plan, History, Arcade, Subject, Question, Option
# Register your models here.

admin.site.register(Plan)
admin.site.register(History)
admin.site.register(Arcade)
admin.site.register(Subject)
admin.site.register(Question)
admin.site.register(Option)