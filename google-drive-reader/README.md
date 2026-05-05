# Google Drive Reader

Shiny Python app that lists the contents of a Google Drive folder via Posit Connect's OAuth integration and renders them as a `DataGrid`.

The app exchanges the inbound `Posit-Connect-User-Session-Token` for a Google access token via `connect.Client().oauth.get_credentials(token)`, then calls the Google Drive API directly with `google-api-python-client`.

## Required environment variables

| Variable    | Type    | Description                                                                                                          |
| ----------- | ------- | -------------------------------------------------------------------------------------------------------------------- |
| `FOLDER_ID` | string  | The Drive folder ID — the segment after `/folders/` in the folder URL.                                               |
| `PAGE_SIZE` | integer | Optional. Files per Drive API page (max 1000). Defaults to 100. The app paginates through all pages regardless.      |

### Finding the folder ID

A URL like:

```
https://drive.google.com/drive/folders/1AbC2dEfGhIjKlMnOpQrStUvWxYz
                                       └─────── FOLDER_ID ───────┘
```

gives `FOLDER_ID=1AbC2dEfGhIjKlMnOpQrStUvWxYz`.

## Setting env vars on Posit Connect

1. Open the published content's settings panel → **Vars**.
2. Add `FOLDER_ID` (and optionally `PAGE_SIZE`).
3. Click **Deploy Changes**. Connect restarts the app with the new environment.

If `FOLDER_ID` is missing or the folder isn't readable by the viewer, the status card will report the error instead of failing inside the Drive API call.

## Required Posit Connect setup

- A Google Drive OAuth integration exists on the same Connect server (template `drive`, with default scope `https://www.googleapis.com/auth/drive`).
- That integration is **attached to this content item** (Settings → Access → OAuth Integrations).
- The viewer's Google account has read access to the target folder.

## Local development

```bash
export FOLDER_ID=1AbC2dEfGhIjKlMnOpQrStUvWxYz
shiny run app.py
```

OAuth credential exchange requires a real `Posit-Connect-User-Session-Token` header, which only deployed Connect content receives — running locally will show the "no session token" error in the status card. Deploy to test the full flow.

## Deploy

```bash
rsconnect deploy shiny . \
  --server <connect-url> \
  --api-key <key> \
  --title "Google Drive Reader"
```
