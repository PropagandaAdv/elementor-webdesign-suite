---
name: homepage-elementor-redesign
description: "Motore di redesign homepage WORDPRESS-NATIVE: costruisce una homepage high-fidelity direttamente su WordPress + Elementor Pro, generando il layout come JSON Elementor (Flexbox Containers), con copy di conversione reali e asset visivi unici creati via MCP (se disponibili) con palette del brand, upload in Media Library e pubblicazione su staging. Il deliverable è la PAGINA ELEMENTOR MODIFICABILE, non un mockup. Usala quando l'utente vuole rifare, ricostruire o prototipare una homepage/landing su WordPress, menziona Elementor, page builder, WP, staging, demo per un cliente su WordPress, o vuole mostrare 'come lavoreremmo' con un redesign reale ed editabile. NON usarla per redesign in Figma o deploy su Vercel/Next.js (esistono skill dedicate)."
---

# Homepage Elementor Redesign Engine — WordPress-native, Dev-Ready, Client-Editable

Questa skill esegue un redesign homepage il cui **deliverable primario è una pagina Elementor pubblicata su WordPress**, completamente modificabile dal page builder. La fedeltà visiva si costruisce a livello di JSON Elementor (Flexbox Containers + design token globali), gli asset si generano via MCP con la palette del brand, e il risultato è una demo commerciale che dimostra al cliente qualità e metodo di lavoro.

**Ambiente di esecuzione:** questa versione della skill è pensata per Claude Code (CLI o integrato in un IDE come Antigravity), non per un sandbox cloud isolato. Questo significa accesso diretto a bash/SSH, filesystem locale del progetto e — quando configurati in `.mcp.json` — a MCP server dedicati. Sfruttalo: preferisci SSH+WP-CLI quando disponibile (vedi `references/wp-connection.md`), usa git per versionare `page-state.json` e gli asset del progetto, e lascia che l'hook di validazione automatica (vedi sotto) intercetti i JSON malformati prima ancora che tu tenti il push.

**Regola d'oro:** la pagina deve restare **editabile in Elementor senza errori**. Un layout bellissimo che Elementor non riesce ad aprire in editing è un fallimento. Ogni struttura generata deve rispettare rigorosamente lo schema JSON documentato in `references/elementor-json.md`.

**Regola d'argento:** non toccare MAI il sito di produzione del cliente. Si lavora sempre su staging/demo (sottodominio dell'agenzia, clone, ambiente locale esposto). Se l'utente fornisce credenziali di un sito che sembra di produzione, chiedi conferma esplicita prima di scrivere qualsiasi cosa.

**Regola di sicurezza per questo plugin (nuovo rispetto alla versione Cowork):** questo repository può finire su GitHub, anche pubblico. Non scrivere MAI credenziali reali (URL di staging riservati, utenti, password, Application Password, chiavi MCP) dentro `SKILL.md`, i file di `references/`, o qualunque file che finisca nel commit. Tutte le credenziali vivono in variabili d'ambiente o in un file `.env` locale elencato in `.gitignore` (vedi `.env.example` nella root del plugin). Se stai personalizzando questa skill per la tua agenzia con un ambiente di staging fisso, tienilo in `.env`/variabili d'ambiente della tua macchina, non nel testo della skill.

---

## FASE 0 — Allineamento iniziale (chiedi prima di partire)

Prima di generare qualsiasi cosa, conferma in una sola domanda i dati bloccanti che mancano:

1. **Ambiente WordPress target**: URL di staging, utente, metodo di accesso (SSH? Application Password? un MCP server WordPress già configurato in `.mcp.json`?). Se l'utente/agenzia lavora sempre sullo stesso staging, questi valori possono già essere in variabili d'ambiente (`WP_URL`, `WP_USER`, `WP_APP_PASSWORD`, `WP_SSH_HOST`) — controllale prima di chiedere.
2. **Elementor Pro**: attivo o Free? Se Free, usa le alternative in `references/widget-map.md`.
3. **Pagina di destinazione**: nome e URL/slug della pagina dedicata in cui costruire il design (bloccante — vedi regola "Pagina dedicata" più sotto). Lo stesso WordPress spesso ospita le demo di più clienti: costruisci sempre in una **pagina dedicata**, mai sulla home né su pagine esistenti. Se una pagina con quello slug esiste già, NON sovrascriverla in silenzio: chiedi se aggiornarla o creare una variante (`<slug>-v2`).
4. **Contenuti sorgente**: URL del sito attuale del cliente (per estrarre contenuti reali, brand, tono) + eventuali reference grafiche/benchmark. Se l'utente ha già lanciato prima `homepage-brief-builder`, il brief risultante copre già questo punto e i successivi — chiedi solo cosa manca.

Se l'utente ha già fornito tutto (anche incollando il brief di `homepage-brief-builder`), salta la domanda e procedi.

## FASE 0-bis — PRE-FLIGHT DI PUBBLICAZIONE (bloccante, PRIMA di generare qualsiasi cosa)

Il fallimento peggiore è costruire tutto e non riuscire a pubblicare. Quindi, prima di generare un solo asset o sezione, verifica i canali di scrittura e scegli quello giusto (vedi `references/wp-connection.md` §"Come scegliere il canale"):

1. **SSH + WP-CLI?** Prova `ssh $WP_SSH_HOST "wp core version"`. Se risponde → Canale A, il più solido: usalo.
2. **MCP server WordPress configurato?** (es. un plugin che espone route MCP per pagine/media/publish — vedi `.mcp.json` template). Se i suoi tool compaiono in sessione, verificali con una chiamata di lettura.
3. **Prova di scrittura reale**: crea SUBITO la pagina di destinazione in `draft` col canale scelto. Se la creazione riesce, la pubblicazione a fine lavoro riuscirà con lo stesso canale.
4. **REST diretta** (serve comunque per `_elementor_data` se non hai SSH): `curl -su "$WP_USER:$WP_APP_PASSWORD" "$WP_URL/wp-json/wp/v2/users/me"` — deve restituire l'utente, non 401.
5. **Test scrittura `_elementor_data`**: prova ad aggiornare la pagina draft scrivendo un meta di test — via WP-CLI (Canale A), via MCP se accetta i meta, altrimenti via mu-plugin `/agenzia/v1/elementor-section`. Registra quale funziona.

**Esiti e strategie:**
- SSH ✓ → Canale A per tutto: il caso più semplice e robusto.
- SSH ✗, MCP WP ✓, REST ✓ → pagine/media/publish via MCP, `_elementor_data` via mu-plugin o MCP se accetta i meta.
- SSH ✗, MCP WP ✗, REST ✓ → Canale B classico (mu-plugin).
- Tutti ✗ → Canale C (export `.json` da importare manualmente) — dichiaralo subito, MAI costruire 10 sezioni sperando che il push poi funzioni.

L'esito del pre-flight va dichiarato all'utente in una riga prima di iniziare la build.

---

## 1. PARAMETRI DI INPUT (Configurazione)

```
Ambiente WordPress:
  URL staging: [fornito dall'utente o da $WP_URL]
  Metodo accesso: [SSH+WP-CLI / MCP server WordPress / REST+Application Password+mu-plugin / export .json]
  Credenziali: [da variabili d'ambiente o richieste all'utente — MAI hardcoded nei file della skill]
  Elementor: [Pro o Free — dichiarato dall'utente]
  Pagina destinazione: [nome + URL/slug forniti dall'utente al lancio — bloccante]

Sito attuale (contenuti): [URL del sito da rifare]
Benchmark visivo/funzionale: [URL ispirazione/competitor + eventuali screenshot forniti]

Brand Identity & Design Token:
  Colori: Primario [HEX], Secondario [HEX], Sfondo [HEX], Testo/Dark [HEX], Accent [HEX]
  Tipografia: Font Titoli [Nome] — Font Corpo [Nome] — scala [es. H1 56/1.1, body 16/1.6]
  Spacing: [griglia 8px — 8,16,24,32,48,64,96,120]
  Radius/Shadow: [es. radius 12px card, shadow soft]

Direttive Immagini MCP:
  Connettore preferito: [quello configurato in .mcp.json / disponibile in sessione]
  Stile visivo: [es. fotografia editoriale tech / 3D isometrico / minimal flat]
  Mood: [es. clinico e luminoso / corporate premium / industriale pulito]
  Negative prompt: [es. stock fasullo, handshake, watermark, testo nelle immagini]

Business & copy:
  Business model & target persona: [es. B2B, buyer tecnico, ciclo lungo]
  OKR della pagina: [es. 1. Lead form, 2. Prenotazione call]
  Framework copywriting & lingua: [AIDA / PAS — Italiano, tono …]
```

Default e validazione campi vuoti: vedi sezione "Default & validazione" in fondo.

---

## 2. FASE 1 — Connessione a WordPress (scegli il canale)

Leggi `references/wp-connection.md` per i dettagli operativi completi. In sintesi, quattro canali in ordine di preferenza:

| Canale | Requisiti | Cosa permette | Quando |
|---|---|---|---|
| **A. SSH + WP-CLI** | Accesso SSH allo staging | Tutto: scrittura `_elementor_data`, flush CSS, creazione pagine, upload media | Default se disponibile — è il canale più robusto in un ambiente con bash reale |
| **B0. MCP server WordPress** | Plugin WP che espone route MCP, dichiarato in `.mcp.json` | Pagine, media, publish (copertura variabile) | Buona alternativa senza SSH |
| **B. REST API + mu-plugin** | Application Password + installazione una-tantum del mu-plugin `elementor-bridge.php` (in `scripts/`) | Creazione pagina, scrittura JSON Elementor, upload media, rigenerazione CSS via endpoint dedicato | Hosting senza SSH |
| **C. Export template .json** | Nessun accesso | Generi un file template Elementor che l'utente importa manualmente da Modelli → Importa | Fallback zero-access |

**Prima azione obbligatoria dopo la connessione:** verifica versione Elementor (`wp plugin get elementor --field=version` o endpoint `/wp-json/`), verifica che l'esperimento **Flexbox Container** sia attivo (default da Elementor 3.19+), e recupera l'ID del **Kit attivo** (Site Settings) per iniettare i Global Colors/Fonts.

**Design token globali prima di tutto:** scrivi la palette e la tipografia del brand nei **Global Colors/Global Fonts del Kit**. Via preferenziale: endpoint REST nativi `elementor/v1/globals/colors` e `/globals/typography` (vedi wp-connection.md §B1); fallback: meta `_elementor_page_settings` del post kit (`system_colors`/`custom_colors`) via WP-CLI o `/kit-tokens` del mu-plugin. Poi nel JSON della pagina referenzia i global (`__globals__`) invece di HEX hardcoded dove possibile: la demo diventa così un vero sistema, e dimostra metodo al cliente.

---

## 3. FASE 2 — Analisi e schema della homepage

**Prima della Section Map, consulta `references/design-inspiration.md`**: contiene il workflow di consultazione delle gallery di riferimento (Awwwards, SiteInspire, Lapa.ninja, bentogrids, footer.design, Typewolf, ecc.), una pattern library già distillata (bento grid, tipografia oversize, hero split, social proof quiet...) e le Laws of UX come filtro decisionale. Cerca il settore del cliente sulle gallery (WebSearch/WebFetch o browser), estrai 2-3 pattern distintivi coerenti col brand e **dichiarali nella Section Map** con la loro motivazione ("hero split asimmetrico + bento grid per lo showcase, ispirati ai benchmark di settore, filtrati con Hick's Law"). Ispirazione ≠ copia: si estraggono pattern strutturali, mai layout o palette altrui. Se il brief o il benchmark lo giustificano, valuta come gesto distintivo un **pattern scroll-motion** (sfondo continuo, parallasse, background video — vedi `references/scroll-motion.md`): va dichiarato nella Section Map con la sua regia (visual master, sezioni di richiamo, cosa si muove).

1. **Scraping del sito attuale**: estrai contenuti reali (chi sono, servizi, numeri, certificazioni, news). Niente Lorem Ipsum: la demo convince solo se parla del cliente.
2. **Analisi reference grafiche**: se l'utente ha fornito screenshot/URL benchmark, deducine layout pattern, densità, stile fotografico, e dichiarale come scelte motivate.
3. **Compila la Section Map**: prima di generare JSON, produci uno schema testuale sezione-per-sezione (nome, obiettivo, widget Elementor, copy draft, visual da generare) e — se in sessione interattiva — mostralo all'utente per conferma rapida. Questo è il "contratto" della pagina.

**Architettura standard (10 sezioni)** — adattala al settore, non applicarla ciecamente:

1. **Header/Navbar** — container sticky in-page: logo, menu, CTA primaria ad alto contrasto. (Per la demo NON usare Theme Builder: tutto in-page su template Elementor Canvas, così la pagina è autosufficiente e non tocca il tema.)
2. **Hero** — headline persuasiva ([Framework]) + sottotitolo + doppia CTA asimmetrica + visual principale MCP (background o media a destra).
3. **Trittico di segmentazione** — 3 card simmetriche per smistare i profili utente, micro-visual coordinati.
4. **Showcase prodotti/servizi** — griglia card uniformi, immagini dedicate MCP, tag e micro-copy.
5. **Istituzionale & riprova sociale** — presentazione + fascia numerica (widget Counter).
6. **Qualità/R&D/certificazioni** — loghi, standard, brevetti.
7. **Settori serviti** — griglia o carosello verticali.
8. **News & insights** — 3 card editoriali manuali (i post reali sullo staging spesso non esistono).
9. **Fascia CTA di chiusura** — full-width alto contrasto, form Elementor Pro o doppia CTA.
10. **Footer** — colonne in griglia, dati legali, social.

La mappatura sezione → widget Elementor precisa (Pro e alternative Free) è in `references/widget-map.md`.

---

## 4. FASE 3 — Asset visivi via MCP (niente placeholder, niente stock)

Per ogni sezione con visual, genera l'immagine col connettore/MCP disponibile (dichiarato in `.mcp.json` o abilitato in sessione) iniettando i token del brand:

> Prompt di controllo: `"Dominant color palette: [HEX Primario] and [HEX Secondario], over a clean [HEX Sfondo] background. Style: [Stile Visivo], Mood: [Mood]. Soft professional lighting, consistent color grading."` + negative prompt dai parametri.

- **Coerenza semantica per sezione**: Hero = value proposition macro; card = visual iconici/macro-dettaglio; showcase = close-up puliti.
- **Uniformità di stile** tra tutte le generazioni (stessa resa fotografica o stesso linguaggio illustrativo).
- **Video di serie, non solo immagini**: ogni demo include di norma **1-2 clip brevi** per rendere la home dinamica — la prima come background video dell'hero, l'eventuale seconda come accento in una sezione showcase (inline via widget `video`: `video_type: "hosted"`, `hosted_url` dalla Media Library, autoplay+mute+loop attivi, controls disattivati). Usa il connettore video disponibile in sessione (dichiara quale). Specifiche clip: loop seamless 5-10s, movimento lento e continuo (slow dolly/drift, niente tagli), muto, stessa iniezione palette/mood delle immagini; ri-encoda MP4 H.264 ≤5-6MB l'una (budget video totale pagina ≤10-12MB) e genera SEMPRE il frame poster WebP come fallback. Su mobile: mai autoplay del background video (fallback statico); l'inline nello showcase può restare se leggero. Se nessun connettore video è disponibile, la demo procede con sole immagini — dichiarandolo, senza bloccarsi.
- **Se la Section Map prevede un pattern scroll-motion** (vedi `references/scroll-motion.md`): genera PRIMA il **visual master** (immagine unica di sfondo — verticale se pattern "camera", ≤400KB WebP finale); la clip hero di cui sopra diventa parte della regia. Tutta la palette visiva delle altre generazioni discende dal master.
- **Pipeline media**: genera → scarica in locale → converti/ottimizza in **WebP** (dimensioni target: hero ~1920px, card ~800px, thumbnail ~600px; qualità 80-85; i video restano MP4) → carica su WordPress via `wp media import` o REST `/wp/v2/media` → **salva ID attachment + URL**: nel JSON Elementor ogni immagine va referenziata come `{"url": "...", "id": <attachment_id>}`, mai URL esterni (vale anche per i video di background: URL della Media Library, mai YouTube/Vimeo).
- Usa `scripts/optimize_and_upload.py` per il batch ottimizzazione+upload.

---

## 5. FASE 4 — Build iterativa SEZIONE-PER-SEZIONE (mai deploy monolitico)

**Principio fondante:** la homepage NON si genera e pubblica in un colpo solo. Si costruisce **una sezione alla volta**, come farebbe un designer nell'editor: container della sezione → widget al suo interno → push → verifica visiva → sezione successiva. Ogni sezione è un checkpoint. Se una sezione ha problemi, si corregge PRIMA di costruire la successiva.

Leggi **obbligatoriamente** `references/elementor-json.md` prima di generare la prima struttura.

**Validazione automatica (hook del plugin):** se hai installato questo plugin in Claude Code, un hook (`hooks/hooks.json`) intercetta ogni scrittura di file `sections/*.json` e lancia automaticamente `scripts/validate_json.py` prima che tu possa proseguire — non è più solo una buona pratica documentata, è imposta dall'ambiente. Se l'hook segnala errori, correggi prima di procedere al push.

### 5.1 Setup: pagina vuota + file di stato

1. Crea la pagina dedicata **con il titolo e lo slug indicati dall'utente** — già fatta nel pre-flight se il canale era disponibile; con Canale A (`wp post create`), Canale B0 (tool MCP pagine) o REST (`post_type=page`, `post_name=<slug fornito>`, `post_title=<nome fornito>`, status `draft`), template `elementor_canvas`, meta Elementor minimi (`_elementor_edit_mode=builder`, `_elementor_template_type=wp-page`, `_elementor_version`, `_elementor_page_settings={"hide_title":"yes"}`), `_elementor_data=[]`.
2. Crea in locale `page-state.json`: è la **fonte di verità** del layout, un oggetto ordinato `{slug_sezione: <container JSON>}` che rispecchia le sezioni della Section Map approvata (es. `menu`, `hero`, `chi-siamo`, `come-lavoriamo`, `clienti`, `lavori`, `contatti`, `footer`). Mettilo sotto git (repo del progetto cliente, non di questo plugin): è comodo poter fare `git diff` tra una versione di una sezione e la successiva durante le iterazioni di FASE 4.3.
3. Ogni container root di sezione DEVE avere `settings.css_id = "sec-<slug>"` (es. `sec-hero`): è la chiave che permette di identificare, sostituire o rimuovere la singola sezione sia via script sia a occhio nell'editor.

### 5.2 Loop per ogni sezione della Section Map (in ordine)

Per ciascuna sezione:

1. **Costruisci il container** della sezione: un Flexbox Container root (`elType: "container"`, `css_id: "sec-<slug>"`), impostato come ritieni necessario per il layout (direction, gap, padding, background, boxed/full) — vedi pattern in `references/widget-map.md`. **Parti dagli esempi golden** in `references/examples/` (hero.json, card-grid.json, bento.json, cta.json): sono strutture complete e validate — copiane il pattern (ID, responsive, `__globals__`, placeholder `{{...}}` da sostituire con contenuti reali) invece di costruire da zero dallo schema.
2. **Popola i widget** al suo interno (heading, text-editor, button, image, icon-box, form, ecc.), con copy reali e le immagini già caricate in Media Library (`{url, id}`).
3. **Valida PRIMA di spingere**: `python3 scripts/validate_json.py <sezione.json> --section` (l'hook lo fa comunque automaticamente al salvataggio del file, ma eseguilo anche a mano se vuoi validare senza scrivere su disco). Errori bloccanti (ID duplicati, widget vietati, elType legacy) → correggi e rivalida; warning (responsive mancante, contrasto < 4.5:1) → risolvi salvo motivata eccezione. Solo a validazione superata, aggiorna `page-state.json` e fai il **push della sola sezione**: Canale A → `scripts/merge_state.py` + `wp post meta update` (vedi wp-connection.md §A); Canale B/B0 → `scripts/push_section.py` (endpoint `/elementor-section`, mode `append`/`replace`). Tecnicamente il meta viene riscritto per intero (è l'unità atomica di Elementor), ma il merge è chirurgico: le sezioni già validate non vengono toccate.
4. **Flush CSS** e **ciclo di feedback visivo** (non un semplice check di esistenza) — questo passo è delegabile al subagent `elementor-section-qa` (vedi `agents/elementor-section-qa.md`): passagli lo slug della sezione e l'URL della pagina, e lascia che esegua l'intero ciclo screenshot→giudizio→fix in un contesto separato, riportandoti solo l'esito. Se preferisci farlo in linea:
   a. **Screenshot renderizzato** della sezione, desktop (1440px) E mobile (390px): usa lo strumento di automazione browser disponibile nell'ambiente (Antigravity ha un browser integrato; in Claude Code una MCP di browser automation come Playwright o chrome-devtools, oppure uno script Playwright standalone). Se nessuno strumento visivo è disponibile, ripiega sulla verifica markup (`#sec-<slug>` presente — via REST autenticata se il fetch pubblico è bloccato dal robots) e dichiara che la verifica visiva non è stata possibile.
   b. **Guarda lo screenshot e giudicalo** come un art director: spaziature coerenti con la griglia, testi che non spezzano male, gerarchia leggibile, contrasto reale sul background image, nessun overflow orizzontale su mobile. Se la sezione ha Motion Effects: screenshot a 2-3 posizioni di scroll diverse per verificare la gerarchia dei movimenti, e giudica lo screenshot mobile COME PAGINA STATICA (gli effetti su mobile sono esclusi per regola).
   c. Se qualcosa non va: **correggi il JSON → ri-valida → ri-push in mode `replace` → ri-screenshot**. Massimo 2 iterazioni di fix per sezione; il problema residuo si annota in `page-state.json` e si sistema in coda, non si resta bloccati.
5. **(Consigliato)** Salva la sezione anche come **template Container nella libreria** (`elementor_library`, tipo `container`) con titolo `[Cliente] — <Sezione>`: costruisce una libreria di blocchi riutilizzabili per l'agenzia. Via preferenziale: endpoint nativo `POST /elementor/v1/template-library/templates`; alternative: endpoint `/elementor-library-block` del mu-plugin o `wp post create --post_type=elementor_library`.
6. Solo a verifica superata, passa alla sezione successiva.

Regole non negoziabili durante il loop:
- **Solo Flexbox Container** (`elType: "container"`), mai section/column legacy.
- **ID univoci** di 7 caratteri alfanumerici minuscoli per ogni elemento.
- **Responsive esplicito** su ogni container: direzione/gap/padding anche `_tablet` e `_mobile`.
- **Contrasto WCAG ≥ 4.5:1** su testo/CTA (overlay sui background image).
- Copy reali secondo il [Framework], in [Lingua]. Niente Lorem Ipsum nemmeno "temporaneo".
- **Motion con giudizio** (se previsto dalla Section Map): solo settings nativi Elementor (Motion Effects/Sticky/background video), mai JS custom; effetti esclusi su mobile; max 2-3 elementi in movimento per viewport; testo da leggere mai in traslazione. Regole complete in `references/scroll-motion.md`.

### 5.3 Chiusura

1. Quando tutte le sezioni sono verificate: flush CSS finale, `post_status=publish`.
2. **Test di editabilità**: apri (o fai aprire all'utente) la pagina con `action=elementor` — l'editor deve caricare senza errori e ogni sezione deve apparire come container distinto, selezionabile e modificabile singolarmente.
3. Screenshot full-page finale desktop + mobile.
4. **Commit del progetto**: se `page-state.json`, gli script di override e i JSON di sezione vivono in un repo del cliente, fai un commit di chiusura — è la base per riprendere il lavoro (revisioni, nuova pagina, altro cliente con lo stesso starter).

**Canale C (fallback zero-access):** genera UN file template `.json` per OGNI sezione (formato template export, `"type": "container"`) più un file pagina completa. L'utente importa i blocchi da Modelli → Importa e li inserisce in pagina uno alla volta: anche il flusso manuale resta sezione-per-sezione. Genera il file `.json` in formato template Elementor (`{"content": [...], "page_settings": {...}, "version": "0.4", "title": "...", "type": "page"}`) e consegnalo con le istruzioni di import (Modelli → Modelli salvati → Importa). Le immagini in questo caso vanno prima caricate a mano o servite da URL raggiungibili.

---

## 6. FASE 5 — Presentazione al cliente

Lo scopo commerciale è dimostrare qualità e metodo. Chiudi sempre con:

1. **URL della demo** (+ eventuale link con protezione, es. pagina privata + link condivisibile).
2. **Screenshot desktop e mobile** full-page.
3. **Documento di metodo in Word** (1-2 pagine, italiano, formattazione professionale, tono caldo e benefit-first): cosa è stato analizzato del sito attuale, scelte di design motivate (pattern F/Z, gerarchia, palette con i riferimenti HEX, framework di copy usato e perché), struttura delle sezioni, e come proseguirebbe il progetto (pagine interne, SEO, performance). Genera il file `.docx` con la skill/tooling docx disponibile nell'ambiente: è l'artefatto che il commerciale allega alla mail con il link della demo e usa in call — trasforma la demo tecnica in un'arma commerciale.

---

## 7. Default & validazione input

Se un campo è vuoto non bloccarti: applica un default sensato e dichiaralo.
- **Colori/font mancanti** → estraili dal sito attuale (CSS/computed) o dal benchmark; altrimenti proponi palette di settore e chiedi conferma.
- **Spacing** → griglia 8px. **Radius** → 12px card, 8px bottoni.
- **Framework copy** → PAS per B2B problem-aware, AIDA per awareness. **Lingua** → italiano.
- **Negative prompt** → "foto stock finte, handshake, watermark, testo deformato, disordine".
- **Connettore immagini** → il primo disponibile tra quelli collegati; dichiara quale usi.
- **Ambiente WordPress mancante** → chiedilo in FASE 0 (non c'è più un default hardcoded in questa versione). Se manca solo la Application Password, chiedila; se l'utente non può fornirla, ripiega sul Canale C (template .json) che non richiede accessi.

---

## 8. Criteri di "Done" (checklist verificabile)

- [ ] Le sezioni della Section Map approvata sono tutte presenti, in Flexbox Container, responsive (desktop/tablet/mobile) e senza placeholder.
- [ ] Ogni sezione ha superato `scripts/validate_json.py` prima del push (zero errori bloccanti).
- [ ] Ogni sezione ha completato il ciclo di feedback visivo (screenshot desktop + mobile giudicato e corretto, anche tramite il subagent `elementor-section-qa`) o, in assenza di strumenti visivi, la cosa è stata dichiarata.
- [ ] Global Colors/Fonts del brand scritti nel Kit e referenziati dal layout.
- [ ] Ogni visual generato via MCP con iniezione palette, ottimizzato WebP, caricato in Media Library e referenziato con attachment ID.
- [ ] Copy reali (no Lorem Ipsum), contrasti ≥ 4.5:1 verificati.
- [ ] CSS Elementor rigenerato; pagina pubblicata; **URL demo fornito**.
- [ ] La pagina si apre in editing Elementor senza errori.
- [ ] Screenshot desktop + mobile e documento di metodo in Word consegnati.
- [ ] Nessuna credenziale reale è finita in un file tracciato da git (controlla `git diff`/`git status` prima di ogni commit).

**Miglioramento continuo:** a fine progetto, se una sezione è venuta particolarmente bene, salvane il JSON (anonimizzato con placeholder `{{...}}`) in `references/examples/` come nuovo esempio golden: la skill migliora a ogni lavoro. Dopo ogni modifica alla skill, rilancia gli eval di regressione in `evals/evals.json` per verificare che triggering e flusso non si siano rotti.

---

## File di riferimento

- `references/elementor-json.md` — Anatomia di `_elementor_data`, Flexbox Container, settings responsive, global, esempi completi di widget. **Leggilo sempre prima di generare JSON.**
- `references/widget-map.md` — Mappatura sezione → widget (Pro + alternative Free) con i settings chiave di ognuno.
- `references/wp-connection.md` — Setup dei quattro canali di accesso, comandi WP-CLI, endpoint REST, sicurezza.
- `references/scroll-motion.md` — **Scroll motion**: sfondo continuo (fixed), Motion Effects (chiavi JSON translateY/opacity/blur, sticky), background video con generazione clip via connettori MCP, pattern di regia e guardrail performance/accessibilità. **Da leggere se la Section Map prevede un pattern scroll-motion.**
- `references/design-inspiration.md` — **Fonti di ispirazione e pattern**: catalogo gallery (Awwwards, SiteInspire, Lapa, bentogrids, footer.design, Typewolf...), workflow di consultazione, pattern library distillata e Laws of UX applicate. **Da leggere in FASE 2 prima della Section Map.**
- `references/examples/` — **Esempi golden**: hero.json, card-grid.json, bento.json (griglia bento showcase), cta.json. Strutture complete, responsive e validate con placeholder `{{...}}`: la base few-shot per ogni nuova sezione. Si arricchisce a ogni progetto riuscito.
- `scripts/validate_json.py` — **Validatore pre-push**: ID univoci, widget vietati/whitelist, elType legacy, responsive mancante, contrasto WCAG, hex hardcoded. Lanciato anche in automatico dall'hook del plugin (vedi `hooks/hooks.json`).
- `evals/evals.json` — Eval di regressione (flusso tipico, non-trigger Figma, ambiente esterno Free, Canale C zero-access). Da rilanciare dopo ogni modifica alla skill.
- `scripts/elementor-bridge.php` — mu-plugin per il Canale B: endpoint pagina intera, endpoint **sezione singola** (append/replace/remove per `css_id`), endpoint salvataggio blocco in libreria, flush CSS.
- `scripts/push_section.py` — push incrementale di UNA sezione via REST (Canale B). È lo script del loop di FASE 4.
- `scripts/merge_state.py` — fonde `page-state.json` (sezioni nominate) nell'array `_elementor_data`; usato col Canale A (WP-CLI) per il push per-sezione.
- `scripts/push_page.py` — push della pagina completa (solo per ripristini/riallineamenti, NON è il flusso standard).
- `scripts/optimize_and_upload.py` — batch: ottimizza immagini in WebP e le carica in Media Library, restituisce mappa file→(id,url).

## Vedi anche (altre skill di questo plugin)

- `homepage-brief-builder` — da lanciare PRIMA di questa, quando hai le risposte grezze di un questionario/intervista cliente e vuoi un brief già nel formato che questa skill si aspetta in FASE 0.
- `website-qa-review` — da lanciare DOPO questa, come ultimo controllo indipendente nel browser reale prima di consegnare la demo o andare live.
