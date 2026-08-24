#!/usr/bin/env python3
"""
validate_json.py — Validazione pre-push del JSON Elementor.

Da eseguire OBBLIGATORIAMENTE prima di ogni push (FASE 4, punto 5.2.3).
Fallire qui in un secondo è meglio che spingere JSON rotto sullo staging.

Uso:
    python3 validate_json.py <file.json> [--section]

Accetta:
  - un array root di elementi (formato _elementor_data)
  - un singolo container di sezione (dict)
  - un page-state.json ({slug: container, ...})

Con --section pretende che ogni root sia un container con css_id "sec-<slug>".

Exit code: 0 = OK (anche con warning), 1 = errori bloccanti.
"""

import json
import re
import sys

# Widget consentiti nelle demo (core free + Pro usati dalla skill; vedi widget-map.md)
WIDGET_WHITELIST = {
    # free core
    "heading", "text-editor", "button", "image", "icon", "icon-box", "icon-list",
    "counter", "spacer", "divider", "image-carousel", "image-box", "star-rating",
    "video", "google_maps", "social-icons", "text-path", "tabs", "accordion", "toggle",
    # pro
    "nav-menu", "theme-site-logo", "form", "call-to-action", "posts", "loop-grid",
    "animated-headline", "price-list", "price-table", "testimonial-carousel",
    "slides", "flip-box", "media-carousel", "hotspot", "table-of-contents",
}
# Vietati nelle demo (vedi widget-map.md "Widget da NON usare")
WIDGET_FORBIDDEN = {"posts", "portfolio", "template", "shortcode"}
WIDGET_FORBIDDEN_PREFIX = ("woocommerce-",)
WIDGET_WARN = {"html", "loop-grid"}

ID_RE = re.compile(r"^[a-z0-9]{7,8}$")
HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")

# chiavi settings considerate "critiche" per il responsive sui container
RESPONSIVE_CRITICAL = ("padding", "flex_direction", "flex_gap")
# chiavi colore testo tipiche da confrontare col background del medesimo elemento
TEXT_COLOR_KEYS = ("title_color", "text_color", "color", "heading_color",
                   "description_color", "button_text_color", "icon_color")
BG_COLOR_KEYS = ("background_color", "button_background_color", "background_overlay_color")

errors, warnings, infos = [], [], []


def err(msg): errors.append("  ✗ " + msg)
def warn(msg): warnings.append("  ⚠ " + msg)
def info(msg): infos.append("  · " + msg)


def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rel_luminance(rgb):
    def chan(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(hex1, hex2):
    l1, l2 = rel_luminance(hex_to_rgb(hex1)), rel_luminance(hex_to_rgb(hex2))
    lo, hi = min(l1, l2), max(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def walk(el, path, seen_ids, parent_bg=None):
    """Visita ricorsiva di un elemento Elementor."""
    if not isinstance(el, dict):
        err(f"{path}: elemento non è un oggetto JSON")
        return

    el_id = el.get("id")
    el_type = el.get("elType")
    settings = el.get("settings") or {}
    label = f"{path} [{el_type or '?'}/{settings.get('css_id') or el.get('widgetType') or el_id or '?'}]"

    # --- ID ---
    if not el_id:
        err(f"{label}: manca 'id'")
    else:
        if not ID_RE.match(str(el_id)):
            err(f"{label}: id '{el_id}' non valido (attesi 7-8 char alfanumerici minuscoli)")
        if el_id in seen_ids:
            err(f"{label}: id '{el_id}' DUPLICATO (già visto in {seen_ids[el_id]})")
        else:
            seen_ids[el_id] = path

    # --- elType / widgetType ---
    if el_type == "widget":
        wt = el.get("widgetType")
        if not wt:
            err(f"{label}: widget senza 'widgetType'")
        else:
            if wt in WIDGET_FORBIDDEN or any(wt.startswith(p) for p in WIDGET_FORBIDDEN_PREFIX):
                err(f"{label}: widget '{wt}' VIETATO nelle demo (dipende da contenuti/plugin dello staging)")
            elif wt in WIDGET_WARN:
                warn(f"{label}: widget '{wt}' sconsigliato in demo (vedi widget-map.md)")
            elif wt not in WIDGET_WHITELIST:
                warn(f"{label}: widget '{wt}' non in whitelist — verificare che esista sull'ambiente")
        if el.get("elements"):
            err(f"{label}: un widget non può avere 'elements' figli")
    elif el_type == "container":
        # responsive esplicito sui container
        for key in RESPONSIVE_CRITICAL:
            if key in settings and f"{key}_mobile" not in settings:
                warn(f"{label}: '{key}' impostato senza override '_mobile' (regola responsive non negoziabile)")
        if settings.get("flex_direction") == "row" and "flex_direction_mobile" not in settings:
            warn(f"{label}: flex row senza 'flex_direction_mobile' (su mobile quasi sempre serve 'column')")
    elif el_type == "section" or el_type == "column":
        err(f"{label}: elType legacy '{el_type}' — solo Flexbox Container ammessi")
    else:
        err(f"{label}: elType '{el_type}' sconosciuto")

    # --- Contrasto WCAG (euristica: colori hex nello stesso elemento) ---
    bg = None
    for k in BG_COLOR_KEYS:
        v = settings.get(k)
        if isinstance(v, str) and HEX_RE.match(v):
            bg = (k, v)
            break
    if bg is None and parent_bg:
        bg = parent_bg
    if bg:
        for k in TEXT_COLOR_KEYS:
            v = settings.get(k)
            if isinstance(v, str) and HEX_RE.match(v):
                ratio = contrast_ratio(v, bg[1])
                if ratio < 4.5:
                    warn(f"{label}: contrasto {ratio:.2f}:1 tra {k}={v} e {bg[0]}={bg[1]} (< 4.5:1 WCAG)")

    # --- hex hardcoded vs __globals__ ---
    globals_used = settings.get("__globals__") or {}
    for k, v in settings.items():
        if isinstance(v, str) and HEX_RE.match(v) and k not in globals_used:
            infos.append(None)  # solo conteggio

    own_bg = None
    for k in ("background_color",):
        v = settings.get(k)
        if isinstance(v, str) and HEX_RE.match(v):
            own_bg = (k, v)
    for i, child in enumerate(el.get("elements") or []):
        walk(child, f"{path}.elements[{i}]", seen_ids, own_bg or parent_bg)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    section_mode = "--section" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(1)

    try:
        with open(args[0], encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"✗ ERRORE FATALE: impossibile leggere/parsare {args[0]}: {e}")
        sys.exit(1)

    # normalizza nei tre formati accettati
    if isinstance(data, dict) and "elType" in data:
        roots = {"(sezione)": data}
    elif isinstance(data, dict):  # page-state.json
        roots = data
    elif isinstance(data, list):
        roots = {f"root[{i}]": el for i, el in enumerate(data)}
    else:
        print("✗ ERRORE FATALE: formato non riconosciuto")
        sys.exit(1)

    seen_ids = {}
    for name, el in roots.items():
        if section_mode or isinstance(data, dict):
            css_id = (el.get("settings") or {}).get("css_id", "") if isinstance(el, dict) else ""
            if not str(css_id).startswith("sec-"):
                err(f"{name}: container root senza settings.css_id 'sec-<slug>' (trovato: '{css_id}')")
            if isinstance(el, dict) and el.get("elType") != "container":
                err(f"{name}: il root di una sezione deve essere un container")
        walk(el, name, seen_ids)

    hex_count = infos.count(None)
    print(f"— validate_json.py · {args[0]} · {len(seen_ids)} elementi —")
    if errors:
        print(f"\nERRORI BLOCCANTI ({len(errors)}):")
        print("\n".join(errors))
    if warnings:
        print(f"\nWARNING ({len(warnings)}):")
        print("\n".join(warnings))
    if hex_count:
        print(f"\nINFO: {hex_count} colori hex hardcoded — valuta se referenziare i Global Colors (__globals__)")
    if not errors and not warnings:
        print("✓ Nessun problema rilevato")
    elif not errors:
        print(f"\n✓ Nessun errore bloccante ({len(warnings)} warning da valutare)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
