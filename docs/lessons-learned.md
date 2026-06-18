# Lessons Learned

## Einordnung

Diese Seite fasst belegbare Learnings aus den vorhandenen Projektdokumenten zusammen. Persönliche oder teambezogene Reflexionen sind nur eingeschränkt aus dem Repository ableitbar.

## Technische Learnings aus der Dokumentation

### 1. Prompts profitieren von modularer Struktur

Aus dem Aufbau unter `prompts/` ist ersichtlich, dass Rollen, Regeln und Aufgaben sinnvoll getrennt werden können.

### 2. Lokale Demonstrierbarkeit senkt die Einstiegshürde

Die Entscheidung für Streamlit wird in den ADRs mit schneller Iteration und geringer Komplexität begründet.

### 3. Datenbankinitialisierung muss sichtbar gemacht werden

Die Known Issues zeigen, dass fehlende Tabellen ein reales Startproblem waren. Daraus folgt, dass Setup und Fehlersuche dokumentiert werden müssen.

### 4. Sicherheitsaspekte tauchen früh auf

Die Dokumentation weist explizit auf `.env`, Secret Keys und den Umgang mit Supabase-Zugängen hin.

### 5. Testartefakte erhöhen Nachvollziehbarkeit

Das Test-Dashboard zeigt, dass auch bei kleinen Lernprojekten strukturierte Rückmeldungen aus JUnit- und Coverage-Dateien nützlich sind.

## Noch nicht sicher ableitbar

### Was ich gelernt habe

TODO: fachlich klären

### Teambezogene Reflexion

TODO: fachlich klären
