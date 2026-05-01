import os

import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from posit import connect
from shiny import reactive, render
from shiny.express import session, ui


SHEET_ID = os.environ.get("SHEET_ID", "")
SHEET_GID_RAW = os.environ.get("SHEET_GID", "")
try:
    SHEET_GID: int | None = int(SHEET_GID_RAW) if SHEET_GID_RAW else None
except ValueError:
    SHEET_GID = None


ui.page_opts(title="Google Sheets Reader", fillable=True)


@reactive.calc
def session_token():
    return session.http_conn.headers.get("Posit-Connect-User-Session-Token")


@reactive.calc
def connect_client():
    return connect.Client()


@reactive.calc
def sheet_data():
    """Returns (DataFrame, info_dict). info_dict has 'tab_title' and optional 'error'."""
    info: dict[str, str | None] = {"tab_title": None, "error": None}
    if not SHEET_ID:
        info["error"] = "SHEET_ID environment variable is not set."
        return pd.DataFrame(), info
    if SHEET_GID is None:
        info["error"] = "SHEET_GID environment variable is not set or not an integer."
        return pd.DataFrame(), info
    token = session_token()
    if not token:
        info["error"] = (
            "No Posit-Connect-User-Session-Token header. Deploy to Connect with a "
            "Google Sheets integration attached to this content."
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
        service = build("sheets", "v4", credentials=google_creds, cache_discovery=False)
        meta = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
        target_title = None
        for s in meta.get("sheets", []):
            if s["properties"]["sheetId"] == SHEET_GID:
                target_title = s["properties"]["title"]
                break
        if not target_title:
            info["error"] = f"No tab with gid={SHEET_GID} in spreadsheet {SHEET_ID}."
            return pd.DataFrame(), info
        info["tab_title"] = target_title
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=SHEET_ID, range=target_title)
            .execute()
        )
        values = result.get("values", [])
        if not values:
            info["error"] = f"Tab '{target_title}' is empty."
            return pd.DataFrame(), info
        headers = values[0]
        rows = values[1:]
        padded = [row + [None] * (len(headers) - len(row)) for row in rows]
        truncated = [row[: len(headers)] for row in padded]
        return pd.DataFrame(truncated, columns=headers), info
    except Exception as e:
        info["error"] = f"Sheets API error ({type(e).__name__}): {e}"
        return pd.DataFrame(), info


with ui.card():
    ui.card_header("Status")

    @render.ui
    def status_display():
        df, info = sheet_data()
        items = [
            ui.tags.li(f"Spreadsheet ID (env SHEET_ID): {SHEET_ID or '<unset>'}"),
            ui.tags.li(f"Target gid (env SHEET_GID): {SHEET_GID if SHEET_GID is not None else '<unset>'}"),
            ui.tags.li(f"Session token present: {bool(session_token())}"),
        ]
        if info.get("tab_title"):
            items.append(ui.tags.li(f"Resolved tab: {info['tab_title']}"))
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
    ui.card_header("Sheet contents")

    @render.data_frame
    def grid():
        df, _ = sheet_data()
        return render.DataGrid(df, filters=True, height="600px")
