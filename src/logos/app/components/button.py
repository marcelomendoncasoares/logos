"""
Button that copies the given text to the clipboard when clicked.

"""

import json

import streamlit.components.v1 as components


BUTTON_DEFAULT_CSS = {
    "border": "0px",
    "padding": "0px",
    "margin-top": "-1rem",
    "margin-bottom": "-1rem",
    "margin-left": "5px",
    "margin-right": "5px",
    "background-color": "transparent",
    "opacity": "0.3",
    "transition": ".3s",
}

BUTTON_HOVER_CSS = {
    "cursor": "pointer",
    "opacity": "1 !important",
    "transition": ".3s",
}


def copy_to_clipboard_button(  # noqa: PLR0913
    text_to_copy: str,
    *,
    key: str | None = None,
    icon: str = "🖇️",  # "🗐",
    default_css_style: dict[str, str] = BUTTON_DEFAULT_CSS,
    hover_css_style: dict[str, str] = BUTTON_HOVER_CSS,
    height: int = 30,
    width: int = 40,
) -> None:
    """
    Create a button that copies the given text to the clipboard when clicked.

    Args:
        text_to_copy: The text to copy to the clipboard.
        key: The key associated with this button.
        icon: The icon to display on the button.
        default_css_style: The default CSS styles for the button.
        hover_css_style: The CSS styles for the button when hovered.
        height: The height of the button.
        width: The width of the button.
    """

    fn_copy_name = f"fn_{key}"
    default_style_str = " ".join([f"{k}: {v};" for k, v in default_css_style.items()])
    hover_style_str = " ".join([f"{k}: {v};" for k, v in hover_css_style.items()])

    components.html(
        f"""
            <script>
            function {fn_copy_name}() {{
                navigator.clipboard.writeText({json.dumps(text_to_copy)});
            }}
            </script>
            <style>
            div {{
                border: 0px;
                padding: 0px;
                margin-top: -5px;
                overflow: visible;
                margin-bottom: -1rem !important;
                background-color: transparent !important;
            }}
            button {{
                {default_style_str}
            }}
            button:hover {{
                {hover_style_str}
            }}

            </style>
            <div>
                <button
                    kind="secondary"
                    data-testid="baseButton-secondary"
                    height="{height}px"
                    width="{width}px"
                    onclick="{fn_copy_name}()"
                >
                    <div data-testid="stMarkdownContainer">
                        <p style="margin: 0px">{icon}</p>
                    </div>
                </button>
            </div>
        """,
        height=height,
        width=width,
    )
