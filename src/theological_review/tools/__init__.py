"""Theological source tools for the review agent."""

from theological_review.tools.magisterium import query_magisterium
from theological_review.tools.vatican import search_vatican_documents, search_catechism
from theological_review.tools.newadvent import search_church_fathers, search_encyclopedia
from theological_review.tools.citation import verify_citation, fetch_source_content

__all__ = [
    "query_magisterium",
    "search_vatican_documents",
    "search_catechism",
    "search_church_fathers",
    "search_encyclopedia",
    "verify_citation",
    "fetch_source_content",
]
