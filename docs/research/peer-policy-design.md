# Named receiver peer policies

## Implemented receiver contract

The receiver can authorize either an optional legacy `BearerToken` or named peers.
A named peer has a stable `Id`, one to eight rotation `Tokens`, an `Enabled` flag,
a `Revision`, and an explicit list of allowed operations. The allowed names are
`Capabilities`, `Export`, `Preview`, `Apply`, `AssetRead`, `AssetWrite`,
`PublicationPreview`, `PublicationApply`, and `RecoveryRead`. An empty list grants
no receiver operation.

The optional legacy token remains available for existing deployments and grants all
receiver operations. A named peer is the appropriate choice when a receiver needs
separate machine identities or operation scopes. This is receiver authorization only:
it does not grant Umbraco user-group, content-root, or culture permissions.

Use the host's secret provider and register the configuration section directly. For
example, the host may populate `Ferry__Peers__0__Tokens__0` through its
secret-provider integration before the application is built:

```csharp
builder.Configuration.AddEnvironmentVariables(); // or the host's managed secret provider
builder.Services.AddFerryTransportFromConfiguration(
    builder.Configuration.GetRequiredSection("Ferry"));
```

The corresponding non-secret configuration can contain peer identity and scope:

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

Do not put a token value in source-controlled configuration. Each peer object accepts
only `Id`, `Tokens`, `Enabled`, `AllowedOperations`, and `Revision`; unknown fields,
invalid operation names, comma-combined names, numeric enum values, and malformed
scalar/list shapes are rejected. Startup rejects invalid configuration. With
`AddFerryTransportFromConfiguration`, peer policy is read for each request
after the host has published a configuration reload. An invalid current policy value
fails closed and a corrected published configuration takes effect on the next
request. This does not detect a configuration-source parse failure or a missed host
reload notification; those are host configuration concerns. Request and asset limits
remain startup values; peer credentials and permissions, including the optional
legacy bearer token, are live-reloaded.

Every HTTPS request that reaches receiver authentication sends `Cache-Control: no-store`.
A missing, unknown, disabled, or revoked token returns `401` with
`WWW-Authenticate: Bearer`.
A recognized peer without the requested operation returns `403`. Protected work
reauthorizes after it enters the receiver's operation gate and before it reads a
snapshot, starts a journal record, publishes, or writes. A queued request therefore
observes permission or token revocation before it can access receiver state.

## Capabilities and approvals

Named peers receive the adapter declaration intersected with their allowed operations.
Asset read and asset write are independently represented; a legacy combined asset
capability is expanded only into directions the named peer is allowed to use. The
capability response includes a non-secret policy fingerprint and its approval-token
limit. Legacy peers retain the existing adapter declaration.

For named peers, transfer and publication previews return an opaque approval envelope
instead of the raw planner or publisher fingerprint. The envelope binds the raw
fingerprint to the peer id, the canonical hash of its id/revision/operations, the
purpose (`transfer` or `publication`), and a 15-minute expiry. It is protected by an
HMAC-SHA256 key generated for the receiver process. Apply validates the current
peer, policy hash, purpose, expiry, and MAC before any journal, store, publisher, or
write access. Bad or stale envelopes return `410 Gone` ProblemDetails ("This approval has expired"); a policy
denial remains `403`.
Legacy peers continue to use raw approval fingerprints.

The approval key is process-local. Restarting the receiver invalidates named-peer
approvals. Multi-node deployments need preview/apply affinity until a durable shared
approval protector exists. Envelopes are not single-use and do not provide a replay
ledger; the existing backoffice prepared-transfer store retains its separate
single-use behavior. Token rotation that preserves id, revision, and operations
retains an unexpired envelope. Operators must advance `Revision` for every policy
change: restoring the same id, revision, and operation set can make an unexpired
envelope valid again.

The additional capability fields can cause strict older clients to reject a new
receiver declaration. Upgrade both peers when adopting named policies; this is
deliberately fail-closed rather than a claim of wire compatibility with older strict
clients.

## Verification

The ordinary .NET suite currently has 191 passing tests: 74 Transport, 42 Core, 8
Backoffice, and 67 Umbraco adapter. The peer-policy coverage includes strict startup
and reload binding, exact expiry, queued permission and token revocation, envelope
purpose and policy-drift rejection before I/O, and directional asset capabilities.
The current real-site E2E set has 30 scenarios: 19 final-package consumer cases, 4
named-policy cases, 4 coexistence cases, 1 scoped-export case, and 2 legacy-capability
cases. Their run records and scope are in verification.
