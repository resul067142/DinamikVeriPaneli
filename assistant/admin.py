from django.contrib import admin
from .models import AssistantConversation, AssistantSettings

@admin.register(AssistantConversation)
class AssistantConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('question', 'answer', 'user__username')
    readonly_fields = ('created_at',)

@admin.register(AssistantSettings)
class AssistantSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')