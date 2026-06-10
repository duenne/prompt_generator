# Known Issues & Lernpunkte

## Issue 1: Fehler `PGRST205: Could not find the table`

**Severity**: 🔴 Critical (für Startup)  
**Status**: ✅ Gelöst  
**Datum erkannt**: 23. April 2026

### Symptom
```
{'message': "Could not find the table 'public.prompts' in the schema cache", 
 'code': 'PGRST205', ...}
```

### Ursache
Die Supabase-Datenbank hatte die Tabellen `prompts` und `prompt_versions` noch nicht.
Supabase REST-Client versucht, die Tabelle zu lesen → Fehler.

### Lösung
Zwei Optionen implementiert:
1. **Automatisch** (mit `DATABASE_URL`): Button in der DB-Test-Seite führt DDL aus
2. **Manuell**: SQL direkt im Supabase Dashboard ausführen

### Prevention
- Immer zuerst DB-Test-Seite checken
- Oder vor dem ersten Start `DATABASE_URL` setzen + Button nutzen
- Dokumentation: `.env.example` enthält Hinweise

### Für Studierenden zum Lernen
- Zeigt: Datenbanken müssen initialisiert werden
- REST-APIs sind stark vom Schema abhängig
- Fehlerbehandlung: `getattr(response, "error", None)` ist robuster als direkter Access

---

## Issue 2: Doppelte App-Dateien

**Severity**: 🟡 Medium (Verwirrung)  
**Status**: ⏳ Offen  
**Datum erkannt**: 23. April 2026

### Problem
Im Repo existieren zwei Python-App-Dateien:
- `app.py` im Projektroot (sehr einfaches Beispiel)
- `src/app.py` (komplette MVP mit all Features)

### Impact
- Unklarheit: Welche App sollen Studierenden starten?
- Git: `app.py` wurde mit gecommitted, obwohl `src/app.py` die Hauptapp ist
- Dokumentation: Start-Befehl unklar

### Konsequenz für Studierenden
Sie müssen `streamlit run src/app.py` nutzen, nicht `streamlit run app.py`.

### Zu beheben
- ✅ In README dokumentieren: `src/app.py` ist Standard
- 🔜 Option: `app.py` löschen oder explizit als "Minimal Example" kennzeichnen

---

## Issue 3: Supabase-URL mit `/rest/v1/` verwirrt

**Severity**: 🟡 Medium (Fehlerquelle)  
**Status**: ✅ Dokumentiert  
**Datum erkannt**: 23. April 2026

### Problem
Supabase zeigt mehrere URLs in der Web-UI:
- Project URL: `https://...supabase.co`
- API URL: `https://...supabase.co/rest/v1/`

Anfänger tragen die API-URL in `SUPABASE_URL` ein → `InvalidURL`-Fehler.

### Lösung
Nur die **Basis-URL** verwenden.
Der Python-Client erledigt `/rest/v1/` automatisch.

### Für Studierenden zum Lernen
- REST APIs haben standardisierte Pfade
- Client-Libraries abstrahieren diese Details
- `.env.example` sollte solche Hinweise enthalten

### Prevention
- Clear in `.env.example` dokumentieren
- README-Anleitung hinzufügen

---

## Issue 4: `.env` Sicherheit

**Severity**: 🔴 Critical  
**Status**: ✅ Implementiert  
**Datum**: 23. April 2026

### Problem
Wenn `.env` ins Git committet würde, sind alle Secrets publik!

### Implementierte Lösung
```gitignore
.env
```

Plus `.env.example` als sicheres Template.

### Für Studierenden zum Lernen
- Secrets gehören niemals ins Git
- `.env` + `.example` Pattern verwenden
- Selbst `python-dotenv` nicht `python-decouple` nutzen (letzteres ist sicherer, da defaults in Files)

### Prevention
- `.gitignore`-Check vor jedem `git push`
- Optional: Pre-Commit-Hooks für Secrets-Scanning

---

## Issue 5: Abhängigkeits-Duplikate

**Severity**: 🟡 Medium  
**Status**: ⏳ Offen  
**Datum erkannt**: 23. April 2026

### Problem
```
pyproject.toml: dependencies = ["streamlit>=1.35"]
requirements.txt: streamlit>=1.35
                  supabase>=2.28.3
                  python-dotenv>=1.0
                  psycopg2-binary>=2.9
```

Beide Dateien werden gepflegt, aber sind nicht konsistent.

### Konsequenzen
- Unklarheit: Welche nutzen für `pip install`?
- Wartungslast: Wenn neue Version nötig → beide Dateien updaten

### Zu beheben
Option A: Nur `requirements.txt` (bei Development)
Option B: `pyproject.toml` authoritative machen, `requirements.txt` davon generieren

### Für Studierenden zum Lernen
- Python hat mehrere Dependency-Systeme (pip, poetry, setuptools)
- Moderne Best Practice: `pyproject.toml` mit PEP 517/518
- Ältere Projekte nutzen `requirements.txt`

---

## Issue 6: Error Handling in Supabase-Responses

**Severity**: 🟢 Low  
**Status**: ✅ Implementiert (aber ausbaubar)  
**Datum**: 23. April 2026

### Beobachtung
Supabase-Responses haben kein einheitliches Error-Format:
- Manchmal: `response.error` (Objekt)
- Manchmal: `response.error.message` (String)
- Manchmal: `None` bei Erfolg

### Aktuelle Lösung
```python
error = getattr(response, "error", None)
if error:
    message = getattr(error, "message", str(error))
```

### Für Studierenden zum Lernen
- APIs können inkonsistent sein
- `getattr(obj, attr, default)` ist sicherer als direkter Access
- Defensive Programmierung ist wichtig

### Mögliche Verbesserung
Custom Exception-Wrapper für klarere Error-Handling

---

## Issue 7: Session State und Formular-Reset

**Severity**: 🟢 Low (UX-Polish)  
**Status**: ✅ Implementiert  
**Datum**: 23. April 2026

### Problem
Nach dem Speichern eines Prompts sollte das Formular geleert werden,
damit Nutzer gleich einen neuen eingeben können.

### Lösung
Streamlit `session_state` verwendet:
```python
if success:
    st.session_state["save_title"] = ""
    st.session_state["save_prompt_text"] = ""
    st.experimental_rerun()
```

### Für Studierenden zum Lernen
- Streamlit ist **reaktiv** (state-getrieben)
- `st.rerun()` triggert vollständiges Re-Rendering
- `session_state` persistiert über Re-Renders

---

## Lernpunkte für die nächste Phase

### Backend & Datenmodelle
- [ ] FK-Constraints und Cascade-Deletes verstehen
- [ ] Migrations-Tools wie Alembic einführen (nicht nur DDL)
- [ ] Transaction-Safety bei Multi-Insert Szenarien

### Security
- [ ] RLS (Row-Level Security) bei Multi-User Nutzung
- [ ] Authentication (z. B. Supabase Auth) implementieren
- [ ] Rate-Limiting für Prompt-Speicherung

### Performance & Skalierung
- [ ] Pagination für große Prompt-Listen
- [ ] Index-Strategien für `title` & `created_at`
- [ ] Caching für häufige Queries

### DevOps
- [ ] Containerisierung (Docker) für Streamlit
- [ ] CI/CD Pipeline (GitHub Actions)
- [ ] Secrets Management (z. B. GitHub Secrets)

---

**Stand**: 23. April 2026
