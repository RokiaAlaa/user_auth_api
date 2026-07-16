from ninja import Router
from django.contrib.postgres.search import TrigramSimilarity
from .models import SDNEntry, Alias, SearchLog
from .schemas import SearchResultSchema
from typing import List
from django.core.cache import cache
from users.auth import jwt_auth
import jellyfish
from django.db.models import Q

router = Router()

MIN_SIMILARITY = 0.3

@router.get('/search', response=List[SearchResultSchema], auth=jwt_auth)
def search_sanctions(request, name: str, page: int = 1, page_size: int = 20):

    cache_key = f'search:{name.lower()}:{page}:{page_size}'

    cached_result = cache.get(cache_key)
    
    if cached_result:
        SearchLog.objects.create(query=name, results_count=len(cached_result), user=request.auth)
        return cached_result
    
    phonetic_key = jellyfish.metaphone(name)

    entries = SDNEntry.objects.filter(
        Q(name__trigram_similar=name) | Q(phonetic_key=phonetic_key)
        ).annotate(
            similarity=TrigramSimilarity('name', name)
        ).filter(
            Q(similarity__gte=MIN_SIMILARITY) | Q(phonetic_key=phonetic_key)
        )

    aliases = Alias.objects.select_related('entry').filter(
        Q(alias_name__trigram_similar=name) | Q(phonetic_key=phonetic_key)
    ).annotate(
        similarity=TrigramSimilarity('alias_name', name)
    ).filter(
        Q(similarity__gte=MIN_SIMILARITY) | Q(phonetic_key=phonetic_key)
    ) 

    results = {}

    for entry in entries:
        results[entry.uid] = {
            'entry': entry,
            'similarity': entry.similarity,
            'matched_field': 'name',
            'source': entry.source,
            'matched_aliases': []
        }

    for alias in aliases:
        entry_uid = alias.entry.uid

        if entry_uid not in results:
            results[entry_uid] = {
            'entry': alias.entry,
            'similarity': alias.similarity,
            'source': alias.entry.source,
            'matched_field': f'alias: {alias.alias_name}',
            'matched_aliases': []
        }
        
        elif alias.similarity > results[entry_uid]['similarity']:
            
            results[entry_uid]['similarity'] = alias.similarity
            results[entry_uid]['matched_field'] = f'alias: {alias.alias_name}'

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
        matched_field = result['matched_field']
        matched_aliases = []

        for alias in result['matched_aliases']:
            matched_aliases.append({'alias_type' : alias.alias_type , 'alias_name' : alias.alias_name})


        final_results.append({
            'uid' : uid,
            'name' : entry_name,
            'source': result['source'],
            'entity_type' : entity_type,
            'program' : program,
            'similarity' : similarity,
            'matched_field': matched_field,
            'matched_aliases' : matched_aliases
        })

    cache.set(cache_key, final_results, timeout=300)

    SearchLog.objects.create(query=name, results_count=len(final_results), user=request.auth)
    return final_results