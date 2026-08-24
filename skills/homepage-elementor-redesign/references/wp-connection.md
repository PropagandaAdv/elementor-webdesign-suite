# Connessione a WordPress — quattro canali operativi

**Ambiente:** nessun ambiente predefinito hardcoded in questa versione del plugin — l'ambiente WordPress (URL, utente, canale d'accesso) lo dichiara l'utente in FASE 0 del SKILL.md, o lo si legge da variabili d'ambiente/`.mcp.json` del progetto. Se il tuo studio/agenzia lavora sempre sullo stesso staging, la scelta più solida è mettere quei valori in un file `.env` locale (mai committato) o in variabili d'ambiente della shell, non nel testo della skill: così il plugin resta riutilizzabile su più clienti/ambienti senza doverlo modificare.

**Sicurezza prima di tutto:** solo staging/demo, mai produzione senza conferma esplicita. Application Password dedicata (revocabile), utente con ruolo minimo necessario (Editor basta per pagine+media; Administrator serve solo per il Kit e i plugin). Nei file di progetto generati (repo, script, deliverable): mai credenziali in chiaro — usare variabili d'ambiente (`WP_URL`, `WP_USER`, `WP_APP_PASSWORD`) o `.env` in `.gitignore`.

**Differenza chiave rispetto a un ambiente Cowork/cloud sandbox:** qui (Claude Code locale, dev container, o Antigravity IDE) il comando `bash`/terminale gira sulla macchina dello sviluppatore o in un container con accesso di rete pieno — non c'è un proxy sandbox che può bloccare la connessione allo staging. Per questo il **Canale A (SSH + WP-CLI)** è la scelta di default quando l'hosting lo supporta: è il canale più completo e diretto. I canali B/B0 restano essenziali quando l'hosting non offre SSH (es. hosting condivisi come one.com) o quando si preferisce l'automazione via MCP.

---

## Canale A — SSH + WP-CLI (preferito quando l'hosting lo supporta)

Verifica e setup:
```bash
ssh $HOST "cd $WP_PATH && wp core version && wp plugin get elementor --field=version && wp plugin is-active elementor-pro && echo PRO_OK"
```

Workflow completo:
```bash
# 1. Crea pagina draft con template canvas
PAGE_ID=$(wp post create --post_type=page --post_title="Homepage Redesign Demo" \
  --post_status=draft --porcelain)
wp post meta update $PAGE_ID _wp_page_template elementor_canvas

# 2. Meta Elementor
wp post meta update $PAGE_ID _elementor_edit_mode builder
wp post meta update $PAGE_ID _elementor_template_type wp-page
wp post meta update $PAGE_ID _elementor_version "$(wp plugin get elementor --field=version)"

# 3. Stato iniziale vuoto + settings pagina
wp post meta update $PAGE_ID _elementor_data '[]'
wp post meta update $PAGE_ID _elementor_page_settings '{"hide_title":"yes"}' --format=json

# 3b. LOOP PER-SEZIONE (flusso standard di FASE 4): dopo aver aggiunto/modificato
#     una sezione in page-state.json, rigenera l'intero array e riscrivi il meta.
#     Il merge è locale e chirurgico: le sezioni già validate restano identiche.
python scripts/merge_state.py page-state.json > /tmp/homepage.json    # valida anche id e css_id
scp /tmp/homepage.json $HOST:/tmp/
ssh $HOST "cd $WP_PATH && wp post meta update $PAGE_ID _elementor_data \"\$(cat /tmp/homepage.json)\" && wp elementor flush-css"
# → verifica: curl -s $(wp post url $PAGE_ID) | grep -c 'sec-hero'   # la sezione è nel markup?
# → poi passa alla sezione successiva

# 3c. (Consigliato) Salva la sezione anche come blocco riutilizzabile in libreria
TPL_ID=$(wp post create --post_type=elementor_library --post_title="Cliente — Hero" --post_status=publish --porcelain)
wp post meta update $TPL_ID _elementor_edit_mode builder
wp post meta update $TPL_ID _elementor_template_type container
wp post meta update $TPL_ID _elementor_data "$(python -c "import json;print(json.dumps([json.load(open('sections/hero.json'))]))")"
wp term list elementor_library_type >/dev/null 2>&1 && wp post term set $TPL_ID elementor_library_type container

# 4. Media (per ogni asset)
wp media import /tmp/assets/hero.webp --title="Hero Homepage" --porcelain   # → restituisce attachment ID

# 5. Rigenera CSS e pubblica
wp elementor flush-css
wp post update $PAGE_ID --post_status=publish
wp post url $PAGE_ID
```

Nota ordine: i media vanno importati PRIMA di generare il JSON definitivo (servono ID e URL). Flusso corretto: crea pagina → importa media → genera JSON con gli ID reali → scrivi meta → flush → publish.

Global Colors nel Kit via `wp eval-file`:
```php
<?php // set_kit_colors.php — eseguire con: wp eval-file set_kit_colors.php
$kit_id = (int) get_option('elementor_active_kit');
$s = get_post_meta($kit_id, '_elementor_page_settings', true);
if (!is_array($s)) $s = [];
$s['system_colors'] = [
  ['_id'=>'primary','title'=>'Primary','color'=>'{{HEX_PRIMARIO}}'],
  ['_id'=>'secondary','title'=>'Secondary','color'=>'{{HEX_SECONDARIO}}'],
  ['_id'=>'text','title'=>'Text','color'=>'{{HEX_TESTO}}'],
  ['_id'=>'accent','title'=>'Accent','color'=>'{{HEX_ACCENT}}'],
];
$s['system_typography'] = [
  ['_id'=>'primary','title'=>'Primary','typography_typography'=>'custom','typography_font_family'=>'{{FONT_TITOLI}}','typography_font_weight'=>'700'],
  ['_id'=>'text','title'=>'Text','typography_typography'=>'custom','typography_font_family'=>'{{FONT_CORPO}}','typography_font_weight'=>'400'],
];
update_post_meta($kit_id, '_elementor_page_settings', $s);
\Elementor\Plugin::$instance->files_manager->clear_cache();
echo "Kit $kit_id aggiornato\n";
```

---

## Canale B0 — MCP server WordPress (es. Royal MCP o equivalente) — opzionale, utile senza SSH

Se sul sito è installato un plugin che espone un **MCP server** dedicato (es. `royal-mcp/v1`, o qualunque altro plugin WP-MCP con route per pagine/media/pubblicazione), configuralo in `.mcp.json` (vedi template nella root del plugin) invece che come "connettore" — in Claude Code e in Antigravity i server MCP si dichiarano a livello di progetto/plugin, non vanno abilitati da un menu come in Cowork. Due modi d'uso:

**1. Come MCP server dichiarato nel progetto (preferito quando disponibile):** aggiungi la entry in `.mcp.json` con l'URL dell'endpoint (es. `https://<sito>/wp-json/royal-mcp/v1/mcp`) e l'auth Bearer nella variabile d'ambiente indicata. Copertura tipica: pagine (create/update/status), post, media (upload), info sito, search.

**2. Come REST diretta (alternativa dagli script):** le stesse route rispondono via HTTP con header `X-Royal-MCP-API-Key: <chiave>` (o `Authorization: Bearer`), chiave generata dalle impostazioni del plugin in wp-admin — utile quando preferisci chiamarle da script Python/bash invece che via MCP.

**Cosa NON copre (verificare al pre-flight):** queste route di norma non sono Elementor-specifiche. Al pre-flight, testa se l'update pagina accetta un campo `meta` (scrittura `_elementor_data`): se sì, il canale MCP può fare TUTTO; se no, il layout passa dal mu-plugin (§B2) o dal Canale C.

**Divisione dei compiti standard (MCP WP ✓ + REST ✓):**
- MCP WordPress → crea pagina, upload media, publish finale, letture.
- `elementor/v1` nativi (§B1) → Global Colors/Fonts, template library, flush cache.
- mu-plugin (§B2) → push per-sezione di `_elementor_data`.

## Canale B — REST API: endpoint nativi Elementor + mu-plugin (default senza SSH)

**B1 — Endpoint nativi (preferiti dove disponibili).** Le versioni recenti di Elementor espongono REST ufficiali:

```bash
# Global Colors / Typography (sostituiscono /kit-tokens del mu-plugin)
curl -su "$WP_USER:$WP_APP_PASSWORD" -X POST "$WP_URL/wp-json/elementor/v1/globals/colors/primary" \
  -H "Content-Type: application/json" -d '{"value":"{{HEX_PRIMARIO}}","title":"Primary"}'

# Salva una sezione come template in libreria (sostituisce /elementor-library-block)
curl -su "$WP_USER:$WP_APP_PASSWORD" -X POST "$WP_URL/wp-json/elementor/v1/template-library/templates" \
  -H "Content-Type: application/json" -d '{"title":"Cliente — Hero","type":"container","content":{...}}'

# Kit attivo e flush CSS
curl -su "$WP_USER:$WP_APP_PASSWORD" "$WP_URL/wp-json/elementor/v1/kits"
curl -su "$WP_USER:$WP_APP_PASSWORD" -X DELETE "$WP_URL/wp-json/elementor/v1/cache"
```

Nota: i payload esatti possono variare tra versioni di Elementor — prima dell'uso fai un `GET` sull'endpoint (o su `/wp-json/` filtrando la route) per leggere lo schema `args` e adeguare il body. Se un endpoint nativo risponde 404/400, ripiega sull'equivalente del mu-plugin.

**B2 — mu-plugin (necessario per la pagina, se non usi SSH/WP-CLI).** La REST standard non permette di scrivere `_elementor_data` (meta protetto), e nessun endpoint nativo copre il push per-sezione sulla pagina. Soluzione: il mu-plugin `scripts/elementor-bridge.php`, da installare una volta in `wp-content/mu-plugins/` (via FTP/File Manager/SSH). Espone:

- `POST /wp-json/agenzia/v1/elementor-page` — crea la pagina (usarla per il setup iniziale con `elementor_data: []`, o per ripristini completi).
- `POST /wp-json/agenzia/v1/elementor-section` — **endpoint del loop di FASE 4**: aggiunge/sostituisce/rimuove UNA sezione identificata da `settings.css_id` (`mode: append|replace|remove`, `position` opzionale). Idempotente: ripushare la stessa sezione la sostituisce. Fa flush CSS a ogni chiamata.
- `POST /wp-json/agenzia/v1/elementor-library-block` — salva una sezione come blocco Container riutilizzabile nella libreria Elementor.
- `POST /wp-json/agenzia/v1/kit-tokens` — scrive Global Colors/Fonts nel Kit attivo.
- Autenticazione: Application Password standard (`Authorization: Basic base64(user:app_password)`), permesso richiesto `edit_pages` + capability admin per il kit.

Loop per-sezione tipo: `python scripts/push_section.py sections/hero.json --page-id $PAGE_ID --save-block "Cliente — Hero"` → verifica render → sezione successiva.

Upload media: REST standard `POST /wp-json/wp/v2/media` (binario + header `Content-Disposition: attachment; filename="hero.webp"`). Usare `scripts/optimize_and_upload.py`.

Push pagina: `scripts/push_page.py` (legge il JSON locale, chiama l'endpoint, stampa URL e page ID).

Test di connessione minimo:
```bash
curl -su "$WP_USER:$WP_APP_PASSWORD" "$WP_URL/wp-json/wp/v2/users/me" | head -c 300
```

---

## Canale C — Export template .json (zero access)

Quando non c'è alcun accesso: genera il file template (formato in `elementor-json.md` §8) e consegna istruzioni:
1. WP Admin → Modelli → Modelli salvati → Importa modelli → carica il `.json`.
2. Crea nuova pagina → Modifica con Elementor → icona cartella → I miei modelli → Inserisci.
3. Impostazioni pagina (ingranaggio) → Layout: Elementor Canvas, Nascondi titolo: Sì.

Limite: le immagini devono essere già raggiungibili via URL pubblico al momento dell'import (Elementor le sideloada), oppure vanno caricate a mano e ricollegate. Se possibile, consegna insieme al `.json` anche uno zip delle immagini ottimizzate.

---

## Come scegliere il canale al pre-flight (FASE 0-bis del SKILL.md)

1. **SSH disponibile?** → Canale A. È il default quando l'hosting lo supporta: nessuna dipendenza da endpoint custom, comandi diretti, output verificabile a ogni step.
2. **Nessun SSH ma un MCP server WordPress è configurato in `.mcp.json`?** → Canale B0 per pagine/media/publish, combinato con B1 (endpoint nativi Elementor) per Kit/template, e mu-plugin (B2) per `_elementor_data`.
3. **Nessun SSH, nessun MCP server, ma Application Password disponibile?** → Canale B puro (B1 + B2).
4. **Nessun accesso di alcun tipo?** → Canale C, dichiarando il limite (immagini da ricollegare a mano).

Dichiara sempre all'utente, in una riga, quale canale hai scelto e perché prima di iniziare la build.

---

## Troubleshooting rapido

| Sintomo | Causa probabile | Fix |
|---|---|---|
| Pagina pubblica senza stili | CSS non rigenerato | `wp elementor flush-css` o Elementor → Strumenti → Rigenera CSS |
| Editor: "The content area was not found" | template pagina non-Elementor o tema ostile | `_wp_page_template = elementor_canvas` |
| Pagina vuota dopo scrittura dati | JSON con escaping errato o non valido | validare il JSON, riscrivere via WP-CLI/mu-plugin (mai SQL diretto) |
| Immagini rotte in editing | URL esterni o `id` mancante | ricaricare in Media Library e referenziare `{url, id}` |
| 401 su REST | Application Password non attiva (spesso disabilitata su HTTP non-SSL o da plugin di sicurezza) | verificare HTTPS, whitelist in Wordfence/iThemes |
| SSH funziona ma `wp` non è nel PATH | WP-CLI non installato globalmente sull'hosting | prova `php wp-cli.phar` o ripiega su Canale B |
