# Ferry

**Code-first schema and safe content deployment for Umbraco 17.**

Ferry keeps schema in your code and moves content between sites, such as development, staging and live:

- **Code-first schema.** `SchemaBuilder` declares data types, templates, media types and document types in Umbraco
  migrations, run once per environment. Keys derive from aliases, so schema is identical everywhere. An existing site
  can download its schema as one key-preserving migration. See [code-first schema](docs/code-first-schema.md).
- **Generated migrations.** Development backoffice schema edits become C# migrations you commit; other environments
  run them at startup and report drift. See [generated migrations](docs/code-first-schema.md#generated-migrations).
- **Content-only sites.** With `Ferry:Full:ContentOnly`, a site rejects any transfer that would change its schema and
  lists what to deploy first.
- **Reviewed transfers.** Send and Get (Push and Pull in the API) list every create, update and move and need an
  owner-bound approval before applying. Schema, media, references and blocks travel with the content.
- **Deployment workflow.** Per-user queue, offline `.ferry.zip` packages, import at startup, snapshots and restore
  points, user-group permissions for delegated editors.
- **Extensible.** Custom property editors and package data (Skybrud redirects, Umbraco Forms, your own package) can
  join transfers. See [extending Ferry](docs/extending.md).
- **Safe on real sites.** One operation at a time across load-balanced instances (database lease). Indexing and caches
  pause during large imports. Each apply writes a recovery journal.

**Documentation:** <https://imkeuri.github.io/ferry-umbraco/>. Ferry needs no other synchronisation tool or file export.

> **Free to use, closed source.** Free for any site, including commercial work, under the
> [Ferry Freeware License](LICENSE).

**Status: experimental, pre-1.0.** Tested on Umbraco **17.6.2** and .NET 10. See [supported scope](docs/supported-scope.md).

## Quick start

```sh
dotnet add package Ferry.Umbraco
dotnet add package Ferry.Backoffice
```

```csharp
builder.CreateUmbracoBuilder()
    .AddBackOffice()
    .AddWebsite()
    .AddComposers()
    .AddFerryUmbracoFull()
    .Build();
```

Configuration goes in a `Ferry` section of `appsettings.json`; see [Host integration](#host-integration).

## Using the backoffice

Ferry.Backoffice adds a **Ferry** workspace under **Settings › Synchronisation**:

| Tab | Use |
| --- | --- |
| **Overview** | Connected sites, *Send to another site*, *Get from another site* (whole site or chosen pages), recent activity. *Connect your first site* when none is connected. |
| **Sites** | Site status, the *Connect a site* wizard (paste a pairing code), and *Sites that can connect to this one* (create pairing codes, revoke access). |
| **Packages** | Export a `.ferry.zip` (chosen pages and media, or whole site), import one by dropping it on the page, create or restore snapshots. |
| **Advanced** | *Publish on another site*; danger zone with *Move to recycle bin on another site* and *Seed another site*. |

Content tree **Actions** offer *Send to…*, *Get from…*, *Add to queue* and (administrators) *Publish on another
site…*, each ending in a review ("4 new pages, 1 updated page", schema, move and template callouts, *Show details*).
Items always arrive as drafts. The top-bar **Ferry** button opens the queue (send all or download as a package) and
recent activity. The *Send with Ferry* and *Get with Ferry* group permissions control access, on top of
[delegated-editor grants](#delegated-editor-push).

## Supported and limits

**Supported:** invariant Content, Content variants and segments, selected MediaPicker3 references, segment-varying
scalar Media values, Content `UploadField` assets (draft with hash and byte checks; published as immutable
publish-time snapshots, failing closed when the snapshot is missing, corrupt or mismatched). Each capability and its
limits are listed in the [supported scope](docs/supported-scope.md).

**Limits:**

- Not yet covered: arbitrary `UploadField`/editor configurations, multi-node hosting, cross-browser, accessibility
  and production topologies.
- Unsupported: unknown/custom editors, user/member references. Not every Umbraco editor is supported.
- Templates must already exist at the destination; schema changes needing storage migration are blocked.
- Jobs and approvals are process-local; multi-node needs affinity and external coordination.

## Transfer model

- Stable GUID identities across sites; local numeric IDs may differ.
- Create/update/unchanged previews, dependency ordering, cyclic soft references.
- Whole-site or selected-tree transfer with prerequisite/reference closure (Full mode reads only that closure).
- Optional culture scope (Full mode): selected variants plus invariant values; other destination variants untouched.
  Bound into the approval; peers without the capability are rejected. New scoped content needs the default and
  mandatory cultures.
- Approvals are bound to source and destination fingerprints: edits to incoming entities or prerequisites need a fresh
  preview, unrelated edits do not.
- Peers negotiate a versioned, authenticated capability declaration first; incompatible formats fail closed.
- Native draft saves, whatever the source publication state.
- Media is verified by SHA256 and length. An optional probe skips bytes the peer already has.
- Culture-varying Media (Full mode). Umbraco 17.6.2 drops Media culture names on read, so Ferry keeps them in its own
  table; native APIs and the backoffice do not show them after a restart.
- [Administrator pull](#administrator-pull), and optional metadata-only Browse and name-only BrowseSearch.
- Destination-only entities are kept. No implicit deletion or rollback.
- On failure, completed and possibly touched entities are reported separately.

Adapters:

- `AddFerryUmbraco()`: invariant TextBox/TextArea drafts on matching preinstalled schemas.
- `AddFerryUmbracoFull()`: writes through Umbraco's services, so other packages' save handlers run. Requires an
  `ISyncAssetStore`. Editor/storage changes to existing shared data types are blocked. Re-export older experimental
  manifests.

The BackOffice package has its own composer, independent of the transport switch and adapter.

## Host integration

Register the adapter, then configure transport explicitly:

```csharp
builder.Services.AddFerryTransport(new SyncTransportOptions
{
    BearerToken = tokenFromYourSecretProvider
});
builder.Services.AddFerryFileAssets(privateAssetDirectory);
builder.Services.AddFerryFileRecovery(privateRecoveryDirectory);
// After building/configuring the Umbraco application:
app.MapFerry();
```

For named peers with per-operation permissions, use the reload-aware registration:

```csharp
builder.Configuration.AddEnvironmentVariables(); // or the host's managed secret provider
builder.Services.AddFerryTransportFromConfiguration(
    builder.Configuration.GetRequiredSection("Ferry"));
```

Set peer identity, revision and permitted operations in `Ferry:Peers`, with tokens from the secret provider (for
example `Ferry__Peers__0__Tokens__0`). See the [peer-policy contract](docs/research/peer-policy-design.md).

- Bearer secrets: random, at least 32 characters. No defaults are provided.
- Keep asset and recovery storage outside public static-file directories.
- In the sample, endpoints are off by default and `Ferry:Mode` is `DraftText` (default) or `Full`.

### Access keys from the backoffice only

Access keys from Settings › Ferry › Sites (*Create pairing code*) are also receiver credentials. A receiver using only
those needs no token or placeholder peer: `AddFerryTransportFromConfiguration` (or `AddFerryTransport`) accepts an
empty `Ferry` section when an `ISyncManagedPeerSource` is registered. With neither, the host refuses to start.

### Getting past host authentication

`/ferry/v1` does its own authentication. Basic auth or an IP/SSO gateway in front will block it. For
Umbraco basic auth, add the shared-secret header (`Umbraco:CMS:BasicAuth:SharedSecret`) to requests on that path
before `UseUmbraco()`; otherwise exclude the path in the gateway.

### TLS terminated by a proxy

The receiver rejects plain HTTP. When TLS ends at a proxy (Azure Container Apps, App Service, Front Door, nginx),
forward the scheme:

```csharp
builder.Services.Configure<ForwardedHeadersOptions>(options =>
{
    options.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
    options.KnownIPNetworks.Clear(); // only when the ingress is the sole way in; otherwise list its network
    options.KnownProxies.Clear();
});
// First in the pipeline:
app.UseForwardedHeaders();
```

### Where state is kept

| State | Storage | Survives redeploy / new replica? |
| --- | --- | --- |
| Servers and access keys | `cmsFerryServer`, `cmsFerryAccessKey` | Yes. |
| Secrets in those rows | ASP.NET Data Protection | Only with a persisted, shared key ring (e.g. `PersistKeysToAzureBlobStorage`); otherwise keys stop working after a redeploy and a warning is logged. |
| Peer cache | Memory, 30 seconds | Revoked keys stop working on other instances within 30 seconds. |
| Operation history, submissions, snapshots, restore points | `cmsFerryOperation`, `cmsFerrySubmission`, `cmsFerrySnapshot` | Yes. |
| Previews and batch sessions | Memory | No. See [Hosting requirements](#hosting-requirements). |
| Receiver approvals (push, publication, tree trash) | Memory, per process | No. See [Hosting requirements](#hosting-requirements). |
| Staged assets, recovery records | Directories given to `AddFerryFileAssets` / `AddFerryFileRecovery` | Only on persistent storage. |

`cmsFerry*` tables are created whenever the packages are installed, even with `Ferry:Enabled` or
`Ferry:Backoffice:Enabled` `false`. To remove Ferry: uninstall the packages, drop the
`cmsFerry*` tables, and delete `umbracoKeyValue` rows whose key starts with `Ferry.` or
`Umbraco.Core.Upgrader.State+Ferry.`.

### Hosting requirements

**Database.** Use SQL Server for production receivers. On SQLite with the default `Cache=Shared`, a burst of writes
(such as a large apply) can deadlock Umbraco's cache write with its background jobs, and every later request hangs. If
you must use SQLite, set `Cache=Private`.

**One warm instance.** Previews (15 minutes, single-use), batched push sessions (4 hours) and receiver approvals live
in memory and are lost on restart, scale-to-zero or a different instance. Both sites must run one warm instance:

- Azure Container Apps: minimum and maximum replicas 1.
- App Service and other load-balanced hosts: one instance, or session affinity for the source backoffice. The receiver
  must be a single instance; site-to-site calls carry no affinity cookie.

Otherwise apply returns `410 Gone` ("This preview has expired") and changes nothing.

## Protocol

Endpoints under `/ferry/v1` require HTTPS and bearer authentication; responses are not cached.

| Endpoint | Purpose |
| --- | --- |
| `GET /capabilities` | Peer protocol, adapter, entity, operation and limit support |
| `GET /manifest` | Export the complete supported snapshot |
| `POST /export` | Export selected roots, descendants and dependencies |
| `POST /browse` | One metadata-only page of Content or Media children (if Browse is registered) |
| `POST /browse/search` | One metadata-only name-search page (if BrowseSearch is granted) |
| `POST /preview` | Validate a manifest, return a plan |
| `POST /apply` | Revalidate the approved fingerprint and apply |
| `GET /assets/{hash}` | Stream an asset |
| `PUT /assets/{hash}?length=...` | Verify and stage an asset |
| `GET /operations` | List recovery operation summaries (if registered) |
| `GET /operations/{id}` | Operation outcome |
| `GET /operations/{id}/recovery` | Before-state recovery record |
| `POST /publication/preview` | Validate destination keys and cultures |
| `POST /publication/apply` | Publish only the approved selection |

HTTP 200 does not mean success: check `SyncPlan.IsValid` and `ExecutionResult.Status`. Errors: 401 authentication,
400 malformed, 413 oversized, 422 adapter capability. JSON requests default to 8 MiB; assets have a separate limit.

`SyncRemoteClient` calls one fixed HTTPS destination. `SyncTransferClient.PrepareAsync()` negotiates, exports, stages
assets and previews; `ApplyAsync()` is separate and rechecks the peer. Redirects are disabled. Configure only trusted
peers.

## Administrator pull

Requires `AllowPull: true` on the server-side connection. Endpoints under
`/umbraco/management/api/v1/ferry/pull`:

| Endpoint | Behaviour |
| --- | --- |
| `POST /preview` | Full site or 1–1000 typed roots; returns an owner-bound, expiring approval. |
| `POST /{id}/apply` | Consumes the approval, rechecks connection and capabilities, applies the frozen manifest with recovery journal. Never publishes, deletes, schedules or re-exports. |
| `POST /browse` | `Content` or `Media`, optional parent key, page size 1–100. Returns key, name, breadcrumb (last 16 ancestors, `…` if truncated), child presence, cultures. Never properties, entities, snapshots or bytes. |
| `POST /browse/search` | Name term 2–128 characters, no `%`, `_` or `[`; up to 50 per page, offset up to 10,000. Names only. |

Browse and search need source `Browse` and `Export` and local `Preview` and `Apply`; a source can grant `Browse`
alone. `BrowseSearch` is opt-in (`GET /capabilities?extensions=browse-search`). Content (not Media) can be scoped by
culture; see [transfer model](#transfer-model). Delegated Pull is draft-only, for granted groups within permitted
roots, cultures and Umbraco permissions.

## Delegated editor Push

Administrators can grant a user group a limited Push to one destination:

```json
{
  "Ferry": {
    "Backoffice": {
      "DelegatedEditors": [
        {
          "GroupAlias": "editors",
          "Direction": "Push",
          "ConnectionId": "Production",
          "ContentRootKeys": ["11111111-1111-1111-1111-111111111111"],
          "MediaRootKeys": ["22222222-2222-2222-2222-222222222222"],
          "RemoteContentRootKeys": [],
          "RemoteMediaRootKeys": [],
          "AllowedCultures": ["en-US"]
        }
      ]
    }
  }
}
```

- `GroupAlias`: the stored group alias, not the display name. `ConnectionId`: the configured destination key.
- `ContentRootKeys` / `MediaRootKeys`: roots members may send. `AllowedCultures`: variant values sent.
- Native `Read` permission is also required; grant and scope are rechecked at preview and apply. Anything missing,
  invalid or non-matching denies access.

Push preview takes legacy `contentRoots` or `roots: [{ kind: "Content" | "Media", key }]`: one of them, with 1–1000
unique keys, or an empty `contentRoots` for the whole site. Both sites must support every selected kind.

## Operational boundaries

- **Credentials.** The legacy bearer credential grants every operation; named peers can be limited and rotated, and
  reload with configuration (limits need a restart). Treat every receiver credential as an administrative secret.
- **Concurrency.** Fingerprints detect changes; they do not lock editors or replace authorization. The receiver
  serializes requests per process; external edits and multi-node writers need extra coordination.
- **Recovery.** Records keep before-state and known outcomes, not an atomic transaction or rollback. An interrupted
  write can leave partial changes: inspect the destination and preview again before retrying. No outcome record means
  completion is unknown. Recovery data contains site content; protect it.
- **Live impact.** Drafts are not published, but schema, media, hierarchy and sort changes can affect the live site.
- **Out of scope:** executable templates/scripts, account replication.

See [integration decisions](docs/umbraco-package-guide.md),
[supported scope and recovery limits](docs/supported-scope.md) and
[third-party notices](THIRD-PARTY-NOTICES.md).

## Help and feedback

- **Bugs:** [open an issue](https://github.com/imkeuri/ferry-umbraco/issues/new/choose) with Ferry and Umbraco
  versions, database and steps. Remove tokens, connection strings and passwords.
- **Questions and ideas:** [Discussions](https://github.com/imkeuri/ferry-umbraco/discussions).
- **Package or editor support:** use the *Package or editor support* issue form, or see
  [extending Ferry](docs/extending.md).
- **Security problems:** report [privately](https://github.com/imkeuri/ferry-umbraco/security/advisories/new), never
  in a public issue.
