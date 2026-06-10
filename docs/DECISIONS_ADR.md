# Architektur-Entscheidungen (ADRs)

## ADR-001: Streamlit als Frontend-Framework

**Status**: ✅ Entschieden  
**Datum**: 23. April 2026

### Problem
Brauche schnellen MVP für lokale Prompt-Speicherung mit einfacher DB-Integration.

### Entscheidung
Nutze **Streamlit** statt:
- React/Vue/Angular (zu viel Boilerplate für MVP)
- FastAPI + Frontend (zu komplex für Einzelentwicklung)
- CLI-Tool (keine Web-UI nötig)

### Konsequenzen
✅ **Positive**:
- Zero Build-Pipeline, nur `streamlit run app.py`
- Python-basiert, keine JavaScript-Abhängigkeiten
- Schnelle Iteration möglich
- Natürliche Integration mit Python-Libraries

⚠️ **Nachteile**:
- Deployment begrenzt auf Cloud-Plattformen mit Streamlit-Support (z. B. Streamlit Cloud, Docker)
- Performance bei vielen Benutzern limitiert
- Customization der UI begrenzt auf Streamlit-API

---

## ADR-002: Supabase Service Role Key für Schreibvorgänge

**Status**: ✅ Entschieden  
**Datum**: 23. April 2026

### Problem
Wie soll die App Daten in Supabase speichern?

### Optionen
1. **Anon-Key** + RLS-Policies (Row-Level Security)
   - Sicherer, aber komplexer
   - Erfordert pro Tabelle RLS-Policies
   - Mehrbenutzersystem müsste User-IDs tracken

2. **Service Role Key** (Server-seitig)
   - Einfacher für MVP
   - Beliebige Schreibvorgänge ohne RLS
   - ⚠️ Darf nie im Browser landen!

### Entscheidung
**Service Role Key** verwenden, da:
- MVP-Fokus (schnelle Umsetzung)
- Lokale App (nicht öffentlich im Browser)
- Keine Multi-User-Authentifizierung nötig

### Konsequenzen
- ✅ Einfache Implementierung
- ✅ Keine RLS-Policy-Verwaltung nötig
- ⚠️ **Kritisch**: Secret Key muss in `.env` bleiben, niemals öffentlich
- 🔴 **Bei echter Multi-User-App**: Umstieg auf Anon-Key + Policies nötig

---

## ADR-003: Supabase-URL Format

**Status**: ✅ Entschieden  
**Datum**: 23. April 2026

### Problem
Supabase zeigt mehrere URLs:
- Project URL: `https://fusmcxwtarjwoztxzhlr.supabase.co`
- API URL: `https://fusmcxwtarjwoztxzhlr.supabase.co/rest/v1/`
- Direct Connection: `postgresql://...`

Welche gehört in den Python-Client?

### Entscheidung
Nur die **Basis-URL** verwenden:
```env
SUPABASE_URL=https://fusmcxwtarjwoztxzhlr.supabase.co
```

**NICHT**: `/rest/v1/` in der URL-Config.

Der Supabase-Python-Client erledigt `/rest/v1/`-Appending automatisch.

### Konsequenzen
- ✅ Korrekte Funktionalität
- ✅ Weniger Fehlerquelle
- 📝 Muss in Projektdoku klar dokumentiert sein

---

## ADR-004: DATABASE_URL Optional

**Status**: ✅ Entschieden  
**Datum**: 23. April 2026

### Problem
Wie sollen Tabellen initialisiert werden?

### Optionen
1. **Nur Supabase-Dashboard**: User führt SQL manuell aus
2. **DATABASE_URL + psycopg2**: App kan DDL automatisch ausführen
3. **Migrations-Framework** (z. B. Alembic): Zu komplex für MVP

### Entscheidung
Beide Wege unterstützen:
- User können `DATABASE_URL` in `.env` setzen → App erstellt Tabellen
- Oder manuell in Supabase SQL Editor ausführen

### Konsequenzen
- ✅ Flexibel
- ✅ Keine zwingende Abhängigkeit von `psycopg2`
- 📝 Dokumentation muss klar beide Wege zeigen

---

## ADR-005: Keine zusätzliche Backend-Layer

**Status**: ✅ Entschieden  
**Datum**: 23. April 2026

### Problem
Sollte es einen separaten Server geben (z. B. FastAPI), der zwischen Streamlit und Supabase sitzt?

### Entscheidung
**Nein**, direkter Supabase-Client in der Streamlit-App.

### Konsequenzen
- ✅ Minimale Infrastruktur
- ✅ Schneller MVP
- ⚠️ Alle Geschäftslogik bleibt in Streamlit (später ggf. umzulagern)
- 🔴 **Bei späterem Wachstum**: Umstrukturierung zu dediziertem API-Server sinnvoll

---

## ADR-006: Versionierung mit `prompt_versions` Tabelle

**Status**: ✅ Entschieden  
**Datum**: 23. April 2026

### Problem
Wie wird Prompt-Versionierung umgesetzt?

### Entscheidung
Separate Tabelle `prompt_versions` mit FK zu `prompts`:
- Jeder Insert eines Prompts erstellt automatisch eine erste Version
- Zukünftig: Edit könnte neue Version erstellen
- History ist nachvollziehbar

### Konsequenzen
- ✅ Flexibel für zukünftige Versionshistorie
- ✅ Cascade-Delete bedeutet: Prompt löschen → Versionen weg
- 📝 Migration vom Modell schwierig, daher gute Initialisierung wichtig

---

Alle Entscheidungen wurden unter Berücksichtigung des MVP-Fokus und der Lernziele getroffen.
