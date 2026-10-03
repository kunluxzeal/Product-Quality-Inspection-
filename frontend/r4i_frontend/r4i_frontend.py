import reflex as rx

from .state import AppState
from .api import CAMERA_STREAM_URL
from .styles import (
    COLORS,
    page_style,
    card_style,
)

def navbar():

    return rx.hstack(

    # --------------------------------------------------------
    # GINGA BRAND
    # --------------------------------------------------------

    rx.link(
        rx.text(
            "Ginja",
            font_size="60px",
            font_weight="800",
            color=COLORS["primary"],
        ),

        href="/",
        text_decoration="none",

        _hover={
            "opacity": "0.8",
        },
    ),

    rx.spacer(),
    

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    rx.hstack(

        # HOME
        rx.link(
            rx.hstack(
                
                rx.icon(
                    "house",
                    size=60,
                ),

                rx.text(
                    "Home",
                     font_size="25px",
                
                    
                ),

                spacing="2",
                align="center",
               
            ),

            href="/",
            color=COLORS["text"],
            text_decoration="none",

            _hover={
                "color": COLORS["primary"],
            },
                 
        ),
   

        # ANALYZE
        rx.link(
            rx.hstack(
                
                rx.icon(
                    "scan-search",
                    size=60,
                ),

                rx.text(
                    "Analyze",
                      font_size="25px",
                    
                ),

                spacing="2",
                align="center",
            ),

            href="/analyze",
            color=COLORS["text"],
            text_decoration="none",

            _hover={
                "color": COLORS["primary"],
            },
        ),

        # SETTINGS
        rx.link(
            rx.hstack(
                rx.icon(
                    "settings",
                    size=60,
                ),

                rx.text(
                    "Settings",
                    font_size="25px",
                ),

                spacing="2",
                align="center",
            ),

            href="/settings",
            color=COLORS["text"],
            text_decoration="none",

            _hover={
                "color": COLORS["primary"],
            },
        ),

        spacing="8",
        align="center",
    ),

    width="100%",
    max_width="1800px",
    margin="0 auto",
    padding="22px 30px",
    align="center",
    
)



# ============================================================
# HOME PAGE
# ============================================================

def home_page():

    return rx.box(

        navbar(),

        rx.center(

            rx.vstack(

               
                rx.text(
                    "Ginja",
                    font_size=[
                        "160px",
                        "160px",
                    ],
                    font_weight="900",
                    color=COLORS["primary"],
                    letter_spacing="-3px",
                ),
              

                rx.text(
                    "AI-powered ginger quality inspection",
                    font_size="55px",
                    color=COLORS["muted"],
                    text_align="center",
                ),

                rx.text(
                    "Inspect ginger instantly using "
                    "on-device computer vision.",
                    font_size="30px",
                    color=COLORS["muted"],
                    text_align="center",
                    max_width="600px",
                ),
                rx.spacer(),
                rx.spacer(),
                rx.spacer(),
              
              


                rx.link(

                    rx.button(
                        "Start",
                        size="4",
                        background=COLORS["primary"],
                        color="white",
                        border_radius="45px",
                        padding="55px 140px",
                        font_size="55px",
                        cursor="pointer",
                        _hover={
                            "background": COLORS[
                                "primary_light"
                            ],
                        },
                    ),

                    href="/analyze",
                    text_decoration="none",
                ),

                spacing="6",
                align="center",
                # Move hero content upward
                transform="translateY(-60px)",
                
            ),

            min_height="calc(100vh - 90px)",
        ),

        style=page_style(),
    )


# ============================================================
# RESULT CARD
# ============================================================

def result_card():

    return rx.cond(

        AppState.prediction != "",

        rx.vstack(

            rx.hstack(

                rx.text(
                    "Analysis Result",
                    font_size="45px",
                    font_weight="400",
                ),

                rx.spacer(),

                rx.badge(
                    AppState.status,
                    color_scheme="green",
                    font_size="20px",
                ),

                width="100%",
                align="center",
            ),

            rx.divider(),

            rx.vstack(

                rx.text(
                    AppState.prediction,
                    font_size="45px",
                    font_weight="800",
                    color=COLORS["primary"],
                    text_align="center",
                ),

                rx.text(
                    AppState.confidence_text,
                    font_size="38px",
                    font_weight="700",
                ),

                rx.text(
                    "Confidence",
                    color=COLORS["muted"],
                    font_size="25px",
                ),

                align="center",
                width="100%",
            ),

            rx.divider(),

            rx.hstack(

                rx.vstack(
                    rx.text(
                        "Inference",
                        color=COLORS["muted"],
                    ),
                    rx.text(
                        AppState.inference_text,
                        font_weight="700",
                    ),
                ),

                rx.vstack(
                    rx.text(
                        "Threshold",
                        color=COLORS["muted"],
                    ),
                    rx.text(
                        (AppState.threshold_text),
                        font_weight="700",
                    ),
                ),

                width="100%",
                justify="between",
                
            ),

            width="100%",
            **card_style(),
        ),

        rx.box(),
    )


# ============================================================
# ANALYZE PAGE
# ============================================================

def analyze_page():

    return rx.box(

        navbar(),

        rx.vstack(

            rx.hstack(

                rx.vstack(

                    rx.text(
                        "Ginger Inspection",
                        font_size="50px",
                        font_weight="800",
                    ),

                    rx.text(
                        "Position the ginger in front "
                        "of the camera and run an analysis.",
                        color=COLORS["muted"],
                        font_size="35px",
                    ),

                    align="start",
                    spacing="1",
                ),

                rx.spacer(),

                rx.cond(

                    AppState.backend_online,

                    rx.badge(
                        "System Online",
                        color_scheme="green",
                        font_size="28px",
                    ),

                    rx.badge(
                        "Checking System",
                        color_scheme="gray",
                    ),
                ),

                width="100%",
                align="center",
            ),

            rx.grid(

                # ------------------------------------------------
                # CAMERA
                # ------------------------------------------------

                rx.vstack(

                    rx.box(

                        rx.image(
                            src=CAMERA_STREAM_URL,
                            width="100%",
                            height="100%",
                            object_fit="cover",
                            border_radius="16px",
                        ),

                        width="100%",
                        aspect_ratio="16/9",
                        overflow="hidden",
                        background="#111",
                        border_radius="16px",
                    ),

                    rx.button(

                        rx.cond(
                            AppState.analyzing,
                            rx.text(
                                "Analyzing...",
                                font_size="28px",
                                font_weight="700",
                            ),
                            rx.text(
                                "Run Analysis",
                                font_size="28px",
                                font_weight="700",
                            ),
                        ),

                        on_click=AppState.run_analysis,

                        loading=AppState.analyzing,

                        width="100%",
                        height="80px",
                        size="4",

                        background=COLORS["primary"],
                        color="white",

                        border_radius="12px",

                        cursor="pointer",

                        _hover={
                            "background": COLORS[
                                "primary_light"
                            ],
                        },
                    ),

                    rx.button(
                        "Clear Result",
                        font_size="28px",
                        font_weight="700",
                        on_click=AppState.clear_result,
                        variant="outline",
                        width="100%",
                        padding="30px 10px",

                        
                    ),

                    width="100%",
                    **card_style(),
                ),

                # ------------------------------------------------
                # RESULT
                # ------------------------------------------------

                rx.vstack(

                    result_card(),

                    rx.cond(

                        AppState.error_message != "",

                        rx.box(

                            rx.text(
                                AppState.error_message,
                                color=COLORS["danger"],
                            ),

                            width="100%",
                            **card_style(),
                        ),

                        rx.box(),
                    ),

                    width="100%",
                    height="100%",
                    align="center",
                ),

                columns={
                    "base": "1",
                    "lg": "3fr 2fr",
                },

                spacing="6",
                width="100%",
            ),

            max_width="1800px",
            margin="0 auto",
            padding="5px 8px",
            width="100%",
            spacing="5",
        ),

        style=page_style(),
    )


# ============================================================
# SETTINGS PAGE
# ============================================================

def settings_page():

    return rx.box(

        navbar(),

        rx.vstack(

            rx.text(
                "Settings",
                font_size="45px",
                font_weight="800",
            ),

            rx.text(
                "Ginga system and model configuration",
                color=COLORS["muted"],
                font_size="35px",
            ),

            rx.grid(

                # ------------------------------------------------
                # MODEL
                # ------------------------------------------------

                rx.vstack(

                    rx.text(
                        "Model",
                        font_size="40px",
                        font_weight="700",
                    ),

                    rx.divider(),

                    rx.hstack(
                        rx.text("Model", font_size="30px",),
                        rx.spacer(),
                        rx.text(
                            AppState.model_name ,
                            font_size="30px",
                        ),
                    ),

                    rx.hstack(
                        rx.text("Input" , font_size="30px"),
                        rx.spacer(),
                        rx.text(
                            AppState.input_shape ,font_size="30px"
                        ),
                    ),

                    rx.hstack(
                        rx.text("Input type",font_size="30px"),
                        rx.spacer(),
                        rx.text(
                            AppState.input_dtype,font_size="30px"
                        ),
                    ),

                    rx.hstack(
                        rx.text("Output",font_size="30px"),
                        rx.spacer(),
                        rx.text(
                            AppState.output_shape,font_size="30px"
                        ),
                    ),

                    rx.hstack(
                        rx.text("Classes",font_size="30px"),
                        rx.spacer(),
                        rx.text(
                            AppState.number_of_classes ,font_size="30px"
                        ),
                    ),

                    rx.hstack(
                        rx.text("Threshold" , font_size="30px"),
                        rx.spacer(),
                        rx.text(
                               AppState.threshold_text, 
                                font_size="30px",
                                font_weight="600",  
                        ),
                    ),

                    width="100%",
                    **card_style(),
                ),

                # ------------------------------------------------
                # SYSTEM
                # ------------------------------------------------

                rx.vstack(

                    rx.text(
                        "System",
                        font_size="40px",
                        font_weight="700",
                    ),

                    rx.divider(),

                    rx.hstack(
                        rx.text("Platform", font_size="30px",),
                        rx.spacer(),
                        rx.text(
                            AppState.platform,
                            font_size="30px"
                        ),
                    ),

                    rx.hstack(
                        rx.text("Architecture",font_size="30px"),
                        rx.spacer(),
                        rx.text(
                            AppState.architecture , font_size="30px"
                        ),
                    ),

                    rx.hstack(
                        rx.text("Python", font_size="30px"),
                        rx.spacer(),
                        rx.text(
                            AppState.python_version, font_size="30px"
                        ),
                    ),

                    rx.hstack(
                        rx.text("Runtime",font_size="30px"),
                        rx.spacer(),
                        rx.text(
                            AppState.runtime, font_size="30px"
                        ),
                    ),

                    rx.hstack(
                        rx.text("Processor",font_size="30px"),
                        rx.spacer(),
                        rx.text(
                            AppState.processor, font_size="30px"
                        ),
                    ),

                    width="100%",
                    **card_style(),
                ),

                columns={
                    "base": "1",
                    "lg": "2",
                },

                spacing="6",
                width="100%",
            ),

            rx.button(
                rx.text(
                    "Refresh System Information",
                    font_size="20px",
                    font_weight="600",
                ),

               
                on_click=AppState.load_system_info,
                variant="outline",
                width="300px",
                height="70px",
                border_radius="14px",
                
            ),

            max_width="1600px",
        
            margin="0 auto",
            padding="30px",
            width="100%",
            spacing="6",
        ),

        style=page_style(),
    )


# ============================================================
# ROUTES
# ============================================================

app = rx.App()

app.add_page(
    home_page,
    route="/",
    title="Ginga",
)

app.add_page(
    analyze_page,
    route="/analyze",
    title="Ginga — Analysis",
    on_load=AppState.load_system_info,
)

app.add_page(
    settings_page,
    route="/settings",
    title="Ginga — Settings",
    on_load=AppState.load_system_info,
)