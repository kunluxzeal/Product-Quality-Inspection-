import reflex as rx

config = rx.Config(
    app_name="r4i_frontend",
    plugins=[
        rx.plugins.RadixThemesPlugin(),
    ],
    vite_allowed_hosts=[
        "entra001.local",
    ],
    backend_host="0.0.0.0",
)