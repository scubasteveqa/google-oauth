import os

import pandas as pd
from google.cloud import bigquery
from google.oauth2.credentials import Credentials
from posit import connect
from shiny import reactive, render
from shiny.express import session, ui


BIGQUERY_PROJECT = os.environ.get("BIGQUERY_PROJECT", "")
BIGQUERY_QUERY = os.environ.get("BIGQUERY_QUERY", "")
ROW_LIMIT_RAW = os.environ.get("ROW_LIMIT", "1000")
try:
    ROW_LIMIT = max(1, min(int(ROW_LIMIT_RAW), 100000))
except ValueError:
    ROW_LIMIT = 1000


ui.page_opts(title="Google BigQuery Reader", fillable=True)


@reactive.calc
def session_token():
    return session.http_conn.headers.get("Posit-Connect-User-Session-Token")


@reactive.calc
def connect_client():
    return connect.Client()


@reactive.calc
def query_results():
    """Returns (DataFrame, info_dict). info_dict has 'rows_returned' and optional 'error'."""
    info: dict[str, str | int | None] = {"rows_returned": None, "error": None}
    if not BIGQUERY_PROJECT:
        info["error"] = "BIGQUERY_PROJECT environment variable is not set."
        return pd.DataFrame(), info
    if not BIGQUERY_QUERY:
        info["error"] = "BIGQUERY_QUERY environment variable is not set."
        return pd.DataFrame(), info
    token = session_token()
    if not token:
        info["error"] = (
            "No Posit-Connect-User-Session-Token header. Deploy to Connect with a "
            "Google BigQuery integration attached to this content."
        )
        return pd.DataFrame(), info
    try:
        client = connect_client()
        creds_response = client.oauth.get_credentials(token)
        access_token = creds_response.get("access_token")
        if not access_token:
            info["error"] = (
                f"No access_token in credentials response. keys={list(creds_response.keys())}"
            )
            return pd.DataFrame(), info
    except Exception as e:
        info["error"] = f"OAuth credential exchange failed ({type(e).__name__}): {e}"
        return pd.DataFrame(), info
    try:
        google_creds = Credentials(token=access_token)
        bq_client = bigquery.Client(project=BIGQUERY_PROJECT, credentials=google_creds)
        job = bq_client.query(BIGQUERY_QUERY)
        df = job.result(max_results=ROW_LIMIT).to_dataframe()
        info["rows_returned"] = len(df)
        if df.empty:
            info["error"] = "Query returned no rows."
        return df, info
    except Exception as e:
        info["error"] = f"BigQuery API error ({type(e).__name__}): {e}"
        return pd.DataFrame(), info


with ui.card():
    ui.card_header("Status")

    @render.ui
    def status_display():
        df, info = query_results()
        items = [
            ui.tags.li(f"Billing project (env BIGQUERY_PROJECT): {BIGQUERY_PROJECT or '<unset>'}"),
            ui.tags.li(f"Row limit (env ROW_LIMIT): {ROW_LIMIT}"),
            ui.tags.li(f"Session token present: {bool(session_token())}"),
        ]
        if BIGQUERY_QUERY:
            items.append(
                ui.tags.li(
                    "Query: ",
                    ui.tags.code(
                        BIGQUERY_QUERY
                        if len(BIGQUERY_QUERY) <= 200
                        else BIGQUERY_QUERY[:200] + "…"
                    ),
                )
            )
        else:
            items.append(ui.tags.li("Query (env BIGQUERY_QUERY): <unset>"))
        if info.get("error"):
            return ui.div(
                ui.tags.ul(*items),
                ui.div(
                    ui.tags.strong("Error: "),
                    ui.tags.pre(info["error"]),
                    class_="alert alert-danger",
                ),
            )
        items.append(ui.tags.li(f"Loaded {len(df)} rows × {len(df.columns)} columns"))
        return ui.tags.ul(*items)


with ui.card(full_screen=True):
    ui.card_header("Query results")

    @render.data_frame
    def grid():
        df, _ = query_results()
        return render.DataGrid(df, filters=True, height="600px")
