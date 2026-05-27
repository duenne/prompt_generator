import importlib
import sys
import types
from dataclasses import dataclass


@dataclass
class FakeError:
    message: str


@dataclass
class FakeResponse:
    error: object = None
    data: list | None = None


class FakeTableChain:
    def __init__(self, response: FakeResponse):
        self._response = response

    def insert(self, _payload):
        return self

    def select(self, _fields):
        return self

    def order(self, _field, desc=False):
        return self

    def limit(self, _n):
        return self

    def execute(self):
        return self._response


class ImportSafeSupabase:
    def table(self, _name):
        return FakeTableChain(FakeResponse(error=None, data=[]))


class RecordingSupabase:
    def __init__(self, prompt_response: FakeResponse, version_response: FakeResponse | None = None):
        self.prompt_response = prompt_response
        self.version_response = version_response or FakeResponse(error=None, data=[{"id": 1}])
        self.calls: list[tuple[str, dict]] = []

    def table(self, table_name: str):
        return RecordingTableChain(self, table_name)


class RecordingTableChain:
    def __init__(self, parent: RecordingSupabase, table_name: str):
        self.parent = parent
        self.table_name = table_name

    def insert(self, payload):
        self.parent.calls.append((self.table_name, payload))
        return self

    def execute(self):
        if self.table_name == "prompts":
            return self.parent.prompt_response
        if self.table_name == "prompt_versions":
            return self.parent.version_response
        return FakeResponse(error=None, data=[])


class DummyStreamlit:
    def __init__(self):
        self.session_state = {}
        self.sidebar = types.SimpleNamespace(selectbox=lambda *args, **kwargs: "Prompt-Generator")

    def selectbox(self, _label, options=None, **kwargs):
        if options:
            return options[0]
        return ""

    def button(self, *args, **kwargs):
        return False

    def text_input(self, *args, **kwargs):
        return ""

    def text_area(self, *args, **kwargs):
        return ""

    def columns(self, n):
        return tuple(DummyStreamlit() for _ in range(n))

    def __getattr__(self, _name):
        return self

    def __call__(self, *args, **kwargs):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def __iter__(self):
        return iter([])

    def __bool__(self):
        return False


def load_app_module():
    fake_supabase_mod = types.SimpleNamespace(create_client=lambda *_args, **_kwargs: ImportSafeSupabase())
    sys.modules["streamlit"] = DummyStreamlit()
    sys.modules["supabase"] = fake_supabase_mod

    if "app" in sys.modules:
        del sys.modules["app"]

    return importlib.import_module("app")


def test_save_prompt_writes_prompt_and_initial_version_success() -> None:
    app_module = load_app_module()
    supabase = RecordingSupabase(prompt_response=FakeResponse(error=None, data=[{"id": 7}]))
    app_module.supabase = supabase

    success, message = app_module.save_prompt("  Titel  ", "  Prompt text  ")

    assert success is True
    assert "erfolgreich" in message
    assert supabase.calls == [
        ("prompts", {"title": "Titel", "prompt": "Prompt text"}),
        (
            "prompt_versions",
            {"prompt_id": 7, "prompt": "Prompt text", "version_note": "Erste Version"},
        ),
    ]


def test_save_prompt_returns_error_when_prompts_insert_fails() -> None:
    app_module = load_app_module()
    supabase = RecordingSupabase(
        prompt_response=FakeResponse(error=FakeError("insert failed"), data=None)
    )
    app_module.supabase = supabase

    success, message = app_module.save_prompt("Titel", "Prompt")

    assert success is False
    assert "insert failed" in message
    assert len(supabase.calls) == 1
    assert supabase.calls[0][0] == "prompts"


def test_save_prompt_returns_error_when_prompt_id_missing() -> None:
    app_module = load_app_module()
    supabase = RecordingSupabase(prompt_response=FakeResponse(error=None, data=[{}]))
    app_module.supabase = supabase

    success, message = app_module.save_prompt("Titel", "Prompt")

    assert success is False
    assert "Prompt-ID" in message
    assert len(supabase.calls) == 1


def test_save_prompt_returns_error_when_version_insert_fails() -> None:
    app_module = load_app_module()
    supabase = RecordingSupabase(
        prompt_response=FakeResponse(error=None, data=[{"id": 11}]),
        version_response=FakeResponse(error=FakeError("version insert failed"), data=None),
    )
    app_module.supabase = supabase

    success, message = app_module.save_prompt("Titel", "Prompt")

    assert success is False
    assert "version insert failed" in message
    assert [name for name, _ in supabase.calls] == ["prompts", "prompt_versions"]


class QuerySupabase:
    def __init__(self, query_response: FakeResponse):
        self.query_response = query_response
        self.calls: list[tuple[str, str]] = []

    def table(self, table_name: str):
        return QueryTableChain(self, table_name)


class QueryTableChain:
    def __init__(self, parent: QuerySupabase, table_name: str):
        self.parent = parent
        self.table_name = table_name

    def select(self, fields):
        self.parent.calls.append((self.table_name, f"select:{fields}"))
        return self

    def order(self, field, desc=False):
        self.parent.calls.append((self.table_name, f"order:{field}:{desc}"))
        return self

    def limit(self, n):
        self.parent.calls.append((self.table_name, f"limit:{n}"))
        return self

    def execute(self):
        self.parent.calls.append((self.table_name, "execute"))
        return self.parent.query_response


def test_list_prompts_returns_data_on_success() -> None:
    app_module = load_app_module()
    rows = [{"id": 1, "title": "A", "prompt": "P"}]
    supabase = QuerySupabase(query_response=FakeResponse(error=None, data=rows))
    app_module.supabase = supabase

    result = app_module.list_prompts()

    assert result == rows
    assert ("prompts", "select:*") in supabase.calls
    assert ("prompts", "order:id:False") in supabase.calls


def test_list_prompts_returns_empty_list_without_client_or_on_error() -> None:
    app_module = load_app_module()
    app_module.supabase = None
    assert app_module.list_prompts() == []

    app_module.supabase = QuerySupabase(query_response=FakeResponse(error=FakeError("db error"), data=None))
    assert app_module.list_prompts() == []


def test_test_supabase_connection_missing_client_and_missing_table() -> None:
    app_module = load_app_module()

    app_module.supabase = None
    success, message = app_module.test_supabase_connection()
    assert success is False
    assert "nicht initialisiert" in message

    table_missing_error = types.SimpleNamespace(code="PGRST205", message="Could not find the table")
    app_module.supabase = QuerySupabase(query_response=FakeResponse(error=table_missing_error, data=None))
    success, message = app_module.test_supabase_connection()
    assert success is False
    assert "existiert nicht" in message


def test_create_tables_handles_missing_database_url() -> None:
    app_module = load_app_module()
    app_module.DATABASE_URL = ""

    success, message = app_module.create_tables()

    assert success is False
    assert "DATABASE_URL ist nicht gesetzt" in message


def test_create_tables_success_with_mocked_psycopg2() -> None:
    app_module = load_app_module()
    app_module.DATABASE_URL = "postgres://test"

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def execute(self, ddl):
            assert "CREATE TABLE IF NOT EXISTS prompts" in ddl
            assert "CREATE TABLE IF NOT EXISTS prompt_versions" in ddl

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def cursor(self):
            return FakeCursor()

    fake_psycopg2 = types.SimpleNamespace(connect=lambda _url: FakeConnection())
    original = sys.modules.get("psycopg2")
    sys.modules["psycopg2"] = fake_psycopg2
    try:
        success, message = app_module.create_tables()
    finally:
        if original is None:
            del sys.modules["psycopg2"]
        else:
            sys.modules["psycopg2"] = original

    assert success is True
    assert "wurden angelegt" in message
