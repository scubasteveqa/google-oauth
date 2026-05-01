# Google Sheets Reader

Shiny Python app that reads a Google Sheet via Posit Connect's OAuth integration and renders it as a `DataGrid` table.

The app exchanges the inbound `Posit-Connect-User-Session-Token` for a Google access token via `connect.Client().oauth.get_credentials(token)`, then calls the Google Sheets API directly with `google-api-python-client`.

## Required environment variables

| Variable    | Type    | Description                                                                                                                                       |
| ----------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SHEET_ID`  | string  | The spreadsheet ID — the long token between `/d/` and `/edit` in the sheet URL.                                                                   |
| `SHEET_GID` | integer | The numeric tab ID — the value of the `gid=` query param in the sheet URL. The app uses this to resolve the tab title before pulling row values. |

### Finding the values

A URL like:

```
https://docs.google.com/spreadsheets/d/1Yr7iGqaFFtKfcg5gJR1fwjMcmoCW-CK6NW_91u1sAsk/edit?gid=780868077
                                       └────────────── SHEET_ID ──────────────┘          └ SHEET_GID ┘
```

gives `SHEET_ID=1Yr7iGqaFFtKfcg5gJR1fwjMcmoCW-CK6NW_91u1sAsk` and `SHEET_GID=780868077`.

The first tab in a spreadsheet has `gid=0`.

## Setting env vars on Posit Connect

1. Open the published content's settings panel → **Vars**.
2. Add `SHEET_ID` and `SHEET_GID` with the values from the sheet URL.
3. Click **Deploy Changes**. Connect restarts the app with the new environment.

If either variable is missing or `SHEET_GID` isn't a valid integer, the app's status card will report which one is wrong instead of failing inside the Sheets API call.

## Required Posit Connect setup

- A Google Sheets OAuth integration exists on the same Connect server (template `sheets`, with default scopes `https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive`).
- That integration is **attached to this content item** (Settings → Access → OAuth Integrations).
- The viewer's Google account has read access to the target spreadsheet.

## Local development

```bash
export SHEET_ID=1Yr7iGqaFFtKfcg5gJR1fwjMcmoCW-CK6NW_91u1sAsk
export SHEET_GID=780868077
shiny run app.py
```

OAuth credential exchange requires a real `Posit-Connect-User-Session-Token` header, which only deployed Connect content receives — running locally will show the "no session token" error in the status card. Deploy to test the full flow.

## Deploy

```bash
rsconnect deploy shiny . \
  --server <connect-url> \
  --api-key <key> \
  --title "Google Sheets Reader"
```
