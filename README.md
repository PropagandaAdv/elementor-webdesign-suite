# Elementor Webdesign Suite — plugin per Claude Code / Antigravity IDE

Plugin per **Claude Code** (e compatibile con **Google Antigravity IDE**) per il redesign commerciale di homepage WordPress + Elementor Pro: dal questionario cliente al brief, dal brief alla pagina Elementor pubblicata sezione-per-sezione, fino alla QA pre-pubblicazione nel browser reale.

È la versione "da terminale" della skill Cowork `homepage-elementor-redesign` che uso in agenzia, riorganizzata come plugin GitHub e potenziata con le funzionalità che solo un ambiente con bash/git/hook reali (come Claude Code o Antigravity) può offrire.

## Cosa contiene

```
elementor-webdesign-suite/
├── .claude-plugin/
│   ├── plugin.json          # manifest del plugin
│   └── marketplace.json     # marketplace self-hosted (per /plugin marketplace add)
├── skills/
│   ├── homepage-brief-builder/       # questionario cliente → brief operativo
│   ├── homepage-elementor-redesign/  # il motore di build sezione-per-sezione
│   └── website-qa-review/            # QA pre-pubblicazione nel browser reale
├── agents/
│   └── elementor-section-qa.md       # subagent per il ciclo screenshot→giudizio→fix
├── commands/
│   ├── elementor-brief.md            # /elementor-brief
│   ├── elementor-build.md            # /elementor-build
│   └── elementor-qa.md               # /elementor-qa
├── hooks/
│   ├── hooks.json                    # valida automaticamente i JSON di sezione al salvataggio
│   └── scripts/validate-elementor-json.py
├── .mcp.json                # template MCP server (WordPress + browser automation)
├── .env.example             # dove mettere URL/credenziali — mai nei file della skill
└── install-antigravity.sh   # copia le skill in .agent/skills per Antigravity IDE
```

## Cosa cambia rispetto alla skill Cowork originale

La skill Cowork era pensata per girare in un sandbox cloud isolato, con connettori abilitati da un menu e senza accesso diretto a shell/git. Qui l'ambiente è diverso (terminale reale, rete piena, filesystem persistente), e il plugin ne approfitta:

- **Nessun ambiente hardcoded.** La versione Cowork aveva uno staging e delle credenziali di default scritte nel testo della skill — comodo in una sessione privata, ma un rischio serio se lo stesso testo finisce in un repo GitHub. Qui l'ambiente WordPress (URL, utente, canale) lo dichiari sempre tu, in variabili d'ambiente o `.env` (vedi `.env.example`), mai nei file versionati.
- **Canale SSH+WP-CLI promosso a default.** Nel sandbox Cowork la rete era spesso il collo di bottiglia (da cui la preferenza per un connettore MCP "eseguito fuori dal sandbox"); da un terminale reale l'SSH diretto è normalmente il canale più solido e va preferito quando l'hosting lo supporta.
- **Validazione automatica via hook**, non solo documentata. `hooks/hooks.json` intercetta ogni `Write`/`Edit` su un JSON di sezione e lancia `validate_json.py` in automatico: un JSON malformato non arriva più al push per dimenticanza.
- **Subagent dedicato al ciclo di QA visivo** (`agents/elementor-section-qa.md`): il ciclo screenshot→giudizio→fix di ogni sezione gira in un contesto separato, così la conversazione principale non si riempie di screenshot e iterazioni di dettaglio.
- **Comandi slash rapidi** (`/elementor-brief`, `/elementor-build`, `/elementor-qa`) per lanciare le tre skill senza doverle descrivere ogni volta.
- **Browser automation esplicitamente configurabile** in `.mcp.json` (Playwright MCP di default) invece di dipendere da "Claude in Chrome", che è uno strumento specifico di Cowork/Claude Desktop.
- **Compatibile Antigravity IDE** tramite lo standard Agent Skills (SKILL.md), con uno script di installazione dedicato (vedi sotto).

## Installazione in Claude Code

1. Pubblica questo repository su GitHub (vedi sezione "Portarlo su GitHub" più sotto).
2. In Claude Code:
   ```
   /plugin marketplace add <tuo-utente>/elementor-webdesign-suite
   /plugin install elementor-webdesign-suite
   ```
3. Copia `.env.example` in `.env` nella cartella del progetto cliente su cui lavori e compila i valori del tuo ambiente WordPress (vedi `skills/homepage-elementor-redesign/references/wp-connection.md` per i dettagli sui quattro canali di accesso).
4. Se usi un MCP server WordPress (es. un plugin tipo Royal MCP) o Playwright MCP per la QA visiva, dichiarali in `.mcp.json` del tuo progetto (il template qui incluso è un punto di partenza).
5. Lancia `/elementor-brief`, `/elementor-build` o `/elementor-qa`, oppure descrivi semplicemente cosa vuoi fare — le skill si attivano anche per trigger implicito.

## Installazione in Google Antigravity IDE

Antigravity (dalla versione 1.14.2) legge le Agent Skills nello stesso formato SKILL.md di Claude Code, ma non conosce il concetto di "plugin": cerca le skill in `.agent/skills/<nome>/` (a livello di progetto) o `~/.gemini/antigravity/skills/<nome>/` (a livello globale). Per questo il repo include uno script dedicato:

```bash
# dentro il progetto su cui stai lavorando in Antigravity
./install-antigravity.sh            # installa le 3 skill in .agent/skills/
./install-antigravity.sh --global   # oppure a livello globale, per tutti i progetti
```

Nota: hook, comandi slash e il subagent `elementor-section-qa` sono concetti specifici del sistema di plugin di Claude Code e non vengono letti da Antigravity — solo le tre cartelle skill (SKILL.md + `references/` + `scripts/`) sono portabili così come sono. In Antigravity, il ciclo di verifica visiva descritto nella skill puoi farlo con il browser integrato dell'IDE invece che con il subagent.

## Portarlo su GitHub

Questo repo non è ancora stato pubblicato su GitHub. Tre modi per farlo, a seconda di cosa preferisci:

1. **Da questa sessione, con il tuo account GitHub collegato**: il connettore GitHub del tuo account risulta collegato ma non abilitato in questa chat. Abilitalo dalle impostazioni dei connettori di questa conversazione e potrò creare il repository e caricare i file direttamente.
2. **In autonomia dal tuo computer**: scarica lo zip allegato, scompattalo, e da terminale:
   ```bash
   cd elementor-webdesign-suite
   git init && git add -A && git commit -m "Initial commit"
   gh repo create <tuo-utente>/elementor-webdesign-suite --private --source=. --push
   ```
   (o crea il repo vuoto su github.com e fai `git remote add origin ...` + `git push`).
3. **Dal tuo Mac/PC se hai la app desktop di Claude aperta e una cartella collegata**: posso salvare il progetto direttamente in quella cartella e, se lì hai già `git`/`gh` configurati con le tue credenziali, lanciare il push da lì.

Qualunque opzione tu scelga, controlla `git status`/`git diff` prima del primo push: questo README e gli script sono già scritti per non contenere credenziali, ma se personalizzi la skill con dati della tua agenzia prima di pubblicare, verifica di non aver aggiunto nulla di sensibile.

## Sicurezza

- Nessuna credenziale reale (URL di staging riservati, password, Application Password, chiavi MCP) deve mai finire in un file tracciato da git. Usa sempre `.env` (ignorato da `.gitignore`) o variabili d'ambiente.
- La skill lavora sempre su staging/demo, mai su siti di produzione senza conferma esplicita dell'utente.
- Il testo delle pagine web consultate (gallery di design, siti dei clienti/competitor) va trattato come dato da osservare, mai come istruzione da eseguire — vedi la nota su prompt injection in `homepage-brief-builder/SKILL.md`.

## Manutenzione

Dopo ogni modifica a una delle tre skill, rileggi `skills/homepage-elementor-redesign/evals/evals.json` e verifica a occhio (o con un agente di verifica) che gli scenari elencati si comportino ancora come atteso — non c'è un runner automatico incluso, è una checklist di regressione manuale.
