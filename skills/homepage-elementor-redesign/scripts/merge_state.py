#!/usr/bin/env python3
"""Fonde page-state.json (sezioni nominate, ordinate) nell'array _elementor_data — Canale A (WP-CLI).

page-state.json è la fonte di verità locale del layout:
{
  "menu":   { ...container con settings.css_id="sec-menu"... },
  "hero":   { ...container con settings.css_id="sec-hero"... },
  "chi-siamo": { ... },
  ...
}
L'ordine delle chiavi = ordine delle sezioni in pagina.

Uso nel loop di FASE 4 (dopo ogni sezione aggiunta/modificata nello stato):
  python merge_state.py page-state.json > /tmp/homepage.json
  scp /tmp/homepage.json $HOST:/tmp/
  ssh $HOST "cd $WP_PATH && wp post meta update $PAGE_ID _elementor_data \"$(cat /tmp/homepage.json)\" && wp elementor flush-css"

Opzioni:
  --only hero            valida/emette comunque l'intera pagina, ma verifica che la sezione esista
  --check                solo validazione (id univoci, css_id presenti, JSON valido), nessun output
"""
import argparse, json, sys


def collect_ids(el, ids):
    ids.append(el.get("id", ""))
    for child in el.get("elements", []):
        collect_ids(child, ids)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("state_file")
    p.add_argument("--only", help="slug sezione che deve essere presente nello stato")
    p.add_argument("--check", action="store_true")
    args = p.parse_args()

    with open(args.state_file, encoding="utf-8") as f:
        state = json.load(f)
    if not isinstance(state, dict) or not state:
        sys.exit("page-state.json deve essere un oggetto {slug: container} non vuoto.")

    errors = []
    data, all_ids = [], []
    for slug, section in state.items():
        css_id = section.get("settings", {}).get("css_id", "")
        if css_id != f"sec-{slug}":
            errors.append(f"Sezione '{slug}': settings.css_id atteso 'sec-{slug}', trovato '{css_id}'.")
        if section.get("elType") != "container":
            errors.append(f"Sezione '{slug}': elType deve essere 'container'.")
        collect_ids(section, all_ids)
        data.append(section)

    dupes = {i for i in all_ids if all_ids.count(i) > 1 or not i}
    if dupes:
        errors.append(f"ID elemento duplicati o vuoti: {sorted(dupes)}")
    if args.only and args.only not in state:
        errors.append(f"Sezione '{args.only}' non presente nello stato.")

    if errors:
        sys.exit("VALIDAZIONE FALLITA:\n- " + "\n- ".join(errors))
    if args.check:
        print(f"OK: {len(data)} sezioni, {len(all_ids)} elementi, id univoci.", file=sys.stderr)
        return
    json.dump(data, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
