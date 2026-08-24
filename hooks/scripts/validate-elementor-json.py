#!/usr/bin/env python3
"""
validate-elementor-json.py — hook PostToolUse per Claude Code.

Si aggancia a ogni Write/Edit e, se il file toccato è un JSON di sezione
Elementor (dentro una cartella "sections/", o chiamato "page-state.json",
o dentro "references/examples/" della skill homepage-elementor-redesign),
lancia automaticamente scripts/validate_json.py di quella skill.

Legge l'evento hook da stdin (JSON, formato Claude Code):
  {"tool_name": "Write", "tool_input": {"file_path": "...", ...}, ...}

Se la validazione fallisce, stampa l'errore su stderr ed esce con codice 2:
in un hook PostToolUse questo rimanda l'output a Claude come feedback da
correggere prima di procedere con il push, invece di scoprirlo solo al
momento della chiamata REST/SSH.

Se il file non è pertinente (non un JSON di sezione), esce silenziosamente
con codice 0 senza fare nulla.
"""

import json
import os
import subprocess
import sys


def is_elementor_section_candidate(path: str) -> bool:
    if not path.endswith(".json"):
        return False
    lowered = path.replace("\\", "/").lower()
    if "/sections/" in lowered or lowered.endswith("/page-state.json") or lowered.endswith("page-state.json"):
        return True
    if "/references/examples/" in lowered and "homepage-elementor-redesign" in lowered:
        return True
    return False


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except Exception:
        # Se non riusciamo a leggere l'evento, non blocchiamo nulla.
        return 0

    tool_name = event.get("tool_name", "")
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        return 0

    tool_input = event.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path") or tool_input.get("path")
    if not file_path or not is_elementor_section_candidate(file_path):
        return 0

    if not os.path.exists(file_path):
        # Il file potrebbe non essere ancora stato scritto su disco in questo hook event;
        # in quel caso non c'è nulla da validare qui.
        return 0

    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    validator = os.path.join(
        plugin_root,
        "skills", "homepage-elementor-redesign", "scripts", "validate_json.py",
    )
    if not os.path.exists(validator):
        # Fallback: prova un percorso relativo a questo script (due livelli sopra + skills/...)
        here = os.path.dirname(os.path.abspath(__file__))
        candidate = os.path.join(here, "..", "..", "skills", "homepage-elementor-redesign", "scripts", "validate_json.py")
        validator = os.path.normpath(candidate)

    if not os.path.exists(validator):
        print(f"[elementor-webdesign-suite] validatore non trovato ({validator}), salto il controllo automatico.", file=sys.stderr)
        return 0

    args = [sys.executable, validator, file_path]
    if "/sections/" in file_path.replace("\\", "/") or file_path.endswith("page-state.json"):
        args.append("--section")

    result = subprocess.run(args, capture_output=True, text=True)

    if result.returncode != 0:
        sys.stderr.write(
            "Validazione automatica JSON Elementor FALLITA per "
            f"{file_path} (hook homepage-elementor-redesign):\n\n"
            f"{result.stdout}\n{result.stderr}\n\n"
            "Correggi il file prima di procedere con il push (mai spingere sezioni non validate).\n"
        )
        return 2

    if result.stdout.strip():
        # Warning non bloccanti: li portiamo comunque a conoscenza di Claude.
        print(f"[elementor-webdesign-suite] {file_path}: {result.stdout.strip()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
