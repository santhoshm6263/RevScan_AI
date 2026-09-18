"""Unit and integration tests for Google Play Store and Microsoft Store app resolvers."""
import pytest
from src.store.resolver import app_resolver, ResolvedApp
from src.store.play_store import play_store_resolver
from src.store.ms_store import ms_store_resolver


def test_play_store_package_extraction():
    """Verify package extraction from URLs and strings."""
    url1 = "https://play.google.com/store/apps/details?id=com.spotify.music&hl=en"
    assert play_store_resolver.extract_package_id(url1) == "com.spotify.music"

    url2 = "https://play.google.com/store/apps/details?id=com.whatsapp"
    assert play_store_resolver.extract_package_id(url2) == "com.whatsapp"

    direct = "com.duolingo"
    assert play_store_resolver.extract_package_id(direct) == "com.duolingo"


def test_ms_store_product_id_extraction():
    """Verify Microsoft Store product ID extraction from URLs and IDs."""
    url = "https://apps.microsoft.com/detail/9N0DX20HK701?hl=en-us&gl=US"
    assert ms_store_resolver.extract_product_id(url) == "9N0DX20HK701"

    direct = "9WZDNCRFJ3Q8"
    assert ms_store_resolver.extract_product_id(direct) == "9WZDNCRFJ3Q8"


def test_app_resolver_play_store():
    """Verify AppResolver resolves Google Play Store apps with authentic metadata."""
    app = app_resolver.resolve("com.spotify.music")
    assert isinstance(app, ResolvedApp)
    assert "Spotify" in app.name
    assert app.package == "com.spotify.music"
    assert app.platform == "android"
    assert app.category == "Music & Audio"
    assert app.developer == "Spotify AB"
    assert app.rating >= 4.0
    assert "play.google.com" in app.store_url


def test_app_resolver_ms_store():
    """Verify AppResolver resolves Microsoft Store apps with authentic metadata."""
    app = app_resolver.resolve("9N0DX20HK701", platform_hint="windows")
    assert isinstance(app, ResolvedApp)
    assert "Terminal" in app.name
    assert "Microsoft.WindowsTerminal" in app.package
    assert app.platform == "windows"
    assert app.category == "Developer Tools"
    assert app.developer == "Microsoft Corporation"
    assert app.rating >= 4.5


def test_app_resolver_custom_app():
    """Verify AppResolver gracefully handles arbitrary custom apps."""
    app = app_resolver.resolve("com.mycompany.inventoryapp")
    assert isinstance(app, ResolvedApp)
    assert app.package == "com.mycompany.inventoryapp"
    assert app.platform == "android"


def test_store_presets():
    """Verify curated authentic presets are populated."""
    presets = app_resolver.get_presets()
    assert "play_store" in presets
    assert "ms_store" in presets
    assert len(presets["play_store"]) >= 5
    assert len(presets["ms_store"]) >= 3
