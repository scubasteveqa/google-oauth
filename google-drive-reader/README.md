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
