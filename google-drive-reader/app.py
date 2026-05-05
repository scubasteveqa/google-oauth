import os

import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from posit import connect
from shiny import reactive, render
from shiny.express import session, ui


FOLDER_ID = os.environ.get("FOLDER_ID", "")
PAGE_SIZE_RAW = os.environ.get("PAGE_SIZE", "100")
try:
    PAGE_SIZE = max(1, min(int(PAGE_SIZE_RAW), 1000))
except ValueError:
    PAGE_SIZE = 100


ui.page_opts(title="Google Drive Reader", fillable=True)


@reactive.calc
def session_token():
    return session.http_conn.headers.get("Posit-Connect-User-Session-Token")


@reactive.calc
def connect_client():
    return connect.Client()


@reactive.calc
def folder_listing():
    """Returns (DataFrame, info_dict). info_dict has 'folder_name' and optional 'error'."""
    info: dict[str, str | None] = {"folder_name": None, "error": None}
    if not FOLDER_ID:
        info["error"] = "FOLDER_ID environment variable is not set."
        return pd.DataFrame(), info
    token = session_token()
    if not token:
        info["error"] = (
            "No Posit-Connect-User-Session-Token header. Deploy to Connect with a "
            "Google Drive integration attached to this content."
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
        service = build("drive", "v3", credentials=google_creds, cache_discovery=False)
        try:
            meta = service.files().get(fileId=FOLDER_ID, fields="id,name,mimeType").execute()
            info["folder_name"] = meta.get("name")
        except Exception:
            pass

        rows: list[dict[str, object]] = []
        page_token: str | None = None
        while True:
            response = (
                service.files()
                .list(
                    q=f"'{FOLDER_ID}' in parents and trashed = false",
                    pageSize=PAGE_SIZE,
                    fields=(
                        "nextPageToken, files(id, name, mimeType, modifiedTime, "
                        "size, owners(emailAddress), webViewLink)"
                    ),
                    pageToken=page_token,
                )
                .execute()
            )
            for f in response.get("files", []):
                owners = f.get("owners", []) or []
                rows.append(
                    {
                        "name": f.get("name"),
                        "mimeType": f.get("mimeType"),
                        "modifiedTime": f.get("modifiedTime"),
                        "size": f.get("size"),
                        "owner": owners[0].get("emailAddress") if owners else None,
                        "id": f.get("id"),
                        "webViewLink": f.get("webViewLink"),
                    }
                )
            page_token = response.get("nextPageToken")
            if not page_token:
                break

        if not rows:
            info["error"] = f"Folder {FOLDER_ID} is empty or not accessible."
            return pd.DataFrame(), info
        return pd.DataFrame(rows), info
    except Exception as e:
        info["error"] = f"Drive API error ({type(e).__name__}): {e}"
        return pd.DataFrame(), info


with ui.card():
    ui.card_header("Status")

    @render.ui
    def status_display():
        df, info = folder_listing()
        items = [
            ui.tags.li(f"Folder ID (env FOLDER_ID): {FOLDER_ID or '<unset>'}"),
            ui.tags.li(f"Page size (env PAGE_SIZE): {PAGE_SIZE}"),
            ui.tags.li(f"Session token present: {bool(session_token())}"),
        ]
        if info.get("folder_name"):
            items.append(ui.tags.li(f"Resolved folder name: {info['folder_name']}"))
        if info.get("error"):
            return ui.div(
                ui.tags.ul(*items),
                ui.div(
                    ui.tags.strong("Error: "),
                    ui.tags.pre(info["error"]),
                    class_="alert alert-danger",
                ),
            )
        items.append(ui.tags.li(f"Loaded {len(df)} files"))
        return ui.tags.ul(*items)


with ui.card(full_screen=True):
    ui.card_header("Folder contents")

    @render.data_frame
    def grid():
        df, _ = folder_listing()
        return render.DataGrid(df, filters=True, height="600px")
