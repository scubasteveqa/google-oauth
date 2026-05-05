# Google BigQuery Reader

Shiny Python app that runs a BigQuery SQL query via Posit Connect's OAuth integration and renders the results as a `DataGrid`.

The app exchanges the inbound `Posit-Connect-User-Session-Token` for a Google access token via `connect.Client().oauth.get_credentials(token)`, then runs the query through `google-cloud-bigquery`.

## Required environment variables

| Variable           | Type    | Description                                                                                                                       |
| ------------------ | ------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `BIGQUERY_PROJECT` | string  | The GCP project ID used to bill the query. Must be a project the viewer has BigQuery permissions on.                              |

### Example query

```sql
SELECT name, gender, SUM(number) AS total
FROM `bigquery-public-data.usa_names.usa_1910_2013`
WHERE state = 'TX'
GROUP BY name, gender
ORDER BY total DESC
LIMIT 50
```

The dataset can live in any project the viewer has access to; `BIGQUERY_PROJECT` only controls billing.

## Setting env vars on Posit Connect

1. Open the published content's settings panel → **Vars**.
2. Add `BIGQUERY_PROJECT`, `BIGQUERY_QUERY`, and optionally `ROW_LIMIT`.
3. Click **Deploy Changes**. Connect restarts the app with the new environment.

If any variable is missing, the status card will report it instead of failing inside the BigQuery client.

## Required Posit Connect setup

- A Google BigQuery OAuth integration exists on the same Connect server (template `bigquery`, with default scopes `https://www.googleapis.com/auth/bigquery https://www.googleapis.com/auth/bigquery.insertdata`).
- That integration is **attached to this content item** (Settings → Access → OAuth Integrations).
- The viewer's Google account has BigQuery Job User on `BIGQUERY_PROJECT` and Data Viewer on whatever tables the query references.

## Local development

```bash
export BIGQUERY_PROJECT=my-project
export BIGQUERY_QUERY="SELECT 1 AS one"
shiny run app.py
```

OAuth credential exchange requires a real `Posit-Connect-User-Session-Token` header, which only deployed Connect content receives — running locally will show the "no session token" error in the status card. Deploy to test the full flow.

## Deploy

```bash
rsconnect deploy shiny . \
  --server <connect-url> \
  --api-key <key> \
  --title "Google BigQuery Reader"
```
