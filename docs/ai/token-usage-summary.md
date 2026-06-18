# Token-Nutzungsstatistik

Diese Statistik dokumentiert die KI-Nutzung im Projekt. Exakte Werte sind nur dort angegeben, wo sie aus Tool-Metadaten ableitbar waren. Geschätzte Werte sind entsprechend markiert.

## Zeitraum der Auswertung

- Lokale Codex-CLI-Sessions: 2026-04-16 bis 2026-06-17
- Verlaufshistorie (`history.jsonl`): 2026-04-16T12:04:53+00:00 bis 2026-06-18T09:05:38+00:00

## Verwendete Quellen

- `~/.codex/sessions/`: vorhanden
- `~/.codex/history.jsonl`: vorhanden
- Projektpfad `.codex/`: nicht gefunden
- Projektpfad `.agents/`: nicht gefunden
- Manuelle Web-Schablone: `docs/ai/manual-web-usage-template.csv`

## Zusammenfassung

| Quelle | Sessions / Einträge | Input Tokens | Output Tokens | Gesamttokens | Schätzung |
|---|---:|---:|---:|---:|---|
| Codex CLI lokal | 5 | 149793145 | 1430737 | 151234195 | teilweise |
| Web Interface manuell | 0 | TODO: manuell ergänzen | TODO: manuell ergänzen | TODO: manuell ergänzen | ja |

## Lokale Codex-Auswertung

- Erkannte lokale Codex-Sessions: 5
- Exakte Token-Metadaten-Sessions: 5
- Geschätzte Sessions: 0
- Summe bekannter Input Tokens: 149793145
- Summe geschätzter Input Tokens: 0
- Summe bekannter Output Tokens: 1430737
- Summe geschätzter Output Tokens: 0
- Summe bekannter Cached Input Tokens: 129737856
- Summe geschätzter Cached Input Tokens: 0
- Summe bekannter Reasoning Tokens: 0
- Summe geschätzter Reasoning Tokens: 0
- Summe exakter Gesamttokens: 151234195
- Summe geschätzter Gesamttokens: 0

## Ergänzende Verlaufshistorie

- Einträge in `history.jsonl`: 17
- Eindeutige Session-IDs in `history.jsonl`: 5
- Diese Verlaufshistorie wurde nur als ergänzende Metadatenquelle betrachtet und nicht für Token-Summen verwendet.

## Methodik

- Exakte Tokenwerte wurden nur übernommen, wenn sie als Metadatenfelder in lokalen Session-Strukturen vorhanden waren.
- Wenn keine exakten Usage-Felder vorhanden waren, wurde konservativ auf Basis strukturierter Nachrichtenfelder geschätzt.
- Die Hauptschätzung basiert auf `tokens ≈ Zeichen / 4`.
- Wenn nicht einmal geeignete Zeichenlängen verfügbar wären, würde als Fallback `tokens ≈ Bytes / 4` verwendet.
- Prompt- und Antwortinhalte wurden nicht veröffentlicht oder in die Dokumentation übernommen.

## Grenzen

- Die lokale Auswertung deckt nur Daten auf diesem Rechner ab.
- Web-Interface-Nutzung muss manuell ergänzt werden.
- Tool-interne Abrechnung kann von lokalen Schätzungen abweichen.
- Cached Input Tokens und Reasoning Tokens sind nur sichtbar, wenn das Tool sie als Metadaten bereitstellt.
