from django.shortcuts import render, redirect

from .forms import ConnectionForm
from .model_utils import SQLModel
from .db_utils import test_connection, get_schema, execute_query


def connect_view(request):
    if request.method == "POST":
        form = ConnectionForm(request.POST)
        if form.is_valid():
            creds = form.cleaned_data
            ok, error = test_connection(creds)
            if ok:
                request.session["db_creds"] = creds
                request.session["chat_history"] = []
                return redirect("query")
            form.add_error(None, f"Connection failed: {error}")
    else:
        form = ConnectionForm()
    return render(request, "connect.html", {"form": form})


def disconnect_view(request):
    request.session.flush()
    return redirect("connect")


def query_view(request):
    creds = request.session.get("db_creds")
    if not creds:
        return redirect("connect")

    try:
        schema = get_schema(creds)
    except Exception:
        request.session.flush()
        return redirect("connect")

    chat_history = request.session.get("chat_history", [])
    current_result = None

    if request.method == "POST":
        if request.POST.get("action") == "clear":
            request.session["chat_history"] = []
            request.session.modified = True
            return redirect("query")

        nl_query = request.POST.get("nl_query", "").strip()
        selected_tables = request.POST.getlist("selected_tables")
        active_schema = (
            {t: schema[t] for t in selected_tables if t in schema} or schema
        )

        sql_query = None
        columns, rows, error = [], [], None

        try:
            sql_query = SQLModel.get_instance().generate_sql(nl_query, active_schema)
            if not sql_query.strip().upper().startswith("SELECT"):
                raise ValueError("Only SELECT queries are allowed for safety.")
            columns, rows = execute_query(creds, sql_query)
        except Exception as e:
            error = str(e)

        # Keep session-stored history lean (no rows — too large).
        chat_history.append({
            "nl_query": nl_query,
            "sql_query": sql_query,
            "error": error,
        })
        # Cap history at 20 messages to avoid bloated sessions.
        request.session["chat_history"] = chat_history[-20:]
        request.session.modified = True

        current_result = {
            "nl_query": nl_query,
            "sql_query": sql_query,
            "columns": columns,
            "rows": [list(r) for r in rows],
            "error": error,
            "row_count": len(rows),
        }

    context = {
        "schema": schema,
        "db_name": creds["db_name"],
        "db_host": creds["db_host"],
        "chat_history": chat_history,
        "current_result": current_result,
    }
    return render(request, "query.html", context)
