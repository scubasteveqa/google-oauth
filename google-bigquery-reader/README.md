# Google BigQuery Reader

Shiny Python app that runs a BigQuery SQL query via Posit Connect's OAuth integration and renders the results as a `DataGrid`.

The app exchanges the inbound `Posit-Connect-User-Session-Token` for a Google access token via `connect.Client().oauth.get_credentials(token)`, then runs the query through `google-cloud-bigquery`.

## Required environment variables

| Variable           | Type    | Description                                                                                                                       |
| ------------------ | ------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `BIGQUERY_PROJECT` | string  | The GCP project ID used to bill the query. Must be a project the viewer has BigQuery permissions on.                              |


Credentials found in 1Password - Google OAuth Client (staging) 
