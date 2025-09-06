from django.db import models
from django.contrib.auth.models import User

class AssistantConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username}: {self.question[:50]}..."

class AssistantSettings(models.Model):
    name = models.CharField(max_length=100, default="AI Asistan")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Asistan Ayarı"
        verbose_name_plural = "Asistan Ayarları"