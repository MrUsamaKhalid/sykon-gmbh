# Sykon ABS GmbH design tokens — GENERATED, DO NOT EDIT.
# Source: brand/tokens/sykon.tokens.json
# Rebuild: node brand/tokens/build.mjs
# 
# Sykon Aluminium Building Systems is NOT Sykon Properties.
# Do not import Sykon Properties assets, colours or type into this system.

RED           = "#C11720"
RED_HOVER     = "#DC1A25"
RED_ON_DARK   = "#DC1A25"   # large display type on dark only
RED_TINT_29   = "#ECB4B7"
RED_TINT_17   = "#F4CED0"
RED_TINT_12   = "#F7D9DB"
INK           = "#1C1C1A"
PAGE          = "#FFFFFF"        # the catalogue page ground
PAPER         = "#FEF4F4"
PAPER_WARM    = "#F1E9E8"
SURFACE_COOL  = "#F2F2F2"
PAPER_COOL    = "#E0E0E1"

# NON-BRAND. Construction/anatomy artwork only. Never on a brand surface.
DOC_GRID_LINE = "#E10916"

FONT_TEXT     = "Hanken Grotesk"
FONT_FALLBACK = ["Helvetica Neue","Arial","sans-serif"]

W_LIGHT, W_REGULAR, W_MEDIUM, W_BOLD = 300, 400, 500, 700

LEAD_DISPLAY = 1.356
LEAD_BODY    = 1.585
LEAD_CAPTION = 1.355
LEAD_TIGHT   = 0.848

MARGIN_MM = 16
BLEED_MM  = 3
GUTTER_MM = 6

PAGE_W_MM = 210
PAGE_H_MM = 297

SYMBOL_VIEWBOX = "0 0 225.679 100"
SYMBOL_ASPECT  = 2.2568
SYMBOL_PATH    = "M125.777 0 L125.777 17.903 L140.590 17.903 L101.356 43.631 L61.419 17.903 L75.982 17.903 L75.982 0 L0 0 L0 17.903 L25.970 17.903 L83.962 54.879 L17.553 98.669 L17.970 100 L49.981 100 L174.727 17.903 L225.679 17.903 L225.679 0 Z"
SYMBOL_T       = 0.17903          # bar thickness / height — the spacing module
CLEAR_SPACE_T  = 1.5                            # multiples of SYMBOL_T, all four sides
MIN_H_PRINT_MM = 12
MIN_H_SCREEN_PX = 34

# Red on ink measures 2.77:1 — below 3:1. On dark grounds red is a
# GRAPHIC FILL ONLY, never text. Dark-surface copy uses PAPER.
RED_IS_TEXT_SAFE_ON_INK = False
