# Design Inspiration — fonti, pattern e principi per sezioni innovative

Questo file guida la FASE 2 (schema homepage) e la FASE 4 (build): come usare le gallery
di riferimento per progettare sezioni **innovative e creative ma coerenti** — col brand
del cliente, con le convenzioni del web (Jakob's Law) e con ciò che Elementor sa fare.

**Regola madre: ispirazione ≠ copia.** Dalle gallery si estraggono *pattern* (struttura,
ritmo, gerarchia, uso dello spazio), MAI layout interi, palette altrui o asset. Ogni
pattern adottato va dichiarato nella Section Map ("hero split ispirato ai casi X del
settore, adattato alla palette brand").

---

## 1. Workflow di consultazione (in FASE 2, prima della Section Map)

1. **Cerca il settore del cliente** su 2-3 gallery generaliste (Awwwards, SiteInspire,
   Lapa.ninja per landing; Behance/Dribbble cercando "Elementor <settore>" per vedere
   cosa è realisticamente ottenibile col builder).
2. **Estrai 3-5 pattern concreti** che ricorrono nei casi migliori del settore: tipo di
   hero, struttura delle card, trattamento tipografico, footer. Annota per ciascuno:
   cosa lo rende efficace + come si implementa in Flexbox Container.
3. **Verifica componenti specifici** sulle gallery tematiche: footer.design per il
   footer, bentogrids.com se valuti una griglia bento, typewolf.com per il pairing
   tipografico coerente col carattere del brand.
4. **Filtra con i principi** (sezione 4): un pattern spettacolare che viola Hick's Law o
   il mental model del target B2B si scarta.
5. Dichiara i pattern scelti nella Section Map che sottoponi all'utente.

La consultazione avviene via web search/browsing (WebSearch/WebFetch in Claude Code, gli strumenti equivalenti in Antigravity); se le gallery non sono
raggiungibili in sessione, usa la pattern library della sezione 3 come base già distillata.

## 2. Catalogo fonti (a cosa serve ciascuna)

**Gallery generaliste — per direzione estetica e benchmark di settore**
- awwwards.com — lo stato dell'arte; cerca per industry/tag. Attenzione: molti vincitori
  usano WebGL/motion pesante non replicabile in Elementor → estrai composizione e
  tipografia, non gli effetti.
- godly.design (+ la guida su uiuxshowcase.com/resources/godly-website/) — selezione
  curatissima di siti "astonishing": ottimo per hero e uso radicale del whitespace.
- siteinspire.com — filtrabile per stile/tipo/soggetto; il più utile per B2B sobrio.
- httpster.net — design "normale ma perfetto": riferimento per clienti che vogliono
  pulizia, non spettacolo.
- mindsparklemag.com — branding + web: utile quando il redesign deve valorizzare
  un'identità visiva forte.
- designspiration.com — moodboard visivi trasversali (grafica, non solo web).
- lapa.ninja — archivio di landing page per categoria: il riferimento più diretto per
  lo schema a 10 blocchi della skill.
- mailerlite.com/features/landing-pages — pattern di landing orientate a conversione
  (struttura benefit → social proof → form): utile per demo lead-gen.

**Gallery di componenti — per la singola sezione**
- bentogrids.com — griglie bento: il pattern showcase più attuale (vedi esempio golden
  `examples/bento.json`).
- footer.design — footer come sezione di design, non ripostiglio di link.
- typewolf.com — pairing tipografici reali con esempi in uso; da qui si scelgono le
  coppie heading/body da mappare sui Global Fonts.
- refero.design e mobbin.com — pattern di UI web/app reali per componenti (nav, form,
  pricing); mobbin è mobile-first: utile per decidere i comportamenti `_mobile`.
- pageflows.com — flussi utente registrati: utile per decidere dove portano le CTA.

**Principi e casi — il filtro critico**
- lawsofux.com — le leggi di UX (sezione 4).
- growth.design/case-studies — case study su psicologia e conversione: da qui i
  micro-pattern di persuasione etica (progress, social proof, riduzione attrito).
- uxdesign.cc — approfondimenti; utile per motivare le scelte nel documento di metodo.

## 3. Pattern library distillata (trend → implementazione Elementor)

Pattern ricorrenti nei casi migliori delle gallery sopra, già tradotti in costruzione
Flexbox Container. Scegline in FASE 2 quelli coerenti col brand — non tutti insieme:
**una homepage eccellente usa 2-3 gesti distintivi, non dieci** (Von Restorff funziona
solo se l'elemento distintivo è UNO).

1. **Bento grid** (showcase/servizi): griglia a celle di peso diverso (1 cella 2/3 + 1
   da 1/3, poi 3 da 1/3) invece della solita griglia uniforme. Container wrap con width
   66/32/32/32/32%, `_mobile` tutto 100%. → `examples/bento.json`.
2. **Tipografia oversize come elemento grafico**: H1 72-110px desktop (34-40 mobile),
   font-weight forte, line-height 1.05-1.15; il testo È il visual, il resto respira.
   Richiede `typography_font_size_mobile` sempre.
3. **Whitespace radicale**: padding verticali 120-160px sulle sezioni chiave, un solo
   messaggio per viewport. Il lusso percepito del sito è proporzionale allo spazio vuoto
   (Aesthetic-Usability Effect).
4. **Hero split asimmetrico**: 55-60% testo / 40-45% visual, mai 50/50; su mobile
   column con testo prima.
5. **Fascia social proof "quiet"**: subito sotto l'hero, loghi clienti in monocromo
   (grayscale/opacity 0.6), nessun titolo urlato — "Scelti da" basta.
6. **Sticky header minimale**: logo + 4-5 voci max + 1 CTA (Hick's Law e Miller's Law:
   oltre 5 scelte la decisione rallenta).
7. **Card system rigoroso**: la stessa anatomia di card ripetuta identica (radius,
   shadow, padding) in tutte le sezioni a griglia — Law of Similarity: la ripetizione
   strutturale è ciò che fa percepire "design system".
8. **Numeri grandi come punteggiatura**: counter 56-72px su fascia a colore pieno del
   brand; 3-4 numeri max (Chunking).
9. **Footer progettato**: 4 colonne + riga legale, oppure footer "statement" con
   payoff grande — mai un ripostiglio (vedi footer.design). È l'ultima cosa che si vede:
   Peak-End Rule.
10. **Micro-interazioni sobrie**: hover su card (translateY -4px + shadow) e sui bottoni;
    in Elementor via `_hover` nei settings o `custom_css` di pagina dichiarato. Niente
    animazioni d'ingresso ovunque: una sezione animata è un accento, dieci sono rumore.
11. **CTA a contrasto isolata** (chiusura): sezione a colore pieno, UNA sola azione,
    bottone grande (Fitts's Law: target grandi e vicini al punto di attenzione).
12. **Scroll narrativo / sfondo continuo**: la pagina percepita come un unico visual
    (immagine o video master) su cui si muovono in parallasse solo alcuni layer, con
    velocità diverse a creare profondità. È il gesto a più alto impatto in demo —
    tecnica completa, chiavi Motion Effects e guardrail in `scroll-motion.md`.
13. **Pairing tipografico a contrasto** (da typewolf): display serif o grotesk marcato
    per gli heading + sans neutro per il body; mai due font simili. Mappare SEMPRE sui
    Global Fonts del Kit, mai font hardcoded per widget.

## 4. Laws of UX applicate alla homepage (filtro decisionale)

Checklist da passare sulla Section Map prima di sottoporla all'utente:

- **Jakob's Law** — l'utente si aspetta le convenzioni degli altri siti: logo in alto a
  sx, nav in alto, CTA a dx, footer con contatti. Innovare dentro la convenzione, non
  contro.
- **Hick's Law + Choice Overload** — poche scelte per sezione: 1-2 CTA nell'hero, max
  5 voci di menu, una sola azione nella CTA finale.
- **Miller's Law / Chunking** — gruppi da 3-6 elementi (card, numeri, voci): mai griglie
  da 8+ item senza raggruppamento.
- **Fitts's Law** — CTA grandi (padding ≥16/32), area cliccabile piena, anchor che
  portano esattamente dove promettono.
- **Law of Proximity / Common Region** — gap interni alla card < gap tra card; le
  sezioni si separano con background alternati o spazio, non con divider decorativi.
- **Law of Similarity / Uniform Connectedness** — elementi con la stessa funzione hanno
  lo stesso aspetto in tutta la pagina (tutti i link-card uguali, tutte le CTA primarie
  uguali).
- **Von Restorff Effect** — UN elemento distintivo per viewport (la CTA primaria, il
  numero chiave): se tutto è evidenziato, niente lo è.
- **Serial Position Effect + Peak-End Rule** — le posizioni che contano: hero (primo),
  CTA+footer (ultimo). Lì va la massima cura; il "peak" è la sezione showcase.
- **Aesthetic-Usability Effect** — la cura estetica (spaziature coerenti, contrasti,
  allineamenti perfetti) aumenta la fiducia percepita: è il motivo del ciclo di feedback
  visivo in FASE 4.
- **Cognitive Load** — copy micro (max 2-3 righe per blocco), un concetto per sezione;
  il dettaglio va nelle pagine interne, la homepage orienta.
- **Goal-Gradient Effect** — nei form della demo: pochi campi (3-4), label chiare,
  bottone che dichiara cosa succede dopo.

## 5. Guardrail finali

- **Coerenza brand > trend**: se il brand del cliente è tradizionale, il bento grid può
  essere il gesto innovativo sufficiente; non forzare estetiche da studio creativo su
  un'azienda di impiantistica.
- **Fattibilità Elementor**: ogni pattern scelto deve restare costruibile in Flexbox
  Container puliti ed editabile dal cliente (Regola d'oro della skill). I benchmark
  Dribbble/Behance "Elementor" servono proprio a calibrare l'asticella del realizzabile.
- **Accessibilità non negoziabile**: nessun trend giustifica contrasti < 4.5:1 o testo
  sopra immagini senza overlay.
- **Nel documento di metodo** (FASE 5) cita i principi usati (2-3 leggi UX, i pattern di
  riferimento): è ciò che distingue la proposta dell'agenzia da "un sito carino".
