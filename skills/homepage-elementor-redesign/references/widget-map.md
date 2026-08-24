# Mappatura Sezione → Widget Elementor

Per ogni sezione dello schema a 10 blocchi: widget consigliato (Pro), alternativa Free, e note di costruzione.

| # | Sezione | Widget Pro consigliati | Alternativa Free | Note |
|---|---|---|---|---|
| 1 | Header/Navbar | `nav-menu` + `theme-site-logo` | `image` (logo) + `icon-list` orizzontale o heading+link | Container sticky: `position: "sticky"` nei settings avanzati (`"position":"fixed"` sconsigliato per demo). Per demo usare menu manuale con anchor `#sezione`, non il menu WP (spesso vuoto su staging). |
| 2 | Hero | `heading`, `text-editor`, `button` ×2 | idem (tutti free) | Background image container + overlay. Doppia CTA: primaria piena, secondaria outline. |
| 3 | Trittico segmentazione | `icon-box` ×3 oppure card custom (container + image + heading + text + button) | idem | Card come container inner con `flex_wrap`, width 33.33% desktop → 100% mobile. Preferire card custom con micro-visual MCP rispetto a icon-box quando le immagini sono il punto di forza. |
| 4 | Showcase prodotti/servizi | card custom in griglia; `loop-grid` solo se esistono CPT reali | card custom | 2×2 o 3×2. Tag = piccolo `heading` h6 con background pill (padding + radius 999). |
| 5 | Istituzionale + numeri | `text-editor` + `counter` ×3-4 | idem (counter è free) | Fascia numeri su background primario o accent, numeri grandi (48-64px). |
| 6 | Qualità/certificazioni | `image-carousel` (loghi) o griglia `image` | griglia `image` | Loghi in monocromo/grigio per uniformità; se mancano i loghi reali, testo delle certificazioni in `icon-list` con check. |
| 7 | Settori serviti | griglia card compatte o `image-carousel` | idem | 4-6 verticali, immagine MCP quadrata + label. |
| 8 | News & insights | 3 card manuali (image + meta + heading + link) | idem | NON usare widget `posts` su staging vuoto. Copiare 3 titoli reali dal blog del cliente se esiste. |
| 9 | CTA di chiusura | `call-to-action` oppure container custom + `form` | container custom + button (Contact Form 7 se serve un form free) | Full-width, alto contrasto, una sola azione. Il `form` Pro con submit email è la scelta migliore per demo di lead-gen. |
| 10 | Footer | container a 4 colonne: `image` (logo), `icon-list` ×2, `social-icons` | idem (tutti free) | Dati legali reali (P.IVA dal sito attuale). Ultima riga: copyright + credits agenzia. |

## Pattern di card riutilizzabile (usato in 3, 4, 7, 8)

Container inner (`isInner: true`, direction column, background bianco/surface, radius 12, shadow soft, padding 0 con immagine full-bleed in alto oppure padding 24 uniforme):
1. `image` (visual MCP, radius solo top se full-bleed)
2. `heading` h3 (20-24px)
3. `text-editor` (2-3 righe max)
4. `button` ghost/text-link ("Scopri di più →")

Duplicare la struttura variando id, contenuti e immagine: la ripetizione strutturale identica è ciò che dà l'aspetto "sistema di design" alla demo.

## Widget da NON usare nelle demo

- `posts`, `portfolio`, `woocommerce-*`: dipendono da contenuti che sullo staging non esistono → sezioni vuote.
- `template` / shortcode di altri plugin: creano dipendenze invisibili.
- `html` con CSS/JS custom pesante: la demo deve dimostrare che il risultato è raggiungibile con Elementor "pulito", editabile dal cliente. Piccoli ritocchi CSS di pagina sono ammessi in `_elementor_page_settings.custom_css` (Pro), dichiarandoli.
