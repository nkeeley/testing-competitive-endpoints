"""Exa runner — wraps exa-py SDK."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import EXA_API_KEY


def _client():
    from exa_py import Exa
    return Exa(api_key=EXA_API_KEY)


def search(query, num_results=5):
    return _client().search(query, num_results=num_results)


def search_and_contents(query, num_results=5):
    return _client().search_and_contents(query, num_results=num_results, text=True)
