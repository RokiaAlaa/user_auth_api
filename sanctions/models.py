from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.conf import settings

class SDNEntry(models.Model):
    uid = models.IntegerField()
    name = models.CharField(max_length=500)
    entity_type = models.CharField(max_length=100)
    program = models.CharField(max_length=200)
    source = models.CharField(max_length=50, default='OFAC')
    phonetic_key = models.CharField(max_length=50, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('source', 'uid')
        indexes = [
            GinIndex(fields=['name'], name='sdn_name_trgm_idx', opclasses=['gin_trgm_ops'])
        ]

class Alias(models.Model):
    entry = models.ForeignKey(SDNEntry, related_name='aliases', on_delete=models.CASCADE)
    alias_type = models.CharField(max_length=50)
    alias_name = models.CharField(max_length=500)
    phonetic_key = models.CharField(max_length=50, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('entry', 'alias_type', 'alias_name')
        indexes = [
            GinIndex(fields=['alias_name'], name='alias_name_trgm_idx', opclasses=['gin_trgm_ops'])
        ]

class SyncLog(models.Model):
    synced_at = models.DateTimeField(auto_now_add=True)
    parsed_entries = models.IntegerField()
    new_entries = models.IntegerField()
    removed_entries = models.IntegerField()
    new_aliases = models.IntegerField()

class SearchLog(models.Model):
    query = models.CharField(max_length=500)
    results_count = models.IntegerField()
    searched_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)