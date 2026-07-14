from ninja import Router, Query
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Max, Q
from .models import SDNEntry, Alias
from .schemas import SearchResultSchema, MatchedAliasSchema
from typing import List
from django.core.cache import cache
import hashlib

router = Router()

MIN_SIMILARITY = 0.3

@router.get('/search', response=List[SearchResultSchema])
def search_sanctions(request, name: str, page: int = 1, page_size: int = 20):

    cache_key = f'search:{name.lower()}:{page}:{page_size}'

    cached_result = cache.get(cache_key)
    
    if cached_result:
        return cached_result

    entries = SDNEntry.objects.filter(name__trigram_similar=name).annotate(
        similarity=TrigramSimilarity('name', name)
    ).filter(similarity__gte=MIN_SIMILARITY)

    aliases = Alias.objects.select_related('entry').filter(alias_name__trigram_similar=name).annotate(
        similarity=TrigramSimilarity('alias_name', name)
    ).filter(similarity__gte=MIN_SIMILARITY) 

    results = {}

    for entry in entries:
        results[entry.uid] = {
            'entry': entry,
            'similarity': entry.similarity,
            'matched_aliases': []
        }

    for alias in aliases:
        entry_uid = alias.entry.uid

        if entry_uid not in results:
            results[entry_uid] = {
            'entry': alias.entry,
            'similarity': alias.similarity,
            'matched_aliases': []
        }
        
        elif alias.similarity > results[entry_uid]['similarity']:
            
            results[entry_uid]['similarity'] = alias.similarity

        results[entry_uid]['matched_aliases'].append(alias)

    sorted_results = sorted(results.values(), key=lambda r: r['similarity'], reverse=True)

    start = (page - 1) * page_size
    end = start + page_size

    paged_results = sorted_results[start:end]
    
    final_results = []
    for result in paged_results:

        uid = result['entry'].uid
        entry_name = result['entry'].name
        entity_type = result['entry'].entity_type
        program = result['entry'].program
        similarity = result['similarity']
        matched_aliases = []

        for alias in result['matched_aliases']:
            matched_aliases.append({'alias_type' : alias.alias_type , 'alias_name' : alias.alias_name})


        final_results.append({
            'uid' : uid,
            'name' : entry_name,
            'entity_type' : entity_type,
            'program' : program,
            'similarity' : similarity,
            'matched_aliases' : matched_aliases
        })

    cache.set(cache_key, final_results, timeout=300)

    return final_results