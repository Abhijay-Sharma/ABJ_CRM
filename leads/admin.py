from django.contrib import admin
from .models import Lead, User, Agent, UserProfile, Category

# Register your models here.

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Lead)
admin.site.register(Agent)
admin.site.register(Category)

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'emails', 'phone_number', 'created_time')
    list_filter = ('created_time',)
    ordering = ('-created_time',)

