import reflex as rx


COLORS = {
    "background": "#F5F7F6",
    "surface": "#FFFFFF",
    "primary": "#1B5E20",
    "primary_light": "#2E7D32",
    "text": "#172117",
    "muted": "#6B756B",
    "border": "#DDE4DD",
    "danger": "#C62828",
}


def page_style():

    return {
        "min_height": "100vh",
        "background": COLORS["background"],
        "color": COLORS["text"],
        "font_family": "Inter, Arial, sans-serif",
    }


def card_style():

    return {
        "background": COLORS["surface"],
        "border": f"1px solid {COLORS['border']}",
        "border_radius": "18px",
        "padding": "24px",
        "box_shadow": "0 8px 30px rgba(0,0,0,0.05)",
    }