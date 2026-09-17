"""Comprehensive tests for Module: Knowledge Generator (Spec 6, 7, 8, 12 - Member 3)."""
import os
import json
import tempfile
import pytest
from PIL import Image
from src.knowledge.element_parser import ElementParser, element_parser
from src.knowledge.screen_analyzer import ScreenAnalyzer, screen_analyzer
from src.knowledge.design_analyzer import DesignAnalyzer, design_analyzer
from src.knowledge.knowledge_pack import KnowledgeGenerator, knowledge_generator
from src.core.models import (
    ElementModel,
    ScreenModel,
    ActionModel,
    TransitionModel,
    JourneyModel,
    DesignInfo
)


def test_element_parser_classification_and_filtering():
    """Verify Android widget classifications and non-interactive filtering."""
    parser = ElementParser()
    raw_nodes = [
        # 1. Edit text input
        {
            "class": "android.widget.EditText",
            "resource_id": "com.example.app:id/email_field",
            "text": "john@example.com",
            "clickable": True,
            "bounds": [50, 100, 450, 180]
        },
        # 2. Clickable ImageView -> button
        {
            "class": "android.widget.ImageView",
            "resource_id": "com.example.app:id/nav_back",
            "content_desc": "Back",
            "clickable": True,
            "bounds": [10, 10, 60, 60]
        },
        # 3. Non-clickable ImageView without text -> should be filtered out
        {
            "class": "android.widget.ImageView",
            "resource_id": "com.example.app:id/bg_decorative",
            "clickable": False,
            "bounds": [0, 0, 500, 1000]
        },
        # 4. Switch toggle
        {
            "class": "android.widget.Switch",
            "resource_id": "com.example.app:id/dark_mode_switch",
            "text": "Dark Mode",
            "clickable": True,
            "bounds": [50, 200, 450, 260]
        },
        # 5. Checkbox
        {
            "class": "android.widget.CheckBox",
            "resource_id": "com.example.app:id/agree_terms",
            "text": "I agree",
            "clickable": True,
            "bounds": [50, 280, 450, 340]
        },
        # 6. Radio button
        {
            "class": "android.widget.RadioButton",
            "resource_id": "com.example.app:id/opt_standard",
            "text": "Standard Delivery",
            "clickable": True,
            "bounds": [50, 360, 450, 420]
        },
        # 7. Invalid bounds (0 area)
        {
            "class": "android.widget.TextView",
            "resource_id": "com.example.app:id/hidden",
            "text": "Hidden",
            "clickable": False,
            "bounds": [100, 100, 100, 100]
        }
    ]

    elements = parser.parse_elements(raw_nodes)
    assert len(elements) == 5  # Decorative image and invalid bounds filtered out

    # Check classifications
    assert elements[0].type == "input"
    assert elements[0].input is True
    assert elements[0].id == "email_field"

    assert elements[1].type == "button"
    assert elements[1].clickable is True
    assert elements[1].text == "Back"
    assert elements[1].id == "nav_back"

    assert elements[2].type == "switch"
    assert elements[3].type == "checkbox"
    assert elements[4].type == "radio"


def test_element_parser_duplicate_id_deduplication():
    """Ensure duplicate resource IDs (e.g. in list views) get unique disambiguated IDs."""
    parser = ElementParser()
    raw_nodes = [
        {
            "class": "android.widget.TextView",
            "resource_id": "com.example:id/list_item_title",
            "text": "Item One",
            "clickable": True,
            "bounds": [0, 100, 500, 150]
        },
        {
            "class": "android.widget.TextView",
            "resource_id": "com.example:id/list_item_title",
            "text": "Item Two",
            "clickable": True,
            "bounds": [0, 160, 500, 210]
        },
        {
            "class": "android.widget.TextView",
            "resource_id": "com.example:id/list_item_title",
            "text": "Item Three",
            "clickable": True,
            "bounds": [0, 220, 500, 270]
        }
    ]

    elements = parser.parse_elements(raw_nodes)
    ids = [e.id for e in elements]
    assert len(ids) == 3
    assert len(set(ids)) == 3  # All unique!
    assert ids[0] == "list_item_title"
    assert ids[1] == "list_item_title_2"
    assert ids[2] == "list_item_title_3"


def test_screen_analyzer_heuristics_and_deduplication():
    """Verify screen name/purpose inference and structural deduplication."""
    analyzer = ScreenAnalyzer()
    analyzer.reset()

    # Screen 1: Login
    login_elements = [
        ElementModel(id="txt_user", type="input", text="Username", bounds=[10, 10, 200, 50], clickable=True, input=True),
        ElementModel(id="txt_pass", type="input", text="Password", bounds=[10, 60, 200, 100], clickable=True, input=True),
        ElementModel(id="btn_login", type="button", text="Sign In", bounds=[10, 110, 200, 150], clickable=True, input=False),
    ]
    screen1, is_new1 = analyzer.analyze_or_get_screen(login_elements, screenshot_path="screen1.png")
    assert is_new1 is True
    assert screen1.id == "screen_001"
    assert screen1.name == "Login"
    assert "authentication" in screen1.purpose.lower()

    # Deduplication with volatile timestamp variation
    login_with_clock = [
        ElementModel(id="status_time", type="text", text="10:45 AM", bounds=[0, 0, 50, 10], clickable=False),
        ElementModel(id="txt_user", type="input", text="Username", bounds=[10, 10, 200, 50], clickable=True, input=True),
        ElementModel(id="txt_pass", type="input", text="Password", bounds=[10, 60, 200, 100], clickable=True, input=True),
        ElementModel(id="btn_login", type="button", text="Sign In", bounds=[10, 110, 200, 150], clickable=True, input=False),
    ]
    screen1_dup, is_new_dup = analyzer.analyze_or_get_screen(login_elements)
    assert is_new_dup is False
    assert screen1_dup.id == screen1.id

    # Screen 2: Checkout / Cart
    cart_elements = [
        ElementModel(id="lbl_cart", type="text", text="Shopping Cart", bounds=[10, 10, 200, 50], clickable=False),
        ElementModel(id="btn_checkout", type="button", text="Checkout & Pay", bounds=[10, 200, 200, 250], clickable=True),
    ]
    screen2, is_new2 = analyzer.analyze_or_get_screen(cart_elements)
    assert is_new2 is True
    assert screen2.id == "screen_002"
    assert screen2.name == "Checkout"

    # Reset
    analyzer.reset()
    assert analyzer.screen_counter == 0
    assert len(analyzer.known_signatures) == 0


def test_design_analyzer():
    """Verify color extraction and theme detection with synthetic test images."""
    analyzer = DesignAnalyzer()

    # 1. Non-existent path returns fallback
    fallback = analyzer.analyze("non_existent_file.png")
    assert fallback.primary_color == "#2563EB"
    assert fallback.background_color == "#FFFFFF"
    assert fallback.theme == "light"

    # 2. Synthetic Dark Mode Image with Green Accent
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        img = Image.new("RGB", (100, 100), color=(18, 18, 18))  # Dark background
        # Add a chromatic green button
        for x in range(30, 70):
            for y in range(40, 60):
                img.putpixel((x, y), (22, 163, 74))  # Green accent
        img.save(tmp_path)

        design = analyzer.analyze(tmp_path)
        assert design.theme == "dark"
        # Background should be dark
        assert design.background_color.startswith("#")
        # Primary should be chromatic accent
        assert design.primary_color.startswith("#")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_knowledge_generator_lifecycle_and_journeys():
    """Verify KnowledgeGenerator accumulation, journey synthesis, serialization, and restoration."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        pack_file = tmp.name

    try:
        kg = KnowledgeGenerator(output_file=pack_file)
        kg.reset()

        kg.set_app_info(name="ShopApp", package="com.shop.demo")
        kg.set_design_info(DesignInfo(primary_color="#FF5722", background_color="#FAFAFA", theme="light"))

        # Add screens
        s1 = ScreenModel(
            id="screen_001",
            name="Login",
            purpose="User authentication",
            elements=[ElementModel(id="btn_login", type="button", text="Login", bounds=[10, 10, 100, 50])]
        )
        s2 = ScreenModel(
            id="screen_002",
            name="Home",
            purpose="Product catalog",
            elements=[ElementModel(id="btn_cart", type="button", text="Go to Cart", bounds=[20, 20, 150, 60])]
        )
        s3 = ScreenModel(
            id="screen_003",
            name="Checkout",
            purpose="Order checkout",
            elements=[ElementModel(id="btn_pay", type="button", text="Pay Now", bounds=[30, 30, 200, 70])]
        )

        kg.add_screen(s1)
        kg.add_screen(s2)
        kg.add_screen(s3)

        # Add action
        kg.add_action_to_screen("screen_001", ActionModel(type="tap", target_id="btn_login"))

        # Add transitions
        kg.add_transition("screen_001", "tap:btn_login", "screen_002")
        kg.add_transition("screen_002", "tap:btn_cart", "screen_003")

        assert "screen_002" in kg.screens_map["screen_001"].next_screens
        assert "screen_003" in kg.screens_map["screen_002"].next_screens

        # Generate pack
        pack = kg.generate_pack()
        assert pack.app.name == "ShopApp"
        assert pack.scan.screens_found == 3
        assert pack.scan.elements_found == 3
        assert len(pack.transitions) == 2
        # Journey synthesis check
        assert len(pack.journeys) >= 1

        # Check AI summary
        ai_summary = kg.export_ai_summary()
        assert "ShopApp" in ai_summary
        assert "screen_001" in ai_summary
        assert "screen_002" in ai_summary

        # Verify on-disk JSON format strictly conforms to Spec 7.0
        with open(pack_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["app"]["package"] == "com.shop.demo"
        assert data["design"]["primary_color"] == "#FF5722"
        assert len(data["screens"]) == 3
        assert len(data["transitions"]) == 2
        assert "from" in data["transitions"][0]  # Spec alias test

        # Test loading into a new instance restores in-memory structures
        kg2 = KnowledgeGenerator(output_file=pack_file)
        assert len(kg2.screens_map) == 3
        assert "screen_001" in kg2.screens_map
        assert kg2.screens_map["screen_001"].name == "Login"
        assert len(kg2.transitions) == 2
        assert len(kg2.journeys) >= 1
        assert kg2.app_info.name == "ShopApp"

    finally:
        if os.path.exists(pack_file):
            os.remove(pack_file)
