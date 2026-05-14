# Google Sheets Reader

Shiny Python app that reads a Google Sheet via Posit Connect's OAuth integration and renders it as a `DataGrid` table.

The app exchanges the inbound `Posit-Connect-User-Session-Token` for a Google access token via `connect.Client().oauth.get_credentials(token)`, then calls the Google Sheets API directly with `google-api-python-client`.

## Required environment variables

| Variable    | Type    | Description                                                                                                                                       |
| ----------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SHEET_ID`  | string  | The spreadsheet ID — the long token between `/d/` and `/edit` in the sheet URL.                                                                   |

## Required environment variables
| Variable    | Type    | Description                                                                                                                                       |
| ----------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SHEET_GID` | integer | The numeric tab ID — the value of the `gid=` query param in the sheet URL. The app uses this to resolve the tab title before pulling row values. |

### Finding the values

A URL like:

```
https://docs.google.com/spreadsheets/d/yil3453452345r2345a2345ekkk34k4j4kj4sAsk/edit?gid=1234567890
                                       └────────────── SHEET_ID ──────────────┘          └ SHEET_GID ┘
```

gives `SHEET_ID=yil3453452345r2345a2345ekkk34k4j4kj4sAsk` and `SHEET_GID=1234567890`.
