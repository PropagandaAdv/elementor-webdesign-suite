#!/usr/bin/env python3
"""Push di una pagina Elementor su WordPress via mu-plugin elementor-bridge (Canale B).

Uso:
  export WP_URL=https://demo.agenzia.it/cliente
  export WP_USER=agente
  export WP_APP_PASSWORD="xxxx xxxx xxxx xxxx"
  python push_page.py homepage.json --title "Homepage Redesign — Cliente" --status draft [--page-id 123]

homepage.json deve contenere l'ARRAY di elementi root di _elementor_data
(oppure un oggetto template export con chiave "content": viene gestito).
"""
import argparse, json, os, sys
import urllib.request, base64


def main():
    p = argparse.ArgumentParser()
    p.add_argument("json_file")
    p.add_argument("--title", default="Homepage Redesign Demo")
    p.add_argument("--status", default="draft", choices=["draft", "publish", "private"])
    p.add_argument("--page-id", type=int, default=None)
    args = p.parse_args()

    url = os.environ.get("WP_URL", "").rstrip("/")
    user = os.environ.get("WP_USER", "")
    pwd = os.environ.get("WP_APP_PASSWORD", "")
    if not (url and user and pwd):
        sys.exit("Definire WP_URL, WP_USER, WP_APP_PASSWORD nell'ambiente.")

    with open(args.json_file, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "content" in data:  # formato template export
        page_settings = data.get("page_settings") or {"hide_title": "yes"}
        data = data["content"]
    else:
        page_settings = {"hide_title": "yes"}
    if not isinstance(data, list):
        sys.exit("Il file deve contenere un array di elementi root (o un template export).")

    body = {
        "title": args.title,
        "status": args.status,
        "elementor_data": data,
        "page_settings": page_settings,
    }
    if args.page_id:
        body["page_id"] = args.page_id

    req = urllib.request.Request(
        url + "/wp-json/agenzia/v1/elementor-page",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Basic " + base64.b64encode(f"{user}:{pwd}".encode()).decode(),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            out = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:500]}")

    print(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\n✅ Pagina {out.get('page_id')} → {out.get('url')}\n✏️  Editor: {out.get('edit')}")


if __name__ == "__main__":
    main()
