# Ferry

**Code-first schema and safe content deployment for Umbraco 17.**

Ferry keeps schema in your code and moves content between sites, such as development, staging and live:

- **Code-first schema.** `SchemaBuilder` lets you state data types, templates, media types and document types in
  ordinary Umbraco migrations. Each migration runs once per environment and is reviewed like any other code. Keys are
  derived from aliases, so every environment gets identical schema. An existing site can adopt code-first by
  downloading its schema as one migration that keeps every key. See [code-first schema](docs/code-first-schema.md).
- **Content-only sites.** With `Ferry:Full:ContentOnly` set, a site accepts content and rejects any transfer that would
  change its schema, and the error lists what to deploy first.
- **Reviewed transfers.** Send and Get (Push and Pull in the API) show a summary and every create, update and move
  before anything is applied, and nothing is applied without an owner-bound approval. Schema, media files,
  references and blocks travel with the content.
- **Deployment workflow.** A per-user transfer queue, offline `.csync.zip` packages, import at startup, snapshots and
  restore points, and Umbraco user-group permissions for delegated editors.
- **Extensible.** Custom property editors and package data (Skybrud redirects, Umbraco Forms, or your own package)
  can join transfers. See [extending Ferry](docs/extending.md).
- **Safe on real sites.** One operation runs at a time across load-balanced instances (database lease). Indexing and
  caches pause during large imports. Each apply writes a recovery journal.

Ferry works alongside uSync: it uses the open-source `uSync.Core` serializers, and uSync files are optional.

> **Free to use, closed source.** Ferry is free for any site, including commercial work, under the
> [Ferry Freeware License](LICENSE); its source is not published.
>
> **Not affiliated with uSync or Jumoo.** uSync and uSync Complete are products of Jumoo. Ferry is an independent
> product and contains no commercial uSync code.

**Status: experimental, pre-1.0.** Tested on Umbraco **17.6.2** and .NET 10. See [supported scope](docs/supported-scope.md)
for exactly what is verified and the [validation record](docs/validation-record.md) for evidence.

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

Configuration lives under a `Ferry` section in `appsettings.json`; [Host integration](#host-integration) covers
transport, connections and options.

## Using the backoffice

Ferry.Backoffice adds a **Ferry** workspace under **Settings › Synchronisation** (next to uSync when it is installed):

| Tab | What it is for |
| --- | --- |
| **Overview** | Your connected sites and their last activity, *Send to another site* and *Get from another site* (whole site or chosen pages), and recent activity. With no site connected it offers *Connect your first site*. |
| **Sites** | Connected sites with a status check, the *Connect a site* wizard (paste a pairing code), and *Sites that can connect to this one*, where you create pairing codes and revoke access. |
| **Packages** | Export a `.csync.zip` for chosen pages and media or the whole site, import one by dropping it on the page, and create or restore snapshots. |
| **Advanced** | *Publish on another site*, and a danger zone with *Move to recycle bin on another site* and *Seed another site*. |

Editors work from the content tree. **Actions** on a page or media item offer *Send to…*, *Get from…*, *Add to queue* and
(for administrators) *Publish on another site…*. Each opens a side panel that ends in a review: a summary such as
"4 new pages, 1 updated page", callouts for schema changes, moves and templates, and the full list behind *Show
details*. Items always arrive as drafts. The **Ferry** button in the top bar opens the queue (send everything together
or download it as a package) and your recent activity.

Who may send or get is set per user group with the *Send with Ferry* and *Get with Ferry* permissions, on top of the
delegated-editor grants described below.

## Upgrading from CommunitySync

Ferry was released as **CommunitySync**. Upgrading is a rename, and site data is kept:

- **Packages:** `CommunitySync.*` becomes `Ferry.*` (`Ferry.Core`, `Ferry.Transport`, `Ferry.Umbraco`,
  `Ferry.Backoffice`).
- **Code:** namespaces `CommunitySync.*` become `Ferry.*`, and type and method names drop the prefix in the same way,
  for example `AddCommunitySyncUmbracoFull()` becomes `AddFerryUmbracoFull()` and `CommunitySyncFullOptions` becomes
  `FerryFullOptions`. A search and replace of `CommunitySync` with `Ferry` in your host code is enough.
- **Configuration:** rename the `CommunitySync` section to `Ferry` when convenient. Until then, a site without a
  `Ferry` section keeps reading `CommunitySync`; a site never uses both.
- **Unchanged:**
  - database tables (`cmsCommunitySync*`), migration state and protected connection secrets
  - the user-group permission verbs `CommunitySync.Push` / `CommunitySync.Pull`
  - the wire protocol (`/community-sync/v1`, transfer formats, headers), so Ferry and CommunitySync sites still
    transfer to each other
  - the package format (`.csync.zip`)

## Evidence summary

The current suite has 668 ordinary .NET tests and real two-site E2E suites for each module. The
[supported scope](docs/supported-scope.md) lists them per capability. Earlier checkpoints are recorded below.

The experimental Full v5 checkpoint had 433/433 ordinary .NET tests, a fresh
exact-NuGet fixture-consumer package install using an isolated Docker SDK, a packaged
Full transfer/publication run (22/22), and an exact-package two-site source-version
suite with Published `UploadField` coverage (6/6), including native new-content
`SaveAndPublish`, exact bytes, and unchanged replay. It also includes a culture-varying partial republish and a clean
exact-NuGet two-site culture-Media Push/Pull run (2/2). SQLite and SQL
Server-target runs cover the restart path. The suite asserts
different en-US/fr-FR image bytes, captions, durable culture-name metadata, replay
to `Unchanged`, and a destination process restart. These results are in ignored
`artifacts/` and are local evidence, not remote CI; see the
[validation record](docs/validation-record.md) for paths and commands. Delegated Pull
is draft-only and requires an explicit valid grant.

Earlier-package Backoffice browser evidence ran three native suites against two
disposable sites in a Playwright MCP image container: 19/19 passed using the browse
peer policy (`artifacts/e2e/browser-snapshot-final/results.json`). It predates the
current production commit and covers bounded native dashboard, transfer, publication, history and
remote-browse flows; it is not cross-browser, accessibility, hosted-CI, or production
topology validation.

The verified subset includes invariant Content, supported Content variants and
segments, selected relational MediaPicker3 references, Segment-varying scalar Media
values, draft-source Content `UploadField` assets with hash and byte verification,
and bounded Published-source Content `UploadField` assets captured as immutable,
verified publish-time snapshots. Published export uses only the matching saved-content
snapshot and fails closed when it is absent, corrupt, or does not match the published
raw value. Preexisting publications without a snapshot fail closed. Native
new-content `SaveAndPublish` captures immutable bytes before Umbraco assigns its
version, then binds them to the assigned `PublishedVersionId` after publication. A bounded
SQL Server source E2E verifies the snapshot table, primary key, and saved snapshot
row. The source-version E2E also covers an en-US-only republish that preserves an
untouched fr-FR immutable snapshot after its mutable file is overwritten.
The current package install, source-version, and Full transfer/publication evidence
is recorded in the validation record. The host sandbox still denies access to the SDK
trusted-root PEM, so the clean install used an isolated Docker SDK rather than the
host restore environment.
Arbitrary UploadField/editor configurations, multi-node hosting, hosted CI, and
cross-browser coverage are pending; unknown/custom
editors and user/member references remain unsupported. This does not establish
support for every Umbraco editor or parity with any commercial product. Templates must already exist at the destination;
schema changes that require storage migration are blocked. Durable jobs and approval
state are process-local, so multi-node operation needs affinity and external
coordination. See the [supported scope](docs/supported-scope.md) and
[acceptance checklist](docs/acceptance-checklist.md) for exact boundaries.

## Transfer model

- Stable GUID identities across sites with different local numeric IDs.
- Create/update/unchanged previews, dependency ordering and cyclic soft references.
- Whole-site or selected-tree transfer with prerequisite/reference closure.
- Full-mode selected exports resolve their source closure before reading content
  or staging media; selected preview/apply also reads only destination entities in
  that closure and external direct prerequisites. Adapters without scoped
  destination support retain full-snapshot validation.
- Full mode optionally scopes Content variant transfer to selected cultures: it includes
  selected variant names and values plus invariant values, and preserves unselected
  destination variants. The culture scope is bound into the manifest and approval
  fingerprint. A Pull peer without the scoped-culture capability fails closed.
  Creating scoped content requires the default and mandatory cultures.
- Selected destination fingerprints and before-state recovery records use that
  bounded snapshot. Incoming-entity or prerequisite edits stale the approval;
  unrelated destination edits do not. Shared-schema collision checks still run.
- Peers negotiate a versioned, authenticated capability declaration before export,
  asset staging or destination writes. Incompatible transfer formats fail closed.
- Preview fingerprints bound to source and destination snapshots; stale approval
  requires a fresh preview.
- Native draft saves, independently of source publication state.
- Streaming media assets are verified by SHA256 and length before application. An
  optional authenticated, bounded, capability-gated availability probe lets Push, Pull
  and the generic client skip repeat network byte transfer when the peer already has
  the verified staged asset. Older peers fall back to full transfer; target media is
  still re-exported and staged locally during planning, so this saves network bytes,
  not local export work. Cache eviction fails safely.
- Full mode transfers the tested culture-varying Media shape: culture names, scalar
  captions, and distinct culture file descriptors. Because Umbraco 17.6.2 drops
  Media culture names on a fresh native read, Ferry stores approved names by
  Media GUID and canonical culture in its own migration-owned table. That preserves
  Ferry transfer semantics, but does not make the names appear in native
  Umbraco APIs or the Backoffice after a restart.
- An administrator can opt in to a draft-only pull from a configured remote source,
  with typed roots, dependency closure, asset verification and
  local recovery journaling.
- An optional, metadata-only remote Browse capability lists one bounded page of
  direct Content or Media children for a configured pull source.
- An optional BrowseSearch capability finds Content or Media by **name only**
  within that same configured and authorized remote scope; it returns the same
  metadata-only page shape as Browse.
- Destination-only entities are preserved. No implicit deletion or rollback.
- Completed and potentially touched entities are reported separately on failure.

Two adapters are available. `AddFerryUmbraco()` supports invariant
TextBox/TextArea drafts with matching preinstalled schemas.
`AddFerryUmbracoFull()` is standalone. It uses the open-source `uSync.Core` serializers and
value mappers internally (`AdduSyncCore()`), retains guarded native content/media writes,
and never installs the uSync backoffice. A site that also installs uSync keeps it as a
separate product: uSync registers itself, and its configured save handlers can export
Ferry's changes to its normal folders. Full mode requires an `ISyncAssetStore`.
See the documented supported editors and verified scenarios above. Existing shared
data type editor/storage migrations are blocked; declared source storage is
preserved. Older experimental manifests without this metadata must be re-exported.

The installed BackOffice package also has a native Umbraco composer, so its base
services can activate independently of Ferry's transport switch or chosen
adapter. Configure base-uSync export/import behavior through its own settings.
Our guarded draft path does not invoke the generic uSync import pipeline or invent
its import-origin notifications. See [the integration contract](docs/research/core-usync-integration.md).

## Build and test

Install .NET SDK 10.0.201 (see `global.json`), then run:

```sh
dotnet restore Ferry.slnx
dotnet test Ferry.slnx -m:1
```

The normal test runner works. The repository also contains a
two-site sample and a real-site E2E launcher in
`scripts/e2e/run.py`. Fixture credentials and databases belong in ignored
`artifacts/`; do not reuse them for deployed sites.

No public package has been published. Broad layout, accessibility, cross-browser,
and production-topology acceptance remains pending. See
[validation](docs/validation-record.md) for the latest local evidence and its limits.

## Host integration

Register the selected Umbraco adapter, then configure transport explicitly:

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

For operation-scoped named peers, load the token through the host's secret provider
and use the reload-aware registration:

```csharp
builder.Configuration.AddEnvironmentVariables(); // or the host's managed secret provider
builder.Services.AddFerryTransportFromConfiguration(
    builder.Configuration.GetRequiredSection("Ferry"));
```

Set peer identity, revision and permitted operation names in `Ferry:Peers`;
provide each token through the secret provider, such as
`Ferry__Peers__0__Tokens__0`. See the [peer-policy contract](docs/research/peer-policy-design.md)
for the allowed operation names, reload behavior and approval lifecycle.

Supply a random bearer secret of at least 32 characters. Keep asset/recovery
storage outside public static-file directories. Endpoints are disabled by default
in the sample. `Ferry:Mode` selects `DraftText` (default) or `Full` there.
No default deployment credentials are provided.

### Access keys from the backoffice only

When Ferry.Backoffice is installed, the access keys created under Settings › Ferry › Sites (*Create pairing code*) are receiver
credentials too. A receiver whose only credentials are those keys needs no configured token or placeholder peer:
`AddFerryTransportFromConfiguration` (or `AddFerryTransport`) accepts an empty `Ferry`
section when an `ISyncManagedPeerSource` is registered, and the host refuses to start when there is neither.

### Getting past host authentication

The receiver path `/community-sync/v1` authenticates every call itself (HTTPS plus a bearer token). Anything in
front of it that challenges the request first - Umbraco basic auth on lower environments, an IP or SSO gateway -
turns another site's call into a login page or a 401 before Ferry sees it. Let that path through: for
Umbraco basic auth, add its shared-secret header (`Umbraco:CMS:BasicAuth:SharedSecret`) to requests on that path
before `UseUmbraco()`, or exclude the path in the gateway.

### TLS terminated by a proxy

The receiver rejects plain HTTP. When TLS ends at a load balancer or container ingress (Azure Container Apps, App
Service, Front Door, nginx), forward the original scheme so the request is seen as HTTPS:

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

| State | Storage | Survives a redeploy or new replica? |
| --- | --- | --- |
| Servers and access keys (backoffice) | Umbraco database, tables `cmsCommunitySyncServer` and `cmsCommunitySyncAccessKey` | Yes. A `connections.json` from 0.1.1 or earlier is imported once at startup and renamed `.migrated`. |
| Secrets inside those rows | Encrypted with ASP.NET Data Protection | Only if the key ring is persisted and shared, for example `PersistKeysToAzureBlobStorage`. Otherwise keys stop authenticating after a redeploy and a warning is logged. |
| Peer cache | Memory, 30 seconds | A key revoked on one instance stops authenticating on the others within 30 seconds. |
| Operation history, durable submission mappings, snapshots and restore points | Umbraco database, tables `cmsCommunitySyncOperation`, `cmsCommunitySyncSubmission` and `cmsCommunitySyncSnapshot` (package bytes included) | Yes. The `App_Data/CommunitySync` folders from 0.1.1 or earlier are imported once at startup and renamed `.migrated`. |
| Reviews (previews) and batch sessions | Memory | No. See [Hosting requirements](#hosting-requirements). |
| Receiver approvals (push, publication, tree trash) | Memory, keyed to the process | No. See [Hosting requirements](#hosting-requirements). |
| Staged assets and recovery records | The directories passed to `AddFerryFileAssets` / `AddFerryFileRecovery` | Only on persistent storage. |

Ferry creates its tables (`cmsCommunitySync*`) at startup whenever its packages are installed, even when `Ferry:Enabled`
or `Ferry:Backoffice:Enabled` is `false`. A site that only serves transfers still uses the lease table
(`cmsCommunitySyncLease`), and the full adapter keeps media culture names and published asset snapshots in its own
tables. To remove Ferry from a site completely, uninstall the packages, then drop the `cmsCommunitySync*` tables and
delete the `umbracoKeyValue` rows whose key starts with `CommunitySync.` or `Umbraco.Core.Upgrader.State+CommunitySync.`.

### Hosting requirements

**Database.** Use SQL Server for sites that receive transfers in production. On SQLite, a burst of writes (a large
apply, for example) can deadlock Umbraco's own end-of-request cache write with its background jobs under the default
`Cache=Shared` connection string; every later request then waits. If a site must run on SQLite, use `Cache=Private`
in its connection string, as Ferry's own test sites do.

Previews, batch sessions and the receiver's approvals are held in process memory. A preview lasts 15 minutes (a
batched push session 4 hours) and is used once. It is lost when the site restarts, scales to zero, or the apply
request reaches a different instance than the preview did. Both sites in a transfer must therefore run one warm
instance:

- Azure Container Apps: minimum replicas 1 (no scale-to-zero) and maximum replicas 1.
- App Service or other load-balanced hosts: one instance, or session affinity for the source's backoffice. The
  receiver must still be a single instance: site-to-site calls carry no affinity cookie.

Otherwise apply answers `410 Gone` ("This preview has expired") and nothing is changed; the dashboard asks for a
new preview. A receiver that loses its approval answers `410` too, and the source shows the same message.

## Protocol

Endpoints under `/community-sync/v1` require HTTPS and bearer authentication.
Responses disable caching.

| Endpoint | Purpose |
| --- | --- |
| `GET /capabilities` | Describe authenticated peer protocol, adapter, entity, operation and effective-limit support |
| `GET /manifest` | Export the complete supported snapshot |
| `POST /export` | Export selected roots, descendants and required dependencies |
| `POST /browse` | Return one metadata-only page of direct Content or Media children when the optional Browse reader is registered |
| `POST /browse/search` | Return one bounded metadata-only name-search page when BrowseSearch is explicitly granted |
| `POST /preview` | Validate a manifest and return a plan |
| `POST /apply` | Revalidate the approved fingerprint and apply |
| `GET /assets/{hash}` | Stream an asset |
| `PUT /assets/{hash}?length=...` | Verify and stage an asset |
| `GET /operations` | List recovery operation summaries when registered |
| `GET /operations/{id}` | Inspect an operation outcome |
| `GET /operations/{id}/recovery` | Retrieve its before-state recovery record |
| `POST /publication/preview` | Validate explicit destination keys and cultures |
| `POST /publication/apply` | Publish only the separately approved selection |

Inspect `SyncPlan.IsValid` and `ExecutionResult.Status`; HTTP 200 alone does not
mean an import succeeded. Authentication failures return 401, malformed requests
400, oversized requests 413 and known adapter capability errors 422. JSON defaults
to an 8 MiB request limit; assets have a separate configurable limit.

`SyncRemoteClient` offers capability/export/preview/apply calls against one fixed
HTTPS destination. `SyncTransferClient.PrepareAsync()` negotiates capabilities,
exports a selection, stages assets and previews; `ApplyAsync()` is separate and
rechecks the peer declaration. Redirects are disabled. Only configure trusted peers.
For deployments behind a TLS proxy, configure trusted forwarded headers in the host.

## Administrator pull

The management API can pull a draft transfer from a configured source only
when that server-side connection has `AllowPull: true`. `POST
/umbraco/management/api/v1/community-sync/pull/preview` accepts a full-site
choice or 1–1000 typed roots and returns an owner-bound, expiring
approval. `POST /umbraco/management/api/v1/community-sync/pull/{id}/apply`
consumes that approval, rechecks the connection and capabilities, then applies the
frozen manifest through the local store and recovery journal. It neither publishes,
deletes, schedules, nor re-exports remotely during apply.

Full-mode Pull can optionally scope variant data by culture. It includes names and
values for selected variants plus invariant values, leaves unselected destination
variants unchanged, and binds the scope into the frozen manifest and approval
fingerprint. The peer must advertise the scoped-culture capability; an older Pull
peer is rejected before export. Creating a culture-variant item within a scoped
transfer requires the default and all mandatory cultures. The Content transfer modal
exposes an optional localized culture-code input. Leaving
it empty means all cultures; review displays the selected scope. Media transfer does
not offer culture scope. Browser coverage verifies this bounded interaction, not broad
visual, accessibility or cross-browser behavior.

`POST /umbraco/management/api/v1/community-sync/pull/browse` accepts a configured
`AllowPull` source, `Content` or `Media`, an optional parent key, and page/page-size
(1–100). It performs the same pull compatibility preflight as selection: source
`Browse` and `Export`, local `Preview` and `Apply`, matching transfer format, and
the requested kind. The source receiver itself grants `Browse` independently of
`Export`, so a browse-only peer may call `/community-sync/v1/browse` without export
access. Its response contains only key, name, a human-readable bounded breadcrumb,
child presence, and cultures; it never returns properties, serialized entities,
snapshots, or media bytes. A breadcrumb resolves at most the trailing 16 ancestors
and begins with `…` if earlier ancestors were omitted.

`POST /umbraco/management/api/v1/community-sync/pull/browse/search` uses the same
connection, authorization, compatibility and delegated-scope checks. It accepts a
2–128-character name term, rejects SQL wildcard characters (`%`, `_`, `[`), and
returns pages of at most 50 matches with a maximum 10,000-item offset. Search is
name-only: it never searches property values or serializes entities. `BrowseSearch`
is an opt-in protocol extension (`GET /capabilities?extensions=browse-search`) so
older capability clients do not need to parse the new operation value.

The administrator Browse API drives native Content/Media send and receive actions
and a paged remote selector. Native publication selection, administrator operation
history, and limited delegated editor Push are also available. Delegated Pull is
available to explicitly granted groups for permitted roots and cultures, subject to
native Umbraco permissions. It creates drafts only. Search and field-level
differences are implemented within their documented bounds. Three native Backoffice
suites passed 19/19 against two packaged disposable sites in the Playwright MCP image
container, with a browse-authorized peer. Broad layout, accessibility, cross-browser
and production-topology acceptance remains pending.

## Delegated editor Push

Administrators may grant a named Umbraco user group a limited Push to one
configured destination. Add explicit grants under `Ferry:Backoffice`:

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

`GroupAlias` is the persisted Umbraco group alias, not its display name;
`ConnectionId` must match the configured destination key. Local root keys are
the Content and Media roots members may send, and `AllowedCultures` limits
variant values included in the transfer. Delegated Push also checks native
Umbraco `Read` permission and rechecks the grant and scope through preview and
apply. Missing, invalid, or non-matching grants deny access by default.

Push preview keeps the legacy `contentRoots` array for compatible callers and also
accepts `roots: [{ kind: "Content" | "Media", key }]`. A selected request supplies
exactly one selector with 1–1000 unique nonempty keys; a full-site request accepts
only the legacy empty `contentRoots` array. The source and destination must both
advertise every selected kind before source export begins.

## Operational boundaries

The optional legacy receiver bearer credential grants all receiver operations. Named
receiver peers can instead be limited to explicit operations and rotated tokens;
their credentials and policy reload after the host publishes a new configuration
snapshot, while request and asset limits stay fixed until restart. Treat every
receiver credential as an administrative secret. Backoffice operator authorization is a separate layer.
Fingerprints detect snapshot changes; they do not lock all CMS editors or replace
authorization. The receiver serializes requests within its process; external CMS
edits and multi-node writers require additional coordination.

Recovery records preserve before-state and known outcomes. They are not an atomic
transaction or automatic rollback; an interrupted write can leave partial changes.
Reinspect the destination and obtain a new preview before retrying. Missing outcome
records mean completion is unknown. Recovery data contains site content and must
be protected accordingly.

Draft content transfer does not infer publication. Schema, media, hierarchy and
sort changes can affect live rendering independently of content publication.
Executable templates/scripts, account replication and commercial product branding
are outside scope; installed template assignments use stable keys.

See [integration decisions](docs/umbraco-package-guide.md),
[supported scope and recovery limits](docs/supported-scope.md),
[public API findings](docs/usync-api-findings.md), and
[third-party notices](THIRD-PARTY-NOTICES.md). Ferry is proprietary freeware ([license](LICENSE));
uSync.Core is an unmodified MPL-2.0 dependency. No commercial uSync.Complete code
or binaries are included.
