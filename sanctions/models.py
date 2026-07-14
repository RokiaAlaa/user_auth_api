from django.db import models

class SDNEntry(models.Model):
    uid = models.IntegerField(unique=True)
    name = models.CharField(max_length=500)
    entity_type = models.CharField(max_length=100)
    program = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Alias(models.Model):
    entry = models.ForeignKey(SDNEntry, related_name='aliases', on_delete=models.CASCADE)
    alias_type = models.CharField(max_length=50)
    alias_name = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('entry', 'alias_type', 'alias_name')