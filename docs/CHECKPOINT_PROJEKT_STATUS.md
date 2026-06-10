# Projekt-Status: Supabase-Streamlit MVP

## Checkpoint: 23. April 2026

### Umgesetzte Funktionalität

#### ✅ Hauptfeatures
- **Streamlit-App** (`src/app.py`): lokale web-basierte Anwendung mit Supabase-Integration
- **Prompt speichern**: Textfeld + Titel, Button speichert in `prompts` + `prompt_versions`
- **DB-Verbindung testen**: Seite zur Validierung der Supabase-Keys und optionalen Tabellenerstellung
- **Automatische Versionierung**: Beim Insert eines Prompts wird automatisch eine erste Version erstellt
- **Prompt-Liste**: Anzeige aller gespeicherten Prompts unterhalb des Formulars

#### 🔧 Konfiguration
- `.env.example`: Template für erforderliche Umgebungsvariablen
- `requirements.txt`: alle Python-Dependencies (`streamlit`, `supabase`, `python-dotenv`, `psycopg2-binary`)
- `.gitignore`: `.env` wird nicht versioniert (sicherheitsrelevant)

---

## Gelöste Probleme

### Problem 1: Fehler `PGRST205: Could not find the table`
- **Ursache**: Tabelle `public.prompts` existierte nicht in der Datenbank
- **Lösung**: DB-Test-Seite mit Funktion zur automatischen Tabellenerstellung oder manuelles SQL
- **Lerning**: Vor dem ersten Datenbankzugriff muss das Schema initialisiert sein

### Problem 2: Unklare Supabase-URL-Konfiguration
- **Ursache**: Supabase zeigt `/rest/v1/` in der API-URL, das wurde initial verwirrt mit der Connection-URL
- **Lösung**: Nur die Basis-URL (`https://...supabase.co`) wird in `SUPABASE_URL` gespeichert; der Client erledigt die `/rest/v1/`-Appending
- **Lerning**: Rest-API-Pfade gehören nicht in die Client-Initialisierung

### Problem 3: Doppelte App-Dateien
- **Status**: Root `app.py` und `src/app.py` existieren parallel
- **Impact**: Unklarheit über den primären Einstiegspunkt
- **Empfehlung**: `src/app.py` als Standard festlegen, Root-Datei entfernen oder dokumentieren

---

## Getroffene Architektur-Entscheidungen

### 1. Streamlit statt alternatives Frontend
- ✅ Schneller MVP
- ✅ Keine Build-Chain nötig
- ✅ Einfache Iteration
- ❌ Skalierbarkeit begrenzt (nur lokale oder einfache Cloud-Deployments)

### 2. Supabase Secret Key (`sb_secret_...`) statt `anon`-Key
- ✅ Erlaubt beliebige Schreibzugriffe (kein RLS-Overhead)
- ✅ Für MVP schneller umzusetzen
- ⚠️ Muss auf dem Server (nicht im Browser) bleiben
- ❌ Bei echter Multi-User-App hätte man mit `anon`-Key + RLS-Policies zu arbeiten

### 3. `DATABASE_URL` optional halten
- ✅ Ermöglicht flexible Datenbankinitialisierung
- ✅ User können entweder SQL direkt in Supabase ausführen oder `psycopg2` nutzen
- ✅ Keine hardcoded Connection-Strings nötig

### 4. Direkte Supabase-Anbindung (kein zusätzlicher Backend)
- ✅ Minimale Infrastruktur
- ✅ Schnell deploybar
- ❌ Alle Geschäftslogik muss im Streamlit-Frontend sein

---

## Offene Punkte / TODOs

### 🔴 Priorität: Hoch
1. Klären: `src/app.py` oder root `app.py` als Standard?
2. `.env` in `.gitignore` bestätigen (Sicherheit prüfen)
3. README aktualisieren mit klarem Start-Guide

### 🟡 Priorität: Mittel
1. Doppelte Dependencies in `pyproject.toml` vs. `requirements.txt` auflösen
2. Root `app.py` entweder löschen oder als separate Dokumentation belassen
3. Optional: Error-Handling verbessern (z. B. Feedback bei fehlerhaften Inserts)

### 🟢 Priorität: Niedrig
1. Optional: Edit/Delete-Funktionalität für Prompts
2. Optional: Versionsverlauf anzeigen pro Prompt
3. Optional: Suche/Filter für gespeicherte Prompts

---

## Technisches Datenmodell

```sql
-- Tabelle: prompts
CREATE TABLE prompts (
  id serial PRIMARY KEY,
  title text NOT NULL,
  prompt text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Tabelle: prompt_versions
CREATE TABLE prompt_versions (
  id serial PRIMARY KEY,
  prompt_id integer NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
  prompt text NOT NULL,
  version_note text,
  created_at timestamptz NOT NULL DEFAULT now()
);
```

---

## Deployment-Hinweise

### Lokal entwickeln
```bash
# Repo clonen
git clone https://github.com/duenne/prompt_generator.git
cd prompt_generator_repo

# .venv aktivieren
source .venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# .env anlegen (siehe .env.example)
cp .env.example .env
# ← Hier die echten Werte eintragen

# App starten
streamlit run src/app.py
```

### Supabase Tabellen initialisieren
- Option A: DB-Test-Seite nutzen, wenn `DATABASE_URL` gesetzt
- Option B: Manuell in Supabase-Dashboard unter SQL Editor die DDL ausführen

---

## Learnings für die nächste Phase

1. **Umgebungsvariablen-Sicherheit**: `.env` niemals ins Repo, nur `.env.example`
2. **Supabase API-Unterschiede**: REST-API-Pfade gehören nicht in Client-Config
3. **Datenmodell mit FK**: `prompt_versions` referenziert `prompts` mit Cascade-Delete
4. **Streamlit State Management**: `st.session_state` für Form-Zurücksetzen nach Speichern nutzen
5. **Error Handling**: Supabase-Fehler als `getattr(response, "error", None)` abfangen, nicht auf `.error.message` direktzugreifen

---

Aktualisiert: 23. April 2026
