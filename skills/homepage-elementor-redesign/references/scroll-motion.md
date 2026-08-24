# Scroll Motion — sfondo continuo, parallasse e video: la pagina come racconto unico

Tecnica per demo ad alto impatto: la homepage percepita come **un unico visual di fondo**
(immagine o video) su cui, allo scorrimento, **si muovono solo alcune parti** (testi,
card, layer grafici) tramite i Motion Effects di Elementor Pro. Da usare come *gesto
distintivo* della demo (vedi design-inspiration.md: 2-3 gesti, non dieci) — non su ogni
sezione.

**Prerequisito:** Elementor Pro attivo (Motion Effects e Sticky sono Pro). Sull'ambiente
predefinito è già così.

---

## 1. I tre ingredienti tecnici

### A. Sfondo "continuo" — background fixed
L'illusione del sito appoggiato su un'immagine unica si ottiene dando alle sezioni chiave
lo **stesso background image con attachment fixed**: lo sfondo resta fermo mentre il
contenuto ci scorre sopra, e sezioni diverse "rivelano" porzioni diverse della stessa
immagine.

```json
"background_background": "classic",
"background_image": {"url": "{{MEDIA_URL_MASTER}}", "id": "{{MEDIA_ID_MASTER}}"},
"background_position": "center center",
"background_attachment": "fixed",
"background_size": "cover"
```

Varianti di regia:
- **Stessa immagine su 2-3 sezioni non consecutive** (es. hero, fascia numeri, CTA):
  le sezioni intermedie a background pieno chiaro fanno da "sipario" e il ritorno del
  visual crea continuità narrativa.
- **Posizioni diverse della stessa immagine master** (top/center/bottom) su sezioni
  successive: effetto "camera che scende" lungo un unico visual verticale. In questo
  caso genera via MCP un'immagine master VERTICALE (es. 1920×3800) pensata a fasce.

⚠️ **Limite iOS:** `background_attachment: fixed` non funziona su iOS/molti mobile.
Obbligatorio quindi: su mobile lo sfondo torna `scroll` (Elementor lo gestisce da solo
nella maggior parte dei casi, ma verifica nello screenshot mobile del ciclo visivo) e
l'immagine deve funzionare anche da ferma.

### B. Motion Effects (scrolling) — le "parti che si muovono"
I Motion Effects si applicano nei `settings` di widget e container. Chiavi principali
(Elementor Pro; verifica sempre in editor alla prima sezione, i nomi possono variare
leggermente tra versioni):

```json
"motion_fx_motion_fx_scrolling": "yes",
"motion_fx_translateY_effect": "yes",
"motion_fx_translateY_direction": "negative",
"motion_fx_translateY_speed": {"unit": "px", "size": 3},
"motion_fx_translateY_affectedRange": {"unit": "%", "size": "", "sizes": {"start": 0, "end": 100}},
"motion_fx_devices": ["desktop", "tablet"]
```

Effetti disponibili (stesso pattern di chiavi): `translateY` (parallasse verticale),
`translateX`, `opacity` (fade legato allo scroll), `blur`, `rotateZ`, `scale`.
Per il **background** di un container esistono le varianti `background_motion_fx_*`
(parallasse dello sfondo stesso, alternativa "morbida" al fixed).

**Regia del movimento — poche regole ferree:**
- Velocità diverse = profondità: sfondo fermo (o speed 1), visual secondari speed 2-4,
  testo fermo o quasi. Mai tutto alla stessa velocità.
- Si muovono i **layer decorativi e i visual**, NON i testi da leggere (un H1 che scappa
  mentre lo leggi è un danno, non un effetto).
- `motion_fx_devices`: SEMPRE escludere mobile dagli effetti di traslazione/blur.
  Su mobile la pagina deve essere perfetta da ferma.
- Max 2-3 elementi in motion per viewport (Von Restorff: se tutto si muove, niente
  colpisce).

### C. Sticky — elementi che "aspettano"
`"sticky": "top"` (+ `sticky_on: ["desktop","tablet"]`, `sticky_offset`,
`sticky_effects_offset`) su un elemento lo tiene fermo mentre la sezione scorre:
perfetto per un claim o un visual che resta in scena mentre le card gli sfilano accanto.
Combinato con `motion_fx_opacity` sull'header sticky si ottiene la navbar che si
compatta/appare dopo l'hero.

## 2. Pattern pronti (scegline UNO come gesto principale)

1. **"Unico sfondo" (il richiesto):** immagine/video master fixed su hero + 1-2 sezioni
   di richiamo; sezioni intermedie su background pieno; sui richiami, titoli e card
   entrano con `translateY` lento + `opacity`. Percezione: il sito vive sopra un unico
   visual.
2. **Camera verticale:** master verticale generato via MCP, sezioni successive con
   background position a scendere (top → center → bottom). Racconto "dall'alto verso
   il dettaglio" (ottimo per prodotti fisici, impianti, territorio).
3. **Layer parallasse nell'hero:** 2-3 immagini PNG con trasparenza (soggetto scontornato
   via Magnific remove-background) sovrapposte con `position: absolute` e speed diverse:
   profondità cinematografica senza video.
4. **Video hero + eco finale:** background video nell'hero, la stessa clip (o un suo
   frame) ritorna come sfondo della CTA finale. Peak-End Rule applicata al visual.
5. **Sticky showcase:** visual sticky a sinistra, card dei servizi che scorrono a destra.

## 3. Background VIDEO — generazione via connettori e settaggi

```json
"background_background": "video",
"background_video_link": "{{URL_MP4_MEDIA_LIBRARY}}",
"background_video_start": 0,
"background_video_fallback": {"url": "{{MEDIA_URL_POSTER}}", "id": "{{MEDIA_ID_POSTER}}"},
"background_play_on_mobile": ""
```

(campo `background_play_once` per non loopare; lasciare `background_play_on_mobile`
VUOTO: su mobile va il fallback statico — batteria, dati e autoplay policy.)

**Generazione della clip — connettore primario: Kling** (configurato sull'account;
fallback Higgsfield o Magnific video — dichiara quale usi, come per le immagini):
- Prompt con la stessa iniezione di brand delle immagini: HEX palette, mood, soggetto
  di settore; chiedere movimento LENTO e continuo (slow dolly/drift, niente tagli).
- **Loop seamless**: 5-10 secondi, primo e ultimo frame coerenti (chiedi "seamless loop"
  al modello; se non supportato, scegli clip a deriva costante dove lo stacco non si nota).
- **Muto sempre.** Niente audio nei background video.
- Formato: MP4 H.264, 1920×1080 max, target **≤ 5-6 MB** (ri-encoda se serve:
  `ffmpeg -i in.mp4 -an -vcodec libx264 -crf 28 -preset slow out.mp4`).
- Upload in **Media Library** via REST (`wp/v2/media`, come le immagini) e uso dell'URL
  interno — NON link YouTube/Vimeo per le demo (cookie, consenso, latenza).
- Genera SEMPRE anche il **poster/fallback**: un frame della clip (o l'immagine master
  equivalente) ottimizzato WebP.

## 4. Guardrail non negoziabili

- **Mobile-first della quiete:** tutti gli effetti di movimento esclusi su mobile
  (`motion_fx_devices`, `background_play_on_mobile` vuoto, fixed→scroll). Lo screenshot
  mobile del ciclo visivo (FASE 4) va giudicato COME PAGINA STATICA e deve reggere.
- **prefers-reduced-motion:** aggiungi al `custom_css` di pagina (dichiarandolo):
  ```css
  @media (prefers-reduced-motion: reduce) {
    .elementor-motion-effects-element, .elementor-motion-effects-layer { transform: none !important; }
  }
  ```
- **Leggibilità sopra tutto:** testo su sfondo continuo/video SEMPRE con overlay
  (`background_overlay_color` + opacity 0.45-0.65) o su pannello pieno. Il validatore
  non vede il contrasto su immagine: è compito del ciclo visivo giudicarlo.
- **Budget performance:** max 2 clip brevi per pagina (background hero + un accento
  inline), peso video totale ≤ 10-12MB, immagine master ≤ 400KB WebP,
  effetti su max 6-8 elementi totali. La demo deve caricare in < 3s anche su staging.
- **Editabilità (Regola d'oro):** tutto via settings Elementor nativi — MAI JS custom
  per lo scroll. Se un effetto richiede codice, non è il pattern giusto per la demo.
- **Verifica in editor alla prima sezione motion:** apri con `action=elementor` e
  conferma che gli effetti siano visibili/modificabili nel pannello Advanced → Motion
  Effects. Se le chiavi non risultano (versione diversa), imposta l'effetto UNA volta a
  mano in editor, esporta il JSON della sezione e usa quelle chiavi come riferimento
  per le successive.

## 5. Integrazione nel flusso

- **FASE 2:** se scegli un pattern scroll-motion, è il gesto distintivo n.1 della
  Section Map: dichiaralo con la regia (quale master, quali sezioni lo richiamano, cosa
  si muove).
- **FASE 3:** genera il visual master (e/o la clip) PRIMA delle altre immagini: tutta la
  palette visiva discende da lì. Poster e master vanno in Media Library con gli altri asset.
- **FASE 4:** le sezioni con motion seguono il normale loop (validate → push → screenshot),
  ma il giudizio visivo include un check aggiuntivo: scroll simulato (screenshot a 2-3
  posizioni di scroll diverse, o registrazione se lo strumento lo consente) per
  verificare che i layer si muovano con la gerarchia prevista.
- **FASE 5:** nel documento di metodo, la regia dello scroll va raccontata (è il punto
  che in call fa dire "wow, si può fare con Elementor?" — sì, ed è editabile).
