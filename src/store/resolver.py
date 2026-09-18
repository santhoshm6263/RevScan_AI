"""Unified App Resolver for Google Play Store, Microsoft Store, and Custom Local Apps."""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from src.store.play_store import play_store_resolver, PLAY_STORE_PROFILES
from src.store.ms_store import ms_store_resolver, MS_STORE_PROFILES


class ResolvedApp(BaseModel):
    """Normalized app metadata resolved across any store or local environment."""
    name: str
    package: str
    platform: str = "android"  # "android", "windows", "custom"
    developer: Optional[str] = "Unknown"
    category: Optional[str] = "Application"
    rating: Optional[float] = 4.5
    icon_url: Optional[str] = ""
    store_url: Optional[str] = ""
    description: Optional[str] = ""
    version: Optional[str] = "1.0.0"
    protocol_or_intent: Optional[str] = ""
    screenshots: List[str] = Field(default_factory=list)


class AppResolver:
    """Detects platform and resolves authentic application metadata."""

    def resolve(self, input_query: str, platform_hint: Optional[str] = None) -> ResolvedApp:
        """Resolves an input query (store URL, package ID, Product ID, app name) to a ResolvedApp."""
        query = (input_query or "").strip()
        if not query:
            return ResolvedApp(
                name="Demo App",
                package="com.example.demo",
                platform="android",
                developer="RevScan AI Team",
                category="Demo",
                rating=5.0,
                description="Default RevScan AI demo test application."
            )

        # 1. Detect Microsoft Store / Windows app
        is_ms_store = (
            platform_hint == "windows"
            or "apps.microsoft.com" in query
            or "microsoft.com" in query
            or "ms-windows-store:" in query
            or query in MS_STORE_PROFILES
        )

        if is_ms_store:
            meta = ms_store_resolver.fetch_metadata(query)
            return ResolvedApp(
                name=meta.get("name", query),
                package=meta.get("package_family_name", query),
                platform="windows",
                developer=meta.get("developer", "Microsoft Store Publisher"),
                category=meta.get("category", "Windows Application"),
                rating=meta.get("rating", 4.5),
                icon_url=meta.get("icon_url", ""),
                store_url=meta.get("store_url", ""),
                description=meta.get("description", ""),
                version=meta.get("version", "Latest"),
                protocol_or_intent=meta.get("protocol", ""),
                screenshots=meta.get("screenshots", [])
            )

        # 2. Detect Google Play Store / Android package
        is_play_store = (
            platform_hint == "android"
            or "play.google.com" in query
            or query in PLAY_STORE_PROFILES
            or "." in query
        )

        if is_play_store:
            meta = play_store_resolver.fetch_metadata(query)
            return ResolvedApp(
                name=meta.get("name", query),
                package=meta.get("package", query),
                platform="android",
                developer=meta.get("developer", "Google Play Developer"),
                category=meta.get("category", "Application"),
                rating=meta.get("rating", 4.5),
                icon_url=meta.get("icon_url", ""),
                store_url=meta.get("store_url", ""),
                description=meta.get("description", ""),
                version=meta.get("version", "Latest"),
                protocol_or_intent=f"market://details?id={meta.get('package', query)}",
                screenshots=meta.get("screenshots", [])
            )

        # 3. Custom Local Application
        clean_name = query.replace(".", " ").replace("_", " ").title()
        return ResolvedApp(
            name=clean_name,
            package=query,
            platform="custom",
            developer="Local Developer",
            category="Custom Application",
            rating=5.0,
            icon_url="",
            store_url="",
            description=f"Custom local application '{query}'",
            version="1.0.0"
        )

    def get_presets(self) -> Dict[str, List[Dict[str, str]]]:
        """Returns curated authentic presets from Google Play Store & Microsoft Store."""
        return {
            "play_store": [
                {"name": "Spotify: Music & Podcasts", "package": "com.spotify.music", "category": "Music & Audio", "rating": "4.4"},
                {"name": "WhatsApp Messenger", "package": "com.whatsapp", "category": "Communication", "rating": "4.3"},
                {"name": "Instagram", "package": "com.instagram.android", "category": "Social", "rating": "4.1"},
                {"name": "Duolingo: Language Lessons", "package": "com.duolingo", "category": "Education", "rating": "4.7"},
                {"name": "Slack", "package": "com.Slack", "category": "Business", "rating": "4.4"},
                {"name": "Netflix", "package": "com.netflix.mediaclient", "category": "Entertainment", "rating": "4.2"},
            ],
            "ms_store": [
                {"name": "Windows Terminal", "package": "9N0DX20HK701", "category": "Developer Tools", "rating": "4.8"},
                {"name": "Spotify Music (Windows)", "package": "9WZDNCRFJ3Q8", "category": "Music", "rating": "4.5"},
                {"name": "WhatsApp Desktop", "package": "9NBLGGH4NNS1", "category": "Social", "rating": "4.2"},
                {"name": "Microsoft PowerToys", "package": "9MZCT29BR1RR", "category": "Utilities", "rating": "4.7"},
            ],
            "custom": [
                {"name": "RevScan AI Demo App", "package": "com.example.demo", "category": "Demo", "rating": "5.0"},
                {"name": "Android Settings", "package": "com.android.settings", "category": "System", "rating": "5.0"},
                {"name": "Android Calculator", "package": "com.google.android.calculator", "category": "Tools", "rating": "4.6"},
            ]
        }


app_resolver = AppResolver()
