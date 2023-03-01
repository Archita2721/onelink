from django.db import models
import datetime
# Create your models here.

class linkModel(models.Model):
    ios_link = models.URLField()
    android_link = models.URLField()
    fallback_link = models.URLField()
    qr_code = models.URLField(blank=True, null=True)
    appname = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.CharField(max_length=15,blank=True)