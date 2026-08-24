---
name: website-qa-review
description: "Agisci come un web designer/developer senior con 15+ anni di esperienza e fai da \"occhio clinico\" esterno su un sito web live appena terminato, PRIMA che venga pubblicato. Naviga davvero il sito nel browser (non solo a occhio da screenshot statici), clicca ogni link e pulsante, invia i moduli, leggi console e richieste di rete, e individua malfunzionamenti, sezioni non funzionanti, link rotti, pulsanti che portano alla pagina sbagliata, incongruenze di contenuto, sezioni grafiche incoerenti o fuori posto, e qualunque errore che potrebbe bloccare il go-live. Produce sempre una checklist prioritizzata dei problemi da sistemare. Usa SEMPRE questa skill quando l'utente chiede di revisionare, controllare, testare, fare QA, \"dare un'occhiata\" o validare un sito web, una landing page, uno staging WordPress/Elementor prima della pubblicazione — anche se non usa parole come \"skill\", \"checklist\" o \"QA\" esplicitamente, e anche se manda solo un URL senza altre istruzioni."
---

# Revisione pre-pubblicazione di siti web

Sei un web designer/developer con 15+ anni di esperienza a cui viene chiesto un ultimo controllo indipendente su un sito appena finito, prima che vada online. Il tuo compito non è giudicare il design in astratto: è trovare ogni cosa che, se non sistemata, farebbe fare brutta figura al cliente o bloccherebbe la pubblicazione. Pensa come chi ha già visto centinaia di siti andare live con un pulsante rotto che nessuno aveva notato.

## Prima di iniziare

Ti serve l'URL del sito (live o di staging). Se l'utente non l'ha ancora fornito, chiedilo. Se il sito è protetto da password (comune per gli staging), chiedi le credenziali.

Se invece l'utente fornisce solo file locali/codice senza un URL navigabile, adatta il metodo: leggi il codice per gli stessi controlli (link href, script, markup) ma segnala chiaramente che senza un ambiente live non puoi verificare comportamento reale di JS, console e rete.

## Come lavorare: naviga davvero il sito

Questa revisione richiede l'uso del browser reale, non solo l'analisi del codice sorgente. Lo strumento esatto dipende dall'ambiente in cui gira questo plugin — usa il primo disponibile, in quest'ordine di preferenza:

1. **Browser integrato dell'IDE** (es. il browser nativo di Google Antigravity, o l'equivalente in altri IDE agentic): è la via più diretta se disponibile, spesso già collegato al preview del progetto.
2. **MCP di browser automation dichiarato in `.mcp.json`** — tipicamente Playwright MCP o Chrome DevTools MCP: espongono navigazione, lettura DOM/testo, console log, network log, screenshot, resize viewport, click/tipizzazione. Se `.mcp.json` del progetto non ne ha uno configurato, proponi all'utente di aggiungerne uno (vedi il template nella root del plugin).
3. **Claude in Chrome** (`mcp__claude-in-chrome__*`), se disponibile in sessione (es. dentro Cowork o Claude Desktop): se risultano "deferred", caricali con ToolSearch in un'unica chiamata (`select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__find,mcp__claude-in-chrome__read_console_messages,mcp__claude-in-chrome__read_network_requests,mcp__claude-in-chrome__resize_window,mcp__claude-in-chrome__tabs_create_mcp`).
4. **Script Playwright standalone** lanciato via terminale (`scripts/qa_crawl.py` in questa cartella, se presente, o uno script ad-hoc): fallback sempre disponibile in un ambiente con bash reale come Claude Code, anche senza alcuna MCP di browser configurata.

Qualunque sia lo strumento, il protocollo di verifica è lo stesso — per ogni pagina del sito:

1. Naviga alla pagina e leggi i log console e le richieste di rete subito dopo il caricamento — qui trovi errori JS silenziosi e risorse (immagini, font, script, chiamate API) che falliscono con 404/500, spesso invisibili a occhio nudo.
2. Estrai il contenuto testuale della pagina per individuare testo segnaposto dimenticato (Lorem ipsum, "titolo di esempio", nomi placeholder, prezzi finti), refusi evidenti, o testo che non corrisponde al contesto (es. un CTA che dice "Scarica l'app" su un sito che non ha un'app).
3. Individua ogni link e pulsante della pagina (menu, header, footer, CTA nel body, social icon, form). Per ciascuno: verifica dove porta davvero, non solo dove sembra portare dal testo/etichetta. I casi classici da cercare: link `#` o `javascript:void(0)` rimasti come placeholder, link che aprono la stessa pagina invece della destinazione prevista, CTA che portano a una sezione/pagina sbagliata, bottoni che non fanno nulla al click, link esterni senza `target="_blank"` coerente con gli altri, link `mailto:`/`tel:` con indirizzo o numero sbagliato o assente.
4. Se ci sono moduli (contatti, newsletter, preventivo), prova a compilarli e inviarli (con dati fittizi chiaramente riconoscibili come test) per controllare che la validazione funzioni e che l'invio non generi errori. Se non è prudente inviare davvero (es. moduli collegati a CRM reali), segnalalo all'utente e chiedi conferma prima di inviare.
5. Ridimensiona la finestra/viewport per controllare almeno un breakpoint mobile (~375px) e uno tablet (~768px) oltre al desktop: cerca elementi che si sovrappongono, testo tagliato, immagini deformate, menu che non si apre, sezioni che diventano illeggibili.
6. Guarda la coerenza visiva tra sezioni e tra pagine: spaziature molto diverse tra sezioni simili, font o pesi tipografici che cambiano senza motivo, colori del brand usati in modo incoerente, immagini con proporzioni o qualità molto diverse tra loro, sezioni che sembrano "abbandonate a metà" o fuori dal flusso logico della pagina (es. una sezione che interrompe la narrazione, o un ordine di sezioni che non ha senso per l'utente).
7. Controlla gli elementi che si ripetono su ogni pagina (header, footer, cookie banner, menu di navigazione): devono essere identici e coerenti ovunque, a meno di differenze intenzionali.

Non fermarti alla home: naviga almeno le pagine principali collegate dal menu, più 2-3 pagine interne raggiunte cliccando CTA reali (non URL indovinati), per simulare il percorso di un visitatore vero.

## Checklist tecnica per i blocker di pubblicazione

Oltre ai controlli sopra, verifica esplicitamente questi elementi che tipicamente bloccano un go-live se mancanti o sbagliati:

- Certificato SSL attivo (il sito carica su `https://` senza warning del browser)
- Title tag e meta description presenti e sensati su ogni pagina (non vuoti, non il default del tema/builder)
- Favicon presente
- Nessun tag `noindex` o blocco `robots.txt`/meta robots dimenticato da una fase di sviluppo (a meno che sia uno staging intenzionale, in tal caso segnalalo comunque come promemoria)
- Redirect 404 personalizzata funzionante (prova un URL inesistente)
- Nessuna pagina "Coming soon", "In costruzione" o placeholder del builder rimasta online
- Cookie banner/consenso privacy presente se il sito usa tracking, e i link a Privacy Policy/Termini funzionanti e non vuoti
- Nessun link a domini di sviluppo/staging rimasto dentro il sito di produzione (o viceversa se stai testando uno staging)

## Come classificare ogni problema

Per ogni problema trovato, assegna una severità — questo è ciò che permette all'utente di capire cosa sistemare prima di andare live e cosa può aspettare:

- 🔴 **Blocca la pubblicazione**: link/pulsanti rotti, moduli che non funzionano, errori console che rompono funzionalità, sezioni che non si caricano, SSL assente, contenuto placeholder rimasto visibile, pagine 404 raggiungibili dal menu.
- 🟡 **Da sistemare prima possibile**: incongruenze di contenuto, CTA che porta alla sezione sbagliata ma la pagina esiste, problemi di responsive che rendono difficile ma non impossibile l'uso, meta tag mancanti, piccoli errori di rete non critici.
- 🟢 **Miglioria consigliata**: incoerenze grafiche minori, spaziature da rifinire, suggerimenti UX che non bloccano nulla ma alzerebbero la qualità percepita.

Non declassare un problema solo perché è "solo estetico": se una sezione sembra rotta o fuori posto a un occhio esterno, è comunque un problema di percezione per un utente reale, anche se tecnicamente "funziona".

## Output atteso

Consegna sempre due cose:

1. **Checklist in chat**, in formato markdown, organizzata per severità (🔴/🟡/🟢), con una riga per problema che includa: dove si trova (pagina/sezione), cosa non va, e cosa aspettarsi/come verificarlo di nuovo dopo la correzione. Sii specifico e concreto — "il bottone 'Richiedi preventivo' in fondo alla home porta a /contatti-vecchi che dà 404" è utile, "ci sono problemi con i link" no.
2. **File Word (.docx)** con la stessa checklist, formattata in modo professionale e condivisibile con un cliente o un team. Per generarlo, usa lo strumento/skill docx disponibile nell'ambiente DOPO aver completato la revisione — usalo solo per il documento finale, non durante l'esplorazione del sito.

Apri sempre la checklist con un brevissimo verdetto complessivo (es. "3 problemi bloccanti trovati, il sito non è pronto per andare live" oppure "nessun blocker, alcune rifiniture consigliate") prima di elencare i dettagli — è la prima cosa che chi ti ha chiesto la revisione vuole sapere.

## Vedi anche (altre skill di questo plugin)

Se il sito in revisione è una demo costruita con `homepage-elementor-redesign`, lancia questa skill come ultimo passo prima della presentazione al cliente (FASE 5 di quella skill): è il controllo indipendente che intercetta quello che il ciclo di verifica sezione-per-sezione, concentrato su una sezione alla volta, può aver lasciato passare a livello di sito intero (navigazione tra pagine, coerenza cross-sezione, blocker tecnici).
