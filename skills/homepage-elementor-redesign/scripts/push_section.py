#!/usr/bin/env python3
"""Push incrementale di UNA sezione della homepage (Canale B — endpoint /elementor-section).

È lo script del loop di FASE 4: una chiamata per sezione, nell'ordine della Section Map.

Uso:
  export WP_URL=... WP_USER=... WP_APP_PASSWORD=...
  python push_section.py hero.json --page-id 123                       # append/replace per css_id
  python push_section.py hero.json --page-id 123 --position 1          # inserisci in posizione
  python push_section.py --page-id 123 --remove sec-hero               # rimuovi sezione
  python push_section.py hero.json --page-id 123 --save-block "Cliente — Hero"   # anche in libreria

Il file JSON deve contenere IL SINGOLO container root della sezione,
con settings.css_id valorizzato (es. "sec-hero").
"""
import argparse, base64, json, os, sys
import urllib.request


def call(endpoint: str, body: dict) -> dict:
    url = os.environ["WP_URL"].rstrip("/") + "/wp-json/agenzia/v1/" + endpoint
    auth = base64.b64encode(f'{os.environ["WP_USER"]}:{os.environ["WP_APP_PASSWORD"]}'.encode()).decode()
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Basic " + auth},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} su /{endpoint}: {e.read().decode()[:500]}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("section_file", nargs="?", help="JSON del container della sezione")
    p.add_argument("--page-id", type=int, required=True)
    p.add_argument("--position", type=int, default=None)
    p.add_argument("--remove", metavar="CSS_ID", help="rimuovi la sezione con questo css_id")
    p.add_argument("--save-block", metavar="TITOLO", help="salva anche come blocco in libreria")
    args = p.parse_args()

    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD"):
        if not os.environ.get(var):
            sys.exit(f"Variabile d'ambiente mancante: {var}")

    if args.remove:
        out = call("elementor-section", {"page_id": args.page_id, "mode": "remove", "css_id": args.remove})
    else:
        if not args.section_file:
            sys.exit("Serve il file JSON della sezione (o --remove).")
        with open(args.section_file, encoding="utf-8") as f:
            section = json.load(f)
        css_id = section.get("settings", {}).get("css_id")
        if not css_id or not css_id.startswith("sec-"):
            sys.exit('La sezione deve avere settings.css_id nel formato "sec-<slug>".')

        body = {"page_id": args.page_id, "mode": "append", "section": section}
        if args.position is not None:
            body["position"] = args.position
        out = call("elementor-section", body)

        if args.save_block:
            blk = call("elementor-library-block", {"title": args.save_block, "section": section})
            print(f"📚 Blocco in libreria: id={blk['template_id']} «{blk['title']}»")

    print("Sezioni sulla pagina:", " → ".join(out["sections"]))
    print(f"✅ {out['url']}")


if __name__ == "__main__":
    main()
