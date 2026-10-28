# Named receiver peer policies

## Receiver contract

The receiver accepts an optional legacy `BearerToken`, which grants every operation, or named peers with their own
identity and operation scope. Either only authorizes receiver calls; neither grants Umbraco user, root or culture
permissions.

| Peer field | Meaning |
| --- | --- |
| `Id` | Stable identity. |
| `Tokens` | One to eight rotation tokens. |
| `Enabled` | On/off. |
| `Revision` | Policy version; advance on every change. |
| `AllowedOperations` | `Capabilities`, `Export`, `Preview`, `Apply`, `AssetRead`, `AssetWrite`, `PublicationPreview`, `PublicationApply`, `RecoveryRead`. Empty grants nothing. |

Tokens come from the host's secret provider (e.g. `Ferry__Peers__0__Tokens__0`), never source control:

```csharp
builder.Configuration.AddEnvironmentVariables(); // or the host's managed secret provider
builder.Services.AddFerryTransportFromConfiguration(
    builder.Configuration.GetRequiredSection("Ferry"));
```

```json
{
  "Ferry": {
    "Peers": [
      {
        "Id": "deployment-agent",
        "Enabled": true,
        "Revision": "2026-09-17",
        "AllowedOperations": [ "Capabilities", "Export", "Preview", "Apply" ]
      }
    ]
  }
}
```

- **Strict binding:** unknown fields, bad or comma-combined operation names, numeric enums and malformed shapes fail
  startup.
- **Live reload:** peers and the legacy token are re-read per request after a host reload; an invalid value fails
  closed. Parse failures and missed reloads are host concerns. Request and asset limits are startup-only.
- **Responses:** `Cache-Control: no-store` on every request reaching authentication; bad or revoked token `401`
  (`WWW-Authenticate: Bearer`); missing operation `403`.
- **Reauthorization** happens inside the operation gate before any read or write, so queued requests see revocation.

## Capabilities and approvals

- Named peers see the adapter declaration narrowed to their operations, with asset read and write separate, plus a
  policy fingerprint and approval-token limit.
- Their previews return an opaque envelope binding the fingerprint to peer id, policy hash, purpose (`transfer` or
  `publication`) and a 15-minute expiry, signed with a process-generated HMAC-SHA256 key.
- Apply checks all of these before any journal, store or write. Bad or stale envelopes return `410 Gone`; policy
  denials `403`. Legacy peers keep raw fingerprints.

| Decision | Consequence |
| --- | --- |
| Process-local key | Restart invalidates approvals; multi-node needs preview/apply affinity. |
| No replay ledger | Envelopes are not single-use; the backoffice prepared-transfer store stays single-use. |
| Revision in the hash | Token rotation keeps envelopes valid; reusing an old revision can revive one, so always advance it. |
| Fail closed over compatibility | Strict older clients may reject the new fields; upgrade both peers. |
