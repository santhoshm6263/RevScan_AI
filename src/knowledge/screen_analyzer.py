"""Screen analysis, deduplication, and classification (Spec 6.1, Spec 12 - Member 3).
Calculates structural signatures, infers authentic screen names & purposes, and manages screen deduplication.
"""
import hashlib
import re
from typing import List, Tuple, Dict, Optional
from src.core.models import ScreenModel, ElementModel


class ScreenAnalyzer:
    """Analyzes and identifies unique screens."""

    def __init__(self):
        self.known_signatures: Dict[str, str] = {}  # signature -> screen_id
        self.known_screens: Dict[str, ScreenModel] = {}  # screen_id -> ScreenModel
        self.screen_counter: int = 0

    def reset(self):
        """Resets the analyzer state for a new scan."""
        self.known_signatures.clear()
        self.known_screens.clear()
        self.screen_counter = 0

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Strips volatile dynamic content (timestamps, numbers, battery) to stabilize signature."""
        t = text.strip().lower()
        t = re.sub(r"\b\d{1,2}:\d{2}(?::\d{2})?(?:\s*[ap]m)?\b", "", t)
        t = re.sub(r"\b\d+%\b", "", t)
        t = re.sub(r"\b\d+\b", "", t)
        return t.strip()

    def compute_signature(self, elements: List[ElementModel]) -> str:
        """Computes a normalized structural hash signature for screen deduplication."""
        tokens = []
        for elem in sorted(elements, key=lambda e: (e.bounds[1], e.bounds[0], e.id)):
            norm_text = self._normalize_text(elem.text)
            tokens.append(f"{elem.type}:{norm_text}:{elem.clickable}:{elem.input}")
        raw = "|".join(tokens)
        return hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]

    def infer_name_and_purpose(self, elements: List[ElementModel]) -> Tuple[str, str]:
        """Infers authentic screen name and purpose from constituent element types, texts, and IDs."""
        texts = [e.text.lower() for e in elements if e.text]
        ids = [e.id.lower() for e in elements if e.id]
        combined = " ".join(texts + ids)

        # 1. Dialog / Confirmation
        if any(w in combined for w in ["are you sure", "confirm action", "permission", "allow", "deny", "dismiss"]):
            return "Confirmation Dialog", "System confirmation or permission dialog"

        # 2. Terminal / Command Console (Windows Terminal / Dev Tools)
        if any(w in combined for w in ["terminal", "powershell", "command palette", "cmd.exe", "wsl", "console buffer", "split pane", "keybind", "cascadia"]):
            if "palette_title" in combined or "palette_search" in combined or "type a terminal action" in combined:
                return "Command Palette", "Interactive command palette and terminal action launcher"
            elif "scheme" in combined or "color" in combined or "font" in combined or "acrylic" in combined:
                return "Appearance & Color Schemes", "Terminal appearance, fonts, and color configuration"
            elif "keybind" in combined or "copy text" in combined or "paste text" in combined:
                return "Actions & Keybindings", "Keyboard shortcuts and action keybindings configuration"
            return "PowerShell Console Tab", "Active PowerShell command-line shell and buffer"

        # 3. Social Media & Creator Hub (Instagram, TikTok)
        if any(w in combined for w in ["instagram", "reels", "reel", "stories", "feed_title", "tab_explore", "input_caption"]):
            if "feed_title" in combined or "feed" in combined or "stories_bar" in combined:
                return "Social Home Feed", "Main photo and video social feed with story highlights"
            elif "caption" in combined or "studio" in combined or "create" in combined or "new post" in combined:
                return "Post & Reel Creator", "Media creator studio, filters, and caption composer"
            elif "explore" in combined or "reels" in combined or "trending" in combined:
                return "Explore & Trending Media", "Discovery grid, trending reels, and community media"
            elif "profile" in combined or "highlights" in combined:
                return "User Profile & Highlights", "User profile grid, saved collections, and highlights"
            return "Social Media Hub", "Social media feed and creator activity"

        # 4. Audio / Music Streaming (Spotify, Podcasts)
        if any(w in combined for w in ["spotify", "track", "playlist", "shuffle play", "daily mix", "discover weekly", "liked songs", "podcasts", "now playing", "album"]):
            if "greeting" in combined or "daily mix" in combined or "discover weekly" in combined:
                return "Music Home & Discovery", "Audio streaming recommendations and personalized mixes"
            elif "search" in combined or "genre" in combined or "browse" in combined:
                return "Music Search & Browse", "Search songs, browse genres, and discover audio"
            elif "track" in combined or "shuffle" in combined or "queue" in combined:
                return "Playlist & Track View", "Music playlist tracklist, audio streaming, and queue controls"
            elif "library" in combined or "artists" in combined:
                return "Music Library", "User saved playlists, favorite artists, and downloaded audio"
            return "Music Hub", "Audio streaming and music playback overview"

        # 5. Chat & Messaging (WhatsApp, Slack, Telegram)
        if any(w in combined for w in ["whatsapp", "slack", "chat", "voice note", "attach photo", "direct message", "channel", "typing...", "status", "update", "updates", "conversation", "calls"]):
            if "online" in combined or "voice call" in combined or "type a message" in combined or "attach" in combined:
                return "Direct Message Conversation", "Interactive direct message conversation and media sharing"
            elif "status" in combined or "update" in combined or "updates" in combined:
                return "Status & Broadcast Updates", "Live status updates and broadcast channels"
            elif "channel" in combined:
                return "Channel Discussion", "Group workspace and channel discussion feed"
            return "Chats Hub", "Recent message conversations and active chat list"

        # 6. Learning & Education (Duolingo)
        if any(w in combined for w in ["duolingo", "lesson", "streak", "translate", "practice mistake", "diamond league", "xp points", "start lesson"]):
            if "translate" in combined or "exercise" in combined or "check answer" in combined:
                return "Learning Exercise Quiz", "Interactive language lesson and translation quiz"
            elif "league" in combined or "leaderboard" in combined:
                return "League Leaderboard", "Competitive weekly XP leaderboard and reward chest"
            return "Learning Path", "Curriculum unit roadmap, streak status, and lesson tree"

        # 7. Main Landing Dashboard & Home Feed
        if any(w in combined for w in ["dashboard_title", "dashboard", "main dashboard", "home_greeting", "home landing", "overview"]):
            return "Main Dashboard", "Main application landing dashboard and activity overview"

        # 8. Authentication / Login
        if any(w in combined for w in ["login", "sign in", "sign_in", "password", "username", "authenticate"]):
            return "Login", "User authentication screen"

        # 9. Registration / Sign up
        if any(w in combined for w in ["sign up", "sign_up", "register", "create account", "new account"]):
            return "Registration", "New user registration screen"

        # 10. Cart / Checkout
        if any(w in combined for w in ["checkout", "cart", "basket", "place order", "payment", "order summary"]):
            return "Checkout", "Shopping cart and order checkout screen"

        # 11. Item Details / Product View
        if any(w in combined for w in ["item detail", "product detail", "item view", "specifications", "add to cart", "buy now"]):
            return "Item Details", "Detailed view of selected item or product"

        # 12. Search & Filter
        if any(w in combined for w in ["search", "filter", "query", "find", "sort"]):
            return "Search & Filter", "Search queries, category filters, and sorting view"

        # 13. Catalog / Discovery
        if any(w in combined for w in ["catalog", "categories", "category", "explore", "discover", "feed"]):
            return "Catalog & Discovery", "Browse catalog categories and discover content"

        # 14. Settings & Preferences
        if any(w in combined for w in ["settings", "preferences", "configuration", "privacy & security", "notifications"]):
            return "Settings & Privacy", "Application settings, notification toggles, and security"

        # 15. Profile / Account
        if any(w in combined for w in ["profile", "account", "my profile", "avatar", "user info", "logout", "sign out"]):
            return "User Profile", "User profile details, account management, and highlights"

        # 16. Dynamic Title Extraction from topmost text/header element
        for elem in elements:
            if elem.text and len(elem.text) >= 3 and not elem.clickable and elem.type in ("text", "view"):
                clean_title = elem.text.strip().split(" - ")[0].split(":")[0].strip()
                if 3 <= len(clean_title) <= 32:
                    return clean_title, f"{clean_title} screen and functional view"

        return f"Screen_{self.screen_counter:03d}", "Application functional view"

    def analyze_or_get_screen(
        self,
        elements: List[ElementModel],
        screenshot_path: str = ""
    ) -> Tuple[ScreenModel, bool]:
        """Returns (screen, is_new).
        If known, returns existing ScreenModel enriched with newly provided screenshot/actions.
        """
        signature = self.compute_signature(elements)
        if signature in self.known_signatures:
            existing_id = self.known_signatures[signature]
            existing_screen = self.known_screens.get(existing_id)
            if existing_screen:
                if not existing_screen.screenshot and screenshot_path:
                    existing_screen.screenshot = screenshot_path
                return existing_screen, False

            name, purpose = self.infer_name_and_purpose(elements)
            screen = ScreenModel(
                id=existing_id,
                name=name,
                purpose=purpose,
                screenshot=screenshot_path,
                elements=elements
            )
            self.known_screens[existing_id] = screen
            return screen, False

        self.screen_counter += 1
        screen_id = f"screen_{self.screen_counter:03d}"
        self.known_signatures[signature] = screen_id
        name, purpose = self.infer_name_and_purpose(elements)

        screen = ScreenModel(
            id=screen_id,
            name=name,
            purpose=purpose,
            screenshot=screenshot_path,
            elements=elements
        )
        self.known_screens[screen_id] = screen
        return screen, True


screen_analyzer = ScreenAnalyzer()
