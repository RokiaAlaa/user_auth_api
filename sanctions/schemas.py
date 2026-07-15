from ninja import Schema
from typing import List, Optional

class MatchedAliasSchema(Schema):
    alias_type: str
    alias_name: str

class SearchResultSchema(Schema):
    uid: int
    name: str
    entity_type: str
    program: str
    similarity: float
    matched_field: str
    matched_aliases: List[MatchedAliasSchema] = []