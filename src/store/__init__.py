"""Store resolution package for RevScan AI.
Provides scrapers and API clients for Google Play Store and Microsoft Store.
"""
from src.store.resolver import app_resolver, ResolvedApp

__all__ = ["app_resolver", "ResolvedApp"]
