# ADR: hosting of the mother app (Session 11)

**Status:** proposed by Sang, 03/11/2026. The team confirms it at review.

## Decision

Host the app as one **Render Web Service, free plan**, from `render.yaml`, in the Singapore region.

## Why

The three selection questions of Session 11:

1. **Does the product have its own backend that must run continuously?** Yes: FastAPI renders every page and holds the session. So a web service, not serverless functions.
2. **Is it built with Streamlit or Gradio?** No.
3. **Does it need a database?** Yes, but SQLite built from the schema and the seed is enough for sample data, so the app needs no separate database service.

Rejected: Vercel and Netlify (no state kept between calls, so SQLite does not fit). Railway and Fly.io (Session 11 does not recommend them, as they now offer mainly trial plans). ngrok and Cloudflare Tunnel (the link stops when the laptop is off, and a tunnel does not pass the session).

## Trade-offs we accept

| Trade-off | Effect | Why it is acceptable now |
|---|---|---|
| The service sleeps after 15 idle minutes | The first visit waits about a minute | Open the link a few minutes before a demo |
| The disk is not kept | Each deploy or restart returns to the sample data; uploaded diary photos are lost | There is only invented data, and a clean start suits a demo |
| One sample mother for all visitors | Testers see each other's reports | Enough for Session 11 and 12; to review before the street tests of Session 13 |
| One shared staff password (D-82) | Not real accounts | Real staff sign-in stays open (spec-CLI §10 Q11) |
| Requests run one at a time | A slow chatbot call delays others | Traffic is a few testers, and one SQLite connection stays safe |

## Limits

No real patient data may be entered on the public link. The medical text is sample data, Pending SME (D-81), and the home screen says so.
