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

        # Authentication / Login
        if any(w in combined for w in ["login", "sign in", "sign_in", "log in", "password", "username", "authenticate"]):
            return "Login", "User authentication screen"

        # Registration / Sign up
        if any(w in combined for w in ["sign up", "sign_up", "register", "create account", "new account"]):
            return "Registration", "New user registration screen"

        # Checkout / Cart
        if any(w in combined for w in ["btn_checkout", "checkout & pay", "place order", "cart_checkout"]):
            return "Checkout", "Shopping cart and order checkout screen"

        # 2. Racing / Driving Games (e.g. Hill Climb Racing)
        if any(w in combined for w in ["hill climb", "stage_canyon", "stage_desert", "btn_start_race", "garage_header", "btn_upgrade_engine", "btn_gas_pedal", "btn_brake_pedal", "gauge_fuel", "gauge_speedometer", "results_header", "out of fuel"]):
            if any(w in combined for w in ["results_header", "stage rewards", "out of fuel", "distance traveled", "total reward", "btn_double_coins", "retry stage"]):
                return "Stage Rewards & Results", "Race summary, distance traveled, and earned coin rewards"
            elif any(w in combined for w in ["hud_header", "gas pedal", "brake pedal", "gauge_speedometer", "gauge_fuel", "air time stunt"]):
                return "Race Track & Driving HUD", "Active in-game racing track HUD with gas, brake, and fuel meters"
            elif any(w in combined for w in ["menu_title", "stage_canyon", "stage selection", "btn_start_race", "daily bonus chest"]):
                return "Stage Selection & Menu", "Main menu with campaign track and stage selection"
            elif any(w in combined for w in ["garage_header", "upgrade engine", "upgrade suspension", "upgrade tires", "upgrade 4wd"]):
                return "Vehicle Garage & Upgrades", "Vehicle selection and engine/suspension/tires parts upgrade tuning"
            return "Racing Game Screen", "Interactive racing game view"

        # 3. Action / Casual / RPG Games
        if any(w in combined for w in ["game lobby", "start_level", "inventory_header", "flaming sword", "combat hud", "arena_header", "victory_header", "stars earned", "loot chest"]):
            if any(w in combined for w in ["victory_header", "victory", "mission rewards", "stage clear", "loot chest"]):
                return "Victory & Mission Rewards", "Battle victory rewards, loot chest, and score ranking"
            elif any(w in combined for w in ["arena_header", "arena", "combat hud", "cast skill", "health_mana_bar"]):
                return "Active Gameplay Arena", "Real-time combat controls, skill casting, and health gauge"
            elif any(w in combined for w in ["inventory_header", "equipped weapon", "armor", "skill tree"]):
                return "Character & Equipment Inventory", "Hero equipment, weapons, and skill attributes"
            elif any(w in combined for w in ["lobby_title", "game lobby", "level map", "start_level", "lucky spin"]):
                return "Game Lobby & Level Map", "Campaign roadmap, energy lives, and level launcher"
            return "Game Arena View", "Interactive game screen and gameplay controls"

        # 4. Food Delivery & Dining
        if any(w in combined for w in ["search_food", "cuisine_pizza", "restaurant_card", "dish_title", "topping_cheese", "cart_header", "place food order", "order_status", "courier_info"]):
            if any(w in combined for w in ["restaurant discovery", "search_food", "cuisine_pizza", "food_header"]):
                return "Restaurant Discovery & Feed", "Restaurant discovery, food categories, and top-rated eateries"
            elif any(w in combined for w in ["menu", "dish_title", "topping_cheese", "customizer"]):
                return "Restaurant Menu & Customizer", "Menu item customization, portion options, and add-ons"
            elif any(w in combined for w in ["delivery cart", "place food order", "cart_item", "promo code"]):
                return "Delivery Cart & Summary", "Food basket, coupon discounts, and delivery address"
            elif any(w in combined for w in ["tracking_header", "order_status", "courier", "call courier"]):
                return "Live Order & Driver Tracking", "Real-time order progress and courier GPS navigation"
            return "Food Delivery Hub", "Food delivery and ordering view"

        # 5. Finance, Banking & Crypto
        if any(w in combined for w in ["portfolio_header", "balance_amount", "chart_ticker", "order_book", "btn_tab_buy", "btn_confirm_order", "tx_item", "enable_2fa"]):
            if any(w in combined for w in ["portfolio", "balance_amount", "deposit funds", "withdraw cash"]):
                return "Portfolio Dashboard & Balance", "Total balance, profit/loss metrics, and asset distribution"
            elif any(w in combined for w in ["candlestick", "chart_ticker", "order_book", "timeframe"]):
                return "Market Watchlist & Live Chart", "Real-time asset price charts, order books, and market pairs"
            elif any(w in combined for w in ["trade_header", "buy asset", "sell asset", "btn_confirm_order"]):
                return "Trade Execution & Buy/Sell", "Order placement, buy/sell toggles, and trade execution"
            elif any(w in combined for w in ["security_header", "tx_item", "enable_2fa", "biometric"]):
                return "Transaction History & Security", "Past transfers, transaction records, and security authentication"
            return "Financial Assets View", "Financial asset management and trade portfolio"

        # 6. Shopping & E-Commerce
        if any(w in combined for w in ["deal_banner", "cat_electronics", "product_card", "variant_color", "review_summary", "btn_add_cart", "checkout_header", "btn_place_secure_order"]):
            if any(w in combined for w in ["storefront deals", "deal_banner", "flash deal"]):
                return "Storefront Deals & Highlights", "Featured retail deals, trending products, and promotions"
            elif any(w in combined for w in ["filtered product catalog", "filter_price", "sort_rating", "catalog_header"]):
                return "Filtered Product Catalog", "Product discovery catalog, search filters, and sorting"
            elif any(w in combined for w in ["product details", "variant_color", "review_summary", "btn_add_cart"]):
                return "Product Details & Reviews", "Item specifications, photo gallery, and verified reviews"
            elif any(w in combined for w in ["checkout_header", "shipping_method", "payment_method", "place_secure_order"]):
                return "Cart & Secure Checkout", "Shopping cart, shipping address, and payment checkout"
            return "Shopping Storefront", "E-commerce shopping catalog and product view"

        # 7. Travel, Rides & Lodging
        if any(w in combined for w in ["input_destination", "saved_home", "fare_header", "ride_standard", "nav_header", "driver_eta", "trip_summary_header", "rate_5_stars"]):
            if any(w in combined for w in ["destination search", "input_destination", "saved_home"]):
                return "Ride & Destination Search Map", "Pickup/dropoff destination search and interactive map"
            elif any(w in combined for w in ["fare estimate", "ride_standard", "ride_comfort"]):
                return "Fare Estimate & Vehicle Selector", "Ride tier options, fare estimates, and booking confirmation"
            elif any(w in combined for w in ["live route", "nav_header", "driver_eta", "contact driver"]):
                return "Live Route Navigation & Driver ETA", "Driver real-time GPS tracking and estimated arrival"
            elif any(w in combined for w in ["trip summary", "receipt_total", "rate_5_stars", "tip driver"]):
                return "Trip Summary & Driver Rating", "Trip receipt, fare breakdown, and driver rating"
            return "Travel & Rides Hub", "Travel navigation and ride booking"

        # 8. Health, Fitness & Sports
        if any(w in combined for w in ["step_counter", "calories_duration", "workout_header", "set_item", "biometrics_header", "heart_rate_value", "community_header", "challenge_rank"]):
            if any(w in combined for w in ["activity tracker", "step_counter", "calories_duration"]):
                return "Activity Tracker & Daily Goals", "Step counters, active calories, and daily goal progress"
            elif any(w in combined for w in ["workout routine", "workout_header", "set_item", "log_set"]):
                return "Workout Routine & Logger", "Workout routine tracker, set/rep logging, and rest timer"
            elif any(w in combined for w in ["heart rate", "biometrics_header", "sleep_score"]):
                return "Heart Rate & Biometrics Analytics", "Cardio zones, sleep tracking, and biometrics history"
            elif any(w in combined for w in ["community_header", "challenge_rank", "share_workout"]):
                return "Fitness Community & Challenges", "Community leaderboard, fitness challenges, and achievements"
            return "Fitness & Health Dashboard", "Health biometrics and activity metrics"

        # 9. Productivity, Office & Notes
        if any(w in combined for w in ["workspace_header", "btn_create_doc", "kanban_header", "task_card", "editor_header", "input_doc_title", "workspace_settings_header", "invite_team"]):
            if any(w in combined for w in ["workspace projects", "workspace_header", "doc_item"]):
                return "Workspace Projects & Notebooks", "Project notebooks, workspace directory, and quick notes"
            elif any(w in combined for w in ["kanban board", "kanban_header", "task_card", "move_done"]):
                return "Kanban Board & Task Manager", "Task workflow boards, to-do lists, and sprint tracking"
            elif any(w in combined for w in ["document editor", "editor_header", "input_doc_body"]):
                return "Document Editor & Rich Text", "Document editing workspace, formatting toolbar, and content"
            elif any(w in combined for w in ["workspace settings", "invite_team", "export_docs"]):
                return "Workspace Settings & Collaboration", "Team member permissions, document sharing, and export"
            return "Productivity Workspace", "Productivity tasks, document editor, and notes"

        # 10. Terminal / Command Console (Windows Terminal / Dev Tools)
        if any(w in combined for w in ["terminal", "powershell", "command palette", "cmd.exe", "wsl", "console buffer", "split pane", "keybind", "cascadia"]):
            if "palette_title" in combined or "palette_search" in combined or "type a terminal action" in combined:
                return "Command Palette", "Interactive command palette and terminal action launcher"
            elif "scheme" in combined or "color" in combined or "font" in combined or "acrylic" in combined:
                return "Appearance & Color Schemes", "Terminal appearance, fonts, and color configuration"
            elif "keybind" in combined or "copy text" in combined or "paste text" in combined:
                return "Actions & Keybindings", "Keyboard shortcuts and action keybindings configuration"
            return "PowerShell Console Tab", "Active PowerShell command-line shell and buffer"

        # 11. Social Media & Creator Hub (Instagram, TikTok)
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

        # 12. Audio / Music Streaming (Spotify, Podcasts)
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

        # 13. Chat & Messaging (WhatsApp, Slack, Telegram)
        if any(w in combined for w in ["whatsapp", "slack", "chat", "voice note", "attach photo", "direct message", "channel", "typing...", "status", "update", "updates", "conversation", "calls"]):
            if "online" in combined or "voice call" in combined or "type a message" in combined or "attach" in combined:
                return "Direct Message Conversation", "Interactive direct message conversation and media sharing"
            elif "status" in combined or "update" in combined or "updates" in combined:
                return "Status & Broadcast Updates", "Live status updates and broadcast channels"
            elif "channel" in combined:
                return "Channel Discussion", "Group workspace and channel discussion feed"
            return "Chats Hub", "Recent message conversations and active chat list"

        # 14. Learning & Education (Duolingo)
        if any(w in combined for w in ["duolingo", "lesson", "streak", "translate", "practice mistake", "diamond league", "xp points", "start lesson"]):
            if "translate" in combined or "exercise" in combined or "check answer" in combined:
                return "Learning Exercise Quiz", "Interactive language lesson and translation quiz"
            elif "league" in combined or "leaderboard" in combined:
                return "League Leaderboard", "Competitive weekly XP leaderboard and reward chest"
            return "Learning Path", "Curriculum unit roadmap, streak status, and lesson tree"

        # 15. Dynamic Header Extraction from topmost Title / Header element
        for elem in elements:
            if elem.text and not elem.clickable and elem.type in ("text", "view"):
                # Check for "App - Subtitle" format
                if " - " in elem.text:
                    sub_title = elem.text.split(" - ")[-1].strip()
                    if 3 <= len(sub_title) <= 40:
                        return sub_title, f"Functional {sub_title.lower()} view"
                elif 3 <= len(elem.text.strip()) <= 32:
                    return elem.text.strip(), f"Functional {elem.text.strip().lower()} view"

        # 16. Fallbacks
        if any(w in combined for w in ["dashboard", "home", "overview"]):
            return "Home & Overview", "Main application landing view and activity overview"
        elif any(w in combined for w in ["search", "filter", "find"]):
            return "Search & Filter", "Search queries, filters, and discovery view"
        elif any(w in combined for w in ["settings", "preferences", "config"]):
            return "Settings & Preferences", "Application configuration and account preferences"

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
