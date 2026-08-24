# Anatomia del JSON Elementor (`_elementor_data`)

Elementor salva l'intero layout di una pagina nel post meta `_elementor_data` come **stringa JSON** (array di elementi root). Questo file definisce le regole per generare JSON valido, editabile e responsive.

## Indice
1. Struttura base degli elementi
2. Flexbox Container: settings essenziali
3. Responsive: suffissi `_tablet` / `_mobile`
4. Global Colors & Fonts (`__globals__`)
5. Immagini e media
6. Esempi widget completi (heading, text, button, image, icon-box, counter, form)
7. Struttura Hero completa (esempio end-to-end)
8. Meta della pagina e formato template export
9. Errori tipici da evitare

---

## 1. Struttura base

Ogni elemento è un oggetto con questa forma:

```json
{
  "id": "a1b2c3d",
  "elType": "container",
  "settings": { },
  "elements": [ ],
  "isInner": false
}
```

- `id`: **7 caratteri** alfanumerici minuscoli (`[0-9a-f]` va benissimo), univoco nella pagina. Generane uno random per ogni elemento.
- `elType`: `"container"` per i contenitori, `"widget"` per i widget.
- I widget hanno in più `"widgetType": "heading" | "text-editor" | "button" | ...` e `elements` sempre `[]`.
- I container annidati dentro altri container hanno `"isInner": true`.
- La radice di `_elementor_data` è un **array** di container top-level (le "sezioni" della pagina).

## 2. Flexbox Container — settings essenziali

Container top-level (full-width con contenuto boxed):

```json
{
  "id": "hero001",
  "elType": "container",
  "isInner": false,
  "settings": {
    "content_width": "boxed",
    "boxed_width": {"unit": "px", "size": 1200},
    "flex_direction": "row",
    "flex_gap": {"unit": "px", "size": 48, "column": "48", "row": "48"},
    "flex_align_items": "center",
    "flex_justify_content": "space-between",
    "padding": {"unit": "px", "top": "120", "right": "24", "bottom": "120", "left": "24", "isLinked": false},
    "background_background": "classic",
    "background_color": "#0E2A3A"
  },
  "elements": [ ]
}
```

Chiavi ricorrenti:
- `content_width`: `"boxed"` o `"full"`.
- `flex_direction`: `"row"` / `"column"` (+ varianti reverse).
- `flex_wrap`: `"wrap"` per griglie di card fatte a container.
- Dimensionamento colonne interne: sul container figlio usa `"width": {"unit": "%", "size": 50}` oppure `flex_grow`/`flex_shrink`.
- Background: `background_background: "classic"` + `background_color` o `background_image: {"url": "...", "id": 123}`; overlay con `background_overlay_background`, `background_overlay_color`, `background_overlay_opacity: {"unit":"px","size":0.55}`.
- Bordi/ombre: `border_radius: {"unit":"px","top":"12","right":"12","bottom":"12","left":"12","isLinked":true}`, `box_shadow_box_shadow_type: "yes"`, `box_shadow_box_shadow: {"horizontal":0,"vertical":12,"blur":40,"spread":0,"color":"rgba(14,42,58,0.12)"}`.

## 3. Responsive

Elementor è desktop-first: la chiave "nuda" è desktop, i breakpoint si sovrascrivono con suffissi:

```json
"flex_direction": "row",
"flex_direction_tablet": "column",
"flex_direction_mobile": "column",
"padding": {"unit":"px","top":"120","right":"24","bottom":"120","left":"24","isLinked":false},
"padding_mobile": {"unit":"px","top":"64","right":"16","bottom":"64","left":"16","isLinked":false}
```

**Regola:** ogni container top-level DEVE avere almeno `flex_direction_mobile`, `padding_mobile` e (se griglia) larghezze mobile al 100%. Tipografia: `typography_font_size_mobile` sui heading grandi.

## 4. Global Colors & Fonts

I global del Kit si referenziano nel widget tramite `__globals__` dentro `settings`:

```json
"settings": {
  "title": "Titolo",
  "__globals__": {
    "title_color": "globals/colors?id=primary",
    "typography_typography": "globals/typography?id=primary"
  }
}
```

ID di sistema del Kit: `primary`, `secondary`, `text`, `accent` (colori) e `primary`, `secondary`, `text`, `accent` (typography). Colori custom aggiunti al Kit hanno ID generati — leggili dal meta `_elementor_page_settings` del post kit (`custom_colors: [{"_id":"abc1234","title":"Bordeaux","color":"#7A1F2B"}]`) e referenziali come `globals/colors?id=abc1234`.

Scrivere i global nel Kit (WP-CLI):
```bash
KIT_ID=$(wp option get elementor_active_kit)
wp post meta get $KIT_ID _elementor_page_settings   # leggi, modifica il PHP-serialized/JSON con cautela
```
Il meta del kit è un array PHP serializzato: preferisci modificarlo via `wp eval-file` con uno script PHP che usa `get_post_meta`/`update_post_meta` (vedi wp-connection.md) piuttosto che manipolare la serializzazione a mano.

## 5. Immagini e media

Ogni immagine va referenziata con **URL + attachment ID del media caricato sullo stesso WordPress**:

```json
"image": {"url": "https://demo.sito.it/wp-content/uploads/2026/07/hero.webp", "id": 512}
```

Mai URL esterni (rompono srcset, ottimizzazione e portabilità). Per i background: `background_image: {"url": "...", "id": 512}` + `background_size: "cover"`, `background_position: "center center"`.

## 6. Esempi widget

**Heading**
```json
{"id":"aa11b22","elType":"widget","widgetType":"heading","elements":[],
 "settings":{
   "title":"Tecnologia medicale che semplifica il tuo lavoro",
   "header_size":"h1",
   "title_color":"#FFFFFF",
   "typography_typography":"custom",
   "typography_font_family":"Barlow","typography_font_weight":"700",
   "typography_font_size":{"unit":"px","size":56},
   "typography_font_size_mobile":{"unit":"px","size":34},
   "typography_line_height":{"unit":"em","size":1.1}
 }}
```

**Text editor** (accetta HTML)
```json
{"id":"bb22c33","elType":"widget","widgetType":"text-editor","elements":[],
 "settings":{"editor":"<p>Sottotitolo con la value proposition in una frase chiara.</p>",
   "text_color":"#D8DEE4",
   "typography_typography":"custom","typography_font_size":{"unit":"px","size":18},
   "typography_line_height":{"unit":"em","size":1.6}}}
```

**Button**
```json
{"id":"cc33d44","elType":"widget","widgetType":"button","elements":[],
 "settings":{"text":"Richiedi una demo","link":{"url":"#contatti","is_external":"","nofollow":""},
   "background_color":"#7A1F2B","button_text_color":"#FFFFFF",
   "border_radius":{"unit":"px","top":"8","right":"8","bottom":"8","left":"8","isLinked":true},
   "typography_typography":"custom","typography_font_weight":"600",
   "text_padding":{"unit":"px","top":"16","right":"32","bottom":"16","left":"32","isLinked":false}}}
```
Variante secondaria outline: `background_color: "rgba(0,0,0,0)"` + `border_border: "solid"`, `border_width`, `border_color`, `button_text_color` = colore chiaro.

**Image**
```json
{"id":"dd44e55","elType":"widget","widgetType":"image","elements":[],
 "settings":{"image":{"url":"https://.../card-01.webp","id":513},"image_size":"full",
   "width":{"unit":"%","size":100},
   "image_border_radius":{"unit":"px","top":"12","right":"12","bottom":"12","left":"12","isLinked":true}}}
```

**Icon Box** (card trittico)
```json
{"id":"ee55f66","elType":"widget","widgetType":"icon-box","elements":[],
 "settings":{"selected_icon":{"value":"fas fa-microscope","library":"fa-solid"},
   "title_text":"Per i laboratori","description_text":"Strumentazione e supporto dedicati.",
   "position":"top","title_size":"h3","primary_color":"#7A1F2B"}}
```

**Counter** (fascia numeri)
```json
{"id":"ff66a77","elType":"widget","widgetType":"counter","elements":[],
 "settings":{"starting_number":0,"ending_number":250,"suffix":"+","title":"Clienti attivi",
   "number_color":"#7A1F2B","title_color":"#31383F"}}
```

**Form (Elementor Pro)** — minimo funzionante
```json
{"id":"1177b88","elType":"widget","widgetType":"form","elements":[],
 "settings":{"form_name":"Lead Homepage",
   "form_fields":[
     {"_id":"f1a2b3c","custom_id":"name","field_type":"text","field_label":"Nome","required":"true","width":"50"},
     {"_id":"f2b3c4d","custom_id":"email","field_type":"email","field_label":"Email","required":"true","width":"50"},
     {"_id":"f3c4d5e","custom_id":"message","field_type":"textarea","field_label":"Messaggio","width":"100"}],
   "button_text":"Invia richiesta","submit_actions":["email"],
   "email_to":"admin@site.it","email_subject":"Nuovo lead dalla homepage demo"}}
```

Altri widget utili: `nav-menu` (Pro), `image-carousel`, `testimonial`, `social-icons`, `icon-list`, `divider`, `spacer`, `video`, `google_maps`, `call-to-action` (Pro). Mappatura completa in `widget-map.md`.

## 7. Hero end-to-end (pattern di riferimento)

Container root (background image + overlay) → container inner sinistro (column, 55%: heading + text + container row con 2 button) → container inner destro (45%: image o vuoto se il visual è il background). Su mobile: direction column, testo prima, padding ridotti, heading 34px.

## 8. Meta della pagina e formato template

Meta minimi per una pagina Elementor valida:

| Meta | Valore |
|---|---|
| `_elementor_edit_mode` | `builder` |
| `_elementor_template_type` | `wp-page` |
| `_elementor_version` | versione Elementor installata (es. `3.30.1`) |
| `_elementor_data` | JSON **slashed** (usare `wp_slash(wp_json_encode(...))` lato PHP; con WP-CLI `wp post meta update <ID> _elementor_data "$(cat page.json)"` gestisce l'escaping) |
| `_elementor_page_settings` | array (es. `{"hide_title":"yes"}`) |
| `_wp_page_template` | `elementor_canvas` (demo autosufficiente) o `elementor_header_footer` |

Dopo ogni scrittura di `_elementor_data`: **rigenera il CSS** (`wp elementor flush-css`, oppure cancella il meta `_elementor_css` della pagina e svuota `wp-content/uploads/elementor/css/post-<ID>.css`).

Formato file **template export** (Canale C):
```json
{"content":[ ...array elementi root... ],"page_settings":{"hide_title":"yes"},"version":"0.4","title":"Homepage Redesign — Cliente","type":"page"}
```

## 9. Errori tipici da evitare

1. **JSON non slashed** scritto via SQL/REST diretto → Elementor mostra pagina vuota. Usare sempre i canali documentati.
2. **ID duplicati o mancanti** → l'editor non apre o duplica elementi.
3. **Section/column legacy mischiate a container** → layout imprevedibile. Solo container.
4. **URL immagine esterni o senza `id`** → niente srcset, immagini che spariscono all'edit.
5. **Dimenticare flush CSS** → la pagina pubblica appare senza stili.
6. **Settings inventati**: se non sei certo di una chiave, usa il sottoinsieme documentato qui; è sufficiente per il 95% dei layout. In caso di dubbio, crea manualmente il widget su una pagina di test, leggi il suo `_elementor_data` e copia le chiavi reali.
7. **`hide_title` mancante** → il tema stampa il titolo pagina sopra l'hero.
