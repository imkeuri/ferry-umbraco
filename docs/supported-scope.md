# Supported scope and validation

The tested CMS baseline is Umbraco 17.6.2 on .NET 10. Support for another major is
not implied by the package name. The experimental Full v5 checkpoint has 433/433
ordinary .NET tests, a fresh exact-NuGet fixture-consumer package install using an
isolated Docker SDK, a packaged Full transfer/publication run (22/22), and a clean exact-NuGet two-site culture-Media
Push/Pull run (2/2). SQLite and SQL Server-target runs cover the v5 culture case:
names retained in Ferry's durable store, captions, distinct en-US/fr-FR
file bytes, unchanged replay, and a fresh target process. Commands and artifact paths are in the
[validation record](validation-record.md). These files are ignored local artifacts,
not CI evidence; CI evidence is pending. No run establishes commercial uSync
Complete parity.

| Capability | Evidence/status |
| --- | --- |
| Invariant draft text, hierarchy and stable identities | Real two-site tests |
| Existing live content receiving draft changes | Real two-site tests |
| Missing document/data types and compositions | Real two-site tests |
| Language creation and en-US/fr-FR draft values | Real two-site tests |
| Standard image media, new media types, scalar metadata and relational MediaPicker3 references | Full v4 Full/Full real-site test (`run-d95a28499b02`): relational picker identities map to destination Media keys; arbitrary relational editors are not implied |
| Segment-varying scalar Media values | Full v4 Full/Full real-site test (`run-19664d3bb671`) for TextBox values, invariant values, case-varied segment identities and unchanged replay. Arbitrary segmented editors are not implied. |
| Tested culture-varying Media names, captions and files | Exact-NuGet Full Push/Pull E2E 2/2 (`run-d96fcf3e9db4`) and SQL Server-target restart E2E 2/2 (`run-7cc1d7cd178d`): culture-specific en-US/fr-FR captions and distinct PNG bytes, durable Ferry culture-name metadata, repeat `Unchanged`, and target process restart. Umbraco 17.6.2 still returns native culture names as `null` after a fresh Media read, so the names are not displayed by native APIs/Backoffice. |
| Content UploadField assets | Draft-source transfer has verified descriptors and exact destination bytes. Published-source support is bounded to immutable, content-addressed publish-time snapshots: the matching `PublishedVersionId`, property/culture/segment and raw value must resolve to verified bytes or export fails closed. Exact-package two-site source-version E2E 6/6 (`artifacts/e2e/run-8fdee911be35/results.json`) proves same-path A/B isolation, native new-content `SaveAndPublish` capture before `VersionId` assignment then durable published-version binding, exact bytes, repeat `Unchanged`, missing-snapshot rejection before writes, and an en-US-only republish that carries immutable fr-FR bytes forward after the mutable fr-FR path is overwritten. Preexisting publications without a snapshot fail closed. The fresh exact-NuGet fixture-consumer install passed through an isolated Docker SDK (`artifacts/package-install/native-published-docker-20260925/result.json`) after the host sandbox denied access to its trusted-root PEM. Exact-package SQL Server source E2E 4/4 (`artifacts/e2e/run-148ef4ea5e5e/results.json`) verifies one saved snapshot row and `PK_cmsCommunitySyncPublishedContentAsset`; SQL Server target culture-Media E2E 2/2 (`artifacts/e2e/run-923dbb295bb3/results.json`) verifies table/PK creation with zero snapshot rows as expected. Arbitrary culture-varying UploadField configurations, multi-node hosting, hosted CI, and production topology are untested. |
| Optional asset-availability optimization | Authenticated bounded extension-gated probe verifies staged hash/length; Push/Pull/generic client skip repeat network bytes; old peers fall back; target media remains locally re-exported/staged during planning; cache eviction safely falls back |
| Rich-text local links and embedded images | Real two-site tests; native legacy-link normalization |
| Reciprocal content pickers | Real two-site tests |
| Nested Block List content/settings and schema closure | Real two-site tests |
| Block Grid, Multinode Treepicker and Multi URL Picker references | Full/Full E2E `editors` 3/3 (`run.py --mode Full --suite editors`). Values are mapped by base-uSync mappers. Each case selects its referenced entities: a document picked inside a Block Grid block plus the grid's element and data types, MNTP documents and media, and Multi URL Picker document and media links. The stored destination value is identical; a media link's read-time `url` is the destination's own media path. An external link is kept, and a repeat push is `Unchanged`. Block Grid areas, nested grids and Single Block are not covered. |
| Selected subtree including referenced entities | Real two-site tests |
| Full-site Dictionary Item synchronization | NuGet consumer E2E 1/1. Full-site only; the selected Content/Media experience is unchanged. Preserves stable GUID identity, parent hierarchy, translations and language dependencies. Moves and deletion are unsupported; deleting a destination translation is rejected. The `dictionary-item` capability is opt-in, so older peers reject the unsupported kind. System audit identity uses `Umbraco SuperUserKey`. No commercial parity claim. |
| Scoped destination preview/apply and recovery before-state | Package E2E 1/1 (`run-ae4d8657cce4`); bounded snapshot covers selected closure and external direct prerequisites; unrelated target edits do not stale approval; unsupported adapters use full snapshot; journal default limit is 64 MiB per record |
| Repeated import without changes or duplicates | Real two-site tests |
| Explicit existing Content/Media tree moves | Full/Full NuGet consumer Push/Pull E2E 3/3. Target enables `Ferry:Full:AllowExistingTreeMoves`; administrator Push/Pull preview requests `allowMoves: true`. Default remains false. Native Content/Media transfer modals and Settings dashboard expose the opt-in; Chromium suite passed 16/16. Preview shows old/new paths, descendant count, publication impact and ordinary field changes; the approval freezes the affected destination subtree and publication state. Native move carries destination-only descendants. Delegated editor moves remain denied. Deletion and automatic publication are excluded. |
| Explicit destination Content/Media tree trash | Implemented as a separate, receiver-only administrator operation. The Full destination must enable `Ferry:Full:AllowExistingTreeTrash` (default false), and the peer needs separate `TrashPreview` and `TrashApply` grants. The caller supplies 1–100 unique, non-overlapping destination roots; omission from a transfer is never trash intent and the recycle bin cannot be emptied. Preview reports each full subtree path, descendant count and published-descendant count, and freezes the branch, ancestors and publication state. Apply rechecks that state and uses Umbraco's native recycle bin. Recycled and root-level nodes, and Content branches containing publication schedules, are rejected to prevent unsafe or later automatic publication. The operation writes a correlated journal/recovery record; it is evidence for manual inspection and recovery, not automatic rollback or restoration of published versions. FINAL2 package E2E passed 3/3 in `artifacts/e2e/run-fe728d8adbe5/results.json`. |
| Scheduled destination and schema identity conflicts | Rejected before writes in real tests |
| Content default and named-segment values | Real two-site tests |
| Existing installed template assignments | Real two-site tests; template files and hierarchies are not transferred |
| Explicit culture publication and mandatory-language protection | Real two-site tests |
| Published source-version selection | Exact-package source-version E2E 6/6 (`artifacts/e2e/run-8fdee911be35/results.json`), including native new-content `SaveAndPublish` and an en-US-only republish that carries the untouched fr-FR UploadField snapshot into the new published version. For selected variant content, Published transfers the current `PublishedCultures`, including each culture's name, template and published value for each segment. Nonempty published UploadField values require an exact immutable publish-time snapshot and fail closed otherwise. Effective culture scope is bound to those published cultures; drafts in unselected destination cultures persist. Selecting a culture that is unpublished at the source rejects. Draft remains the default, and destination publication is separate. Peers without the advertised version capability reject the request. No commercial parity claim is made. |
| Optional Full-mode culture-scoped transfer | Package E2E: Full transfer/publication 22/22 and admin Pull 4/4; selected variant names/values and invariant values transfer, unselected destination variants persist, scope is frozen with manifest/fingerprint, old Pull peers fail closed, scoped creates require default and mandatory cultures; Content modal culture-code input/default-all/review scope verified in Docker Chromium 12/12; Media offers no culture scope |
| Administrator preview/apply and approval ownership | Real Management API tests |
| Authenticated peer capabilities and Full/Draft format rejection | Two real-site capability scenarios |
| Named receiver peer operations, reload fail-closed behavior and approval envelopes | Ordinary Transport tests and 4 prior installed-package real-site named-policy scenarios |
| Administrator opt-in draft pull from a configured source | Three final NuGet consumer scenarios; Astra review found no P1/P2 |
| Remote Content/Media Browse and BrowseSearch | Configured remote roots, including nested roots, appear in a virtual paged list; delegated child navigation and search require exact ancestry/direct-child scope proofs. Search is name-only, metadata-only and bounded. |
| Update field comparison | Bounded Content/Media field differences in administrator Push/Pull previews; only known scalar editors reveal values, unavailable editors are marked, and receiver preview requires a current Export grant for target values |
| Typed Media push selection | Preceding-package real-site regression; destination kind preflight occurs before export |
| Base-uSync file exports, handler configuration, mapper closure and cancellation | Four focused real-site scenarios |
| Settings dashboard, transfer, publication and history | Three earlier-package native Backoffice suites passed 19/19 against two disposable sites in a Playwright MCP image container using a browse-authorized peer (`artifacts/e2e/browser-snapshot-final/results.json`); they predate the current production commit. |
| Broad dashboard layout and interactive browser behavior | Bounded native flows have earlier-package 19/19 browser evidence; broad layout, accessibility, cross-browser and production-topology acceptance remain open. |
| Native publication selection | Included in the packaged 19/19 native browser run; final package smoke and publication/history real-site scenario also passed. |
| Administrator operation history | Included in the packaged 19/19 native browser run; backend and real-site publication/history evidence also passed. |
| Opt-in durable Backoffice Push and local Pull | An administrator can select durable Push during review when the destination advertises `durable-transfer-jobs` for its authenticated `Apply` peer; the receiver advertises it only with its private file-job store and recovery journal. Push rechecks destination capability, configuration and current administrator access before one bounded admission POST. Opt-in local Pull (`EnableDurableLocalPull`) uses a separate `LocalPull` job kind and owner binding. At admission and before worker execution it rechecks the configured source, bearer credential fingerprint, current access/grant and native Umbraco permissions. Staged Media assets are preflighted at both points and later consumed through independently verified streams; each asset remains limited to 100 MiB. Owner and job kind isolate Push receiver credentials from local Pull users. Both paths persist owner-bound idempotency admission and expose receipt/status recovery; the same owner/key/request returns the original receipt and a changed request conflicts. Accepted work continues in the background after the browser stops waiting. Durable Push remains unavailable to delegated Push and publication; durable Pull is available only where the current Pull authorization, grant and native permissions allow it. |
| Delegated editor Push | One configured connection; exact group alias; local Content/Media roots; allowed cultures; native Umbraco Read checks; package and one real-site scenario passed. The group also needs the `CommunitySync.Push` user-group permission on each sent document, granular or as a default; media uses the group default. A grant without the verb is denied (403), and the real-site case for this passed. |
| Delegated editor Pull | Latest package real-site case: explicit valid Pull grant, existing local root, permitted remote root/culture and native permission; draft-only; full-site prohibited; schema changes denied. The group also needs the `CommunitySync.Pull` user-group permission on the updated items and existing create parents, granular or as a default; media uses the group default. |

Ferry is a standalone package. Full transfer uses the public `uSync.Core` schema
serializers and value mappers (`AdduSyncCore()`) and retains native Umbraco draft saves;
it never installs the uSync backoffice, and its packages do not depend on it (the pack
check enforces this). Its backoffice lives in Settings → Synchronisation → Ferry. Where
a site also installs uSync, uSync registers itself and its normal save handlers perform
configured exports of Ferry's saves without a global pause or fabricated uSync import
events (`base-usync` suite). No commercial package implementation is included. Schema and
media changes are applied to the destination's live definitions/files; content
publication is a separate operation. Preserve a site/database backup appropriate
to your hosting environment when operating on a real site.

## Selected transfers and operational limits

Full mode implements `IScopedSyncExportStore`: a nonempty root selection resolves
its source closure before serializing content/schema or opening media files.
Unrelated source content and media are excluded from this path. Full mode also
implements `IScopedSyncDestinationStore`: selected preview/apply reads existing
destination entities in that closure and any external direct prerequisites, without
serializing unrelated destination content or media. Adapters without either optional
capability retain the full snapshot path.
Looking up a Language root by its portable key may enumerate serializer-derived
language identities because those keys differ from native CMS language GUIDs.

Selected destination preview/apply fingerprints that bounded destination snapshot.
Edits to an incoming entity or its external prerequisite invalidate approval;
unrelated destination edits do not. Schema alias collisions and non-destructive
shared-schema checks still run for every incoming schema during preview and again
at apply. Invalid entities inside the selected source closure also continue to
reject the transfer.

An optional asset-availability extension lets a peer report, through an authenticated
bounded probe, whether its staging store already contains the expected hash and length.
Push, Pull and generic typed clients skip repeat network GET/PUT bytes only when that
capability is advertised and the staged asset verifies. Older peers receive the normal
full transfer. Full descriptors remain in the manifest, approval fingerprint and
recovery records. Target media is still exported and staged locally during planning;
this optimization saves network bytes, not local export work. Cache eviction causes a
safe full transfer.

For selected transfers, recovery records keep the before-state from the same bounded
destination snapshot. The optional recovery journal remains limited to 64 MiB per
record by default; it does not provide atomic rollback. Full-snapshot behavior remains
for adapters that do not implement the optional scoped destination capability.

Full mode can optionally limit Content variant transfer to selected cultures. The frozen
manifest carries the scope and the approval fingerprint covers it. The transfer
includes selected variant names and values plus invariant values, while preserving
destination variants outside the selection. A Pull peer that does not advertise this
capability is rejected before export. Creating a scoped culture-variant item requires
the default and all mandatory cultures. The Content transfer modal provides an optional localized culture-code input; empty
means all cultures, and review shows the selected scope. Media transfer does not offer
culture scope. The 12/12 browser run verifies these bounded interactions, not full UI
parity.

The selected closure includes required ancestors, schemas and referenced entities.
Those dependencies can be planned as updates, not only creations. Review the full
plan rather than assuming that only the explicitly selected branch will change.

An administrator can opt into an existing Content or Media parent change by setting
`allowMoves: true` on a Push or Pull preview. The Full destination must explicitly
enable `Ferry:Full:AllowExistingTreeMoves` and advertise the negotiated
`existing-tree-move` capability. Approval binds the move choice and target branch
state; applying stale approval rejects before mutation. A native move carries the
entire existing subtree, including destination-only descendants. It can affect a
published path, but transfer still does not request publication. The Content/Media
transfer modals and Settings dashboard expose a default-off move toggle.

Tree trash is deliberately separate from transfer reconciliation. An administrator
selects one to 100 explicit, unique Content or Media roots on the destination; roots
may not overlap, may not already be recycled, and may not be top-level roots. The
Full destination must set `Ferry:Full:AllowExistingTreeTrash` to true, which
is false by default. The receiver exposes separate `TrashPreview` and `TrashApply`
peer-policy operations, so a peer permitted to transfer, browse, or preview another
operation is not thereby permitted to trash. Delegated editor grants do not authorize
tree trash.

Preview shows each selected root's path, the complete descendant impact and the
number of published descendants. Its 15-minute, owner-bound, single-use approval
freezes the selected branch, its ancestors and relevant publication state; a changed,
missing, moved, or otherwise unsafe branch causes apply to reject as stale before a
native recycle-bin move. Content with a publication schedule anywhere in the selected
branch is rejected because it could publish later. The operation never infers trash
from a source omission, never uses delete-missing semantics, and never empties the
Umbraco recycle bin.

Before applying, the receiver records the bounded before-state in its tree-trash
journal and returns the correlated operation ID with the outcome. That record supports
manual investigation and host-specific recovery after cancellation, interruption or
partial completion. It is not an atomic rollback and does not automatically restore
prior published versions, files, or a whole site. Inspect the destination recycle bin
and the correlated journal record before retrying an unknown outcome.

Peers expose an authenticated, no-store capability declaration for protocol/schema
version, adapter identity, supported kinds, operations and effective limits. A
transfer checks it before source export or asset staging, and rechecks it before
apply. Full and DraftText use distinct transfer formats, so they cannot transfer
content to one another. Publication has its own advertised operations and approval.

Source-scoped selection, bounded destination planning reads, capability negotiation
and optional Full-mode culture-scoped transfer are implemented. The Content transfer
modal exposes optional culture scope; Media does not. Further planning-time media
optimization to avoid local re-export remains roadmap work.

Published source-version selection is a distinct Full-mode option. For variant
Content, the source's current `PublishedCultures` determine the effective culture
scope: each published culture transfers its name, template and published value for
each segment. Draft values in destination cultures outside that scope persist. A
selected culture that is not published at the source rejects the request. Full-site
selection omits unpublished nodes and fails closed if an omitted unpublished
ancestor is required by a selected published node. Draft is the default source
version. A Published source version is applied as a destination draft; making it live
requires the separate destination publication workflow. The version capability is
negotiated before export, so peers that do not advertise it reject Published requests.
Final exact-package evidence: source-version 6/6 in
`artifacts/e2e/run-8fdee911be35/results.json`, including Published UploadField
same-path A/B, repeat `Unchanged`, missing-snapshot fail-closed, and partial
culture en-US-republish/fr-FR-snapshot-carry-forward cases; Full
transfer/publication 22/22 in `artifacts/e2e/run-b5b2c4780302/results.json`, including
the greenfield template-rejection case; fresh package install in
`artifacts/package-install/native-published-docker-20260925/result.json` using an isolated Docker SDK.
The SQL Server source proof is 4/4 in `artifacts/e2e/run-148ef4ea5e5e/results.json`;
SQL Server target culture-Media proof is 2/2 in
`artifacts/e2e/run-923dbb295bb3/results.json`.
Earlier-package native Backoffice browser evidence passed 19/19 in
`artifacts/e2e/browser-snapshot-final/results.json` against disposable sites in a
Playwright container; it predates the current production commit. It is bounded flow evidence, not cross-browser or hosted-CI
acceptance. Dictionary behavior is verified by the real API suite. Dictionary evidence: 1/1 in
`artifacts/e2e/run-d84b5395c2e5/results.json`; package smoke in
`artifacts/package-install/run-dictionary-fixed-20260924/result.json`. Other real-site
evidence above refers to earlier packages unless an artifact is explicitly listed as
current. This is not a claim of commercial uSync Complete parity.

| Boundary | Current limit |
| --- | --- |
| JSON requests | 8 MiB by default; configurable up to 64 MiB |
| Backoffice frozen transfer manifest | 8 MiB |
| Typed client manifest/ordinary JSON response | 16 MiB |
| Ordinary typed client request timeout | Two minutes |
| Adapter media export | 100 MiB per file; raising transport limits does not raise this adapter limit |
| Optional recovery journal | 64 MiB per record by default; selected transfers record the bounded destination before-state, while adapters without scoped planning retain the full snapshot |
| Optional durable job store | Defaults: 16 queued/preparing jobs, 64 MiB aggregate job-record budget and 1,000 terminal records; configurable ranges are 1–64 jobs, 1–512 MiB (not below the JSON request limit), and 1–1,000 terminal records. The Backoffice admission timeout defaults to 30 seconds and is clamped to 1–120 seconds. |

Source tree enumeration uses pages internally, but the transfer still builds and
a whole manifest. Ordinary transfer has no paged protocol, resumable upload or
background continuation. Durable Push changes only the receiver-side application
step: the Backoffice saves an owner-bound idempotency/destination mapping before its
one admission POST and can refresh the receipt by idempotency key or execution status
by operation ID while that mapping remains accessible. Durable local Pull uses the
same bounded private job store but a separate owner/job-kind binding. Its staged Media
assets are preflighted before admission and again by the worker; the media consumer
independently verifies the stream it opens. Each asset is limited to 100 MiB, and the
job never retains bearer tokens. Both flows retain a browser session recovery key when
available. A lost admission response, an unconfirmable lookup, an interrupted
execution, or a restart while preparing/running yields `OutcomeUnknown`; inspect the
destination or local site and status before creating another approved attempt. The
queue never automatically retries, rolls back, cancels, resumes assets, or replays
interrupted work, and it is private to one process rather than a distributed queue.
These bounds are not
a tested large-site capacity claim. See the backend capability audit
and the current implementation roadmap
for the scoped-snapshot and large-site work still required.

## Named receiver policies

A receiver may keep one optional legacy bearer token, which grants all receiver
operations, or configure named peers with an id, rotation tokens, enabled flag,
revision, and explicit operation allow-list. Named peers scope only the receiver
machine credential; they do not implement user-group, content-root, or culture
authorization. The available operations are capabilities, export, preview, apply,
asset read, asset write, publication preview, publication apply, recovery read,
browse, and BrowseSearch. BrowseSearch is absent from the default capabilities
response and is advertised only when the caller explicitly requests the extension.

`AddFerryTransportFromConfiguration` reads named-peer policy for each
request after the host publishes a configuration reload. Invalid current policy
values fail closed; request and asset limits remain startup settings. An operator
must advance a peer revision for every policy change. Named transfer/publication
approvals are HMAC-protected, process-local envelopes that expire after 15 minutes;
a restart, scale-to-zero or another instance invalidates them and apply answers
`410 Gone`; run one receiver instance. They are not a
replay ledger or a general single-use token. See the [peer-policy contract](research/peer-policy-design.md).

## User-group permissions for delegated editors

Ferry registers two Umbraco permission verbs, **Send with Ferry** (`CommunitySync.Push`) and **Receive
with Ferry** (`CommunitySync.Pull`). Administrators assign them in the Users section, per document (granular
permissions) or as a group default. Umbraco has no media granular permissions, so media transfers use the group default.
A delegated editor needs the verb in addition to the configured grant and Umbraco's native permissions; the verb never
replaces either. Administrators are unaffected.

`Ferry:Backoffice:RequireGranularPermissions` (default `true`) can switch the verb check off. On the first start
after upgrading, every user group already configured in `DelegatedEditors` receives its direction's verb as a default
permission, so existing grants keep working. That step runs once, so a verb an administrator later removes is never
restored. Groups configured after that first start need the verb assigned in the Users section.

## Administrator pull

An authenticated administrator may use the management pull preview/apply API only
for a configured connection whose server-side `AllowPull` flag is true. Preview
accepts either a full site or 1–1000 typed roots, exports the source
closure, stages verified assets, and freezes an owner-bound 15-minute approval.
Apply consumes the approval, rechecks source/local capabilities and connection
state, and writes drafts through the same local recovery journal used by receiver
apply. It does not publish, delete, schedule, or create a durable job.

The optional Browse reader lists configured remote roots, including nested roots,
as a virtual paged list and accepts pages of 1–100 items. It returns key, name, human-readable breadcrumb,
child presence, and cultures. It resolves breadcrumb labels with one bounded public
ancestor lookup per page (at most the trailing 16 IDs per item); an ellipsis marks
a shortened breadcrumb. It does not expose native integer paths, properties,
serialized payloads, snapshots, or media bytes. Sibling order uses native
`sortOrder`; equal-order ties and concurrent sibling changes have no stronger
pagination guarantee. A 3 MiB typed-client response ceiling bounds the largest
legal escaped JSON page.

The management Browse route requires an HTTPS configured `AllowPull` source and
the existing pull compatibility preflight: source Browse plus Export, local Preview
plus Apply, matching format, and the requested kind. The source machine permission
remains separate: a named peer may be granted Browse without Export. Delegated child
navigation verifies remote ancestry and each returned direct child before exposing
metadata. The optional BrowseSearch route repeats the same source, local, delegated
and ancestry checks, then searches only entity names in the permitted Content or
Media scope. Terms must be 2–128 characters, SQL wildcard characters `%`, `_` and
`[` are rejected, results are metadata-only and pages contain at most 50 items;
the maximum offset is 10,000. It does not query property values, serialized data,
media bytes, or a general site index. Administrator previews can show
bounded field differences for supported Content/Media values; delegated preview
responses suppress them. Delegated
Pull grants can scope permitted remote roots and cultures and must pass native
permissions; they cannot request a full-site pull or schema changes. The feature
remains experimental and is not production-ready.

## Explicit exclusions and fail-closed behavior

The tested subset is not a claim that every property editor, reference type or
Media configuration transfers. Unsupported values reject before writes:

- Culture-varying Media outside the tested name/caption/`umbracoFile` shape. The
  tested names survive through Ferry's private durable store, rather than
  native Umbraco's fresh Media read; arbitrary culture-varying Media editors and
  native Backoffice display of those names are not implied. Segment-varying scalar
  Media values are covered only for the tested TextBox contract.
- Published-source Content `UploadField` transfer is limited to publications with a
  matching immutable publish-time snapshot. Missing, corrupt,
  preexisting, or raw-value-mismatched snapshots fail closed. New native
  `SaveAndPublish` content preserves its pre-version immutable capture and binds it
  only after publication assigns a matching `PublishedVersionId`. Draft-source transfer uses hash-addressed descriptors
  and exact destination-byte verification. SQL Server source validation proves the
  new snapshot table, primary key, and one saved snapshot row; a SQL Server target
  culture-Media run proves table/primary-key creation with no snapshot rows expected.
  The tested culture-varying shape covers an en-US-only republish carrying an
  untouched fr-FR snapshot forward. Arbitrary culture-varying UploadField
  configurations, multi-node hosting, hosted CI, production topology, and every
  other Content file editor remain untested.
- Arbitrary relational Media properties/editors. The tested relational mapping is
  MediaPicker3 and destination Media identity; it does not imply support for every
  relation editor or configuration.
- Unknown or custom editors unless the host explicitly registers and validates a
  scalar contract or a mapped contract with an installed mapper.
- User and Member references. Supported references are the tested Content/Media
  pickers, Block List dependencies and rich-text links/images; this does not cover
  arbitrary relation types or every editor configuration.
- Template files and template hierarchies, unless both peers opt into executable
  template transfer (see [Optional modules](#optional-modules)). Otherwise a
  matching template must already be installed at the destination for an assignment
  to be retained.
- Existing schema changes that need storage or variation migration, property
  removal, and composition removal. Missing compatible schemas can be created, but
  unsupported changes need an explicit host migration.

## Optional modules

These modules are off by default. Enabling any of the transfer opt-ins below moves a
site to protocol/schema 2 and `communitysync.full.v6`; such a site negotiates only
with peers that also run v6, and each manifest additionally requires the specific
capability operation on both peers. Default sites keep protocol 1 and
`communitysync.full.v5`. Evidence is from exact-package two-site runs on
2026-09-27 (`artifacts/e2e/`), 494 ordinary .NET tests, and client tests.

| Module | Enable | Contract and limits | E2E |
| --- | --- | --- | --- |
| Executable templates | `Ferry:Full:AllowTemplateTransfer` on both peers | Create-only Razor templates as verified SHA-256 assets (1 MiB each, 16 MiB/200 per manifest); aliases `[A-Za-z0-9_]`, `_ViewStart`/`_ViewImports` blocked; alias/key, duplicate and existing `Views/*.cshtml` collisions rejected (fails closed without a content root); parents created first; a stored alias or `Layout`-derived parent that differs from the approval is removed. Approval shows an executable-code warning. Updates, renames and deletions are unsupported; runtime rendering is not proven because the test host precompiles Razor. | `templates` 4/4 |
| People | `Ferry:Full:AllowPeopleTransfer` on both peers | User groups (sections, fallback and document-level granular permissions, languages, start nodes), users (groups, start nodes, language), member groups, member types (public uSync serializer) and members (identity, approval on creation, groups, invariant values for text/textarea/email/integer/decimal/true-false/date editors). The Administrators group, administrators, the super-user and API users are never exported or modified; **no password, security stamp, lockout, login state or token is transferred**, so accounts need a password reset. Name/alias/user-name/email collisions reject before writes; other member editors and granular permission types fail the export closed; at most 10,000 members per full-site transfer. People move in full-site transfers. | `people` 5/5 |
| Domains | `Ferry:Full:AllowDomainTransfer` on both peers | A content node's default culture and ordered hostnames travel with the node; hostnames taken by another destination node or duplicated in one manifest reject; wildcard/unsafe names and non-BCP-47 cultures reject. Apply replaces the approved node's assignment; a node without domains never clears destination domains. | `domains` 3/3 |
| Offline packages | Always available to administrators | `.csync.zip`: one header (exporting site's capabilities + exact manifest) and one `assets/<sha256>` blob per declared asset. Import rejects unexpected names, traversal, duplicates, undeclared/missing blobs, oversize entries (`MaximumPackageBytes`, default 256 MiB), unsupported versions and any blob whose bytes differ from its hash, even when cached. Import uses the Pull planner, a one-time owner-bound approval and the local journal; it never publishes. Not compatible with any commercial package format. | `packages` 3/3 |
| Startup package import | Off by default; `Ferry:Backoffice:ImportOnStartup:Enabled` and `Files` (default `umbraco/Ferry/import-on-startup.csync.zip`, relative to the content root) | When the site starts at run level, each existing file is validated and checked for compatibility exactly as an uploaded package is. It is then planned and applied under one operation-gate hold, with the local journal, a restore point when existing entities change, and an operation-history entry (actor `startup`). A package whose plan has errors is never applied, and unattended import never publishes. The import finishes before the site reports started. Afterwards the file is renamed `.imported` or `.failed` and a `.result.json` (status, applied count, operation ID, restore point, error) is written next to it, so a restart never imports it twice. A shared file imported by several instances plans as unchanged after the first. | `startup-import` 1/1 |
| Snapshots and restore points | Catalog always available to administrators; restore points on by default (`CreateRestorePoints`) | Snapshots are catalogued packages (full site or roots) in the Umbraco database (`cmsCommunitySyncSnapshot`, shared by every instance); comparing one runs the package review against the current site, and restoring applies it. A restore point captures every destination entity an apply will touch, immediately before writing, on every local apply path: package import, snapshot restore, Pull, a Push received from another site, and durable apply; a failed capture aborts the apply (409 on the receiver). Restores write drafts and do **not** delete entities created after the capture, restore published versions or cover files, secrets or infrastructure. `MaximumSnapshots` (default 50) evicts restore points oldest-first, never manual snapshots. | `snapshots` 4/4 |
| Relations | `Ferry:Full:AllowRelationTransfer` on both peers | Custom relation types between Document and Media and their relations, in full-site transfers. Umbraco's system relation types (reference tracking, relate-on-copy/delete) are never transferred. A relation's identity is derived from (type, parent, child), so repeats are Unchanged and an existing identical destination relation is matched whatever its local key; relations are added or their comment updated, never deleted. Alias and object-type collisions reject. | `relations` 2/2 |
| Document blueprints | `Ferry:Full:AllowBlueprintTransfer` on both peers | Blueprints in full-site transfers, using the content format and the complete content apply pipeline (mapped values, references, file hashes); no parent and no allowed-at-root rule. Blueprint folders are not transferred: a blueprint kept in a folder arrives at the blueprint root. | `blueprints` 2/2 |
| Bulk apply suspensions | On by default; `Ferry:Full:BulkApply:Suspensions` (`None`, `ScheduledPublishing`, `Examine`, `DocumentCache`, `All`) and `MinimumOperations` (default 50) | A Full batch with at least `MinimumOperations` operations pauses scheduled publishing, Examine indexing and document-cache refresh through Umbraco's `Suspendable` switches, then resumes them once on every exit path (success, failure, cancellation). Resuming Examine after a suspended index request rebuilds all indexes, which is why small batches keep per-item indexing. Overlapping batches share one reference-counted suspension; a failing resume is logged and does not block the others. The switches are process-local, so other load-balanced instances are unaffected. Local negotiation only; no peer capability. | Unit tests; `packages` 3/3 with `MinimumOperations=1` (target log shows suspend and resume of `All`) |
| Server-side transfer queue | Every backoffice user with Ferry access; `GET`/`PUT community-sync/queue` | Each user's queue (at most 1000 Content, Media, DocumentType, MediaType or DataType roots) is stored on the server in `cmsCommunitySyncQueue`, one row per user, created by its own `CommunitySync.TransferQueue` migration plan. The queue follows the user across browsers and is cleared after a completed transfer as before. The browser keeps a synchronous cache: the server copy replaces it when the backoffice loads, a browser queue from before is uploaded once, and a server without the endpoint keeps the browser-only queue. Queued Content and Media show a "Queued for transfer" sign in trees and collections (`CommunitySync.QueuedForTransfer` flag); the sign appears when the tree is next loaded. Queueing grants nothing: every transfer is still authorized at review. | `queue` 1/1 |
| Content-only sites | Off by default; `Ferry:Full:ContentOnly` on the receiving site | For sites whose schema is deployed with the code, for example uSync files in source control. Any Push, Pull, package or startup import whose plan would create, update or move a document, media or member type, data type, language, template, media-type variation or relation type is rejected before anything is written. The error lists up to 20 items (kind, alias, key) to deploy first. Unchanged schema prerequisites are accepted, so content whose types already match transfers normally. The check runs on every planned transfer, at review and again at apply. Dictionary items, members and other content-like kinds are not affected. | `content-only` 2/2 |
| Code-first schema (`SchemaBuilder`) | Use `SchemaBuilder` in your own Umbraco migrations; see [code-first schema](code-first-schema.md) | `Ensure…` methods create or converge data types, templates, languages, media types and document types (tabs, groups, folders, templates, variations) and never remove anything. Destructive changes (a property's data type, a data type's editor or storage, variations) are refused. Keys are RFC 4122 v5 UUIDs derived from aliases, so every environment gets identical identities and content-only transfers plan the schema as unchanged. `GET …/community-sync/schema/code` writes an existing site's schema as one migration that keeps every key. | `schema-migrations` 6/6 |
| Package data | Off by default; `Ferry:Full:AllowPackageItemTransfer` on both peers, plus a provider registered on both (`AddFerrySkybrudRedirects()`, `AddFerryUmbracoForms()` or your own `AddFerryPackageProvider<T>()`) | Items a package keeps outside content, as `PackageItem` entities with their keys. A whole-site transfer carries every item; a selected transfer carries the items whose pages and media are all selected. Items pointing at missing or binned pages or media are left out of the export and logged. Items are created or updated, never deleted. Peers negotiate provider aliases; a missing provider refuses the transfer before anything is written. Skybrud redirects: destination URLs must be site paths or http(s). Umbraco Forms: definitions and workflows; records, folders, prevalue and data sources are not transferred, and a form whose prevalue or data source is missing on the destination is refused. See [extending Ferry](extending.md). | `package-items` 4/4 |
| Site seed | Administrators | `seed/preflight` reports compatibility, destination emptiness (when Browse is granted) and shared optional features; the seed is the ordinary full-site Push review, so re-running re-plans and applies only remaining differences. | `seed` 3/3 |

## Schema storage and migrations

Where schema is deployed with the code, set `Ferry:Full:ContentOnly` on the receiving site so transfers carry content only (see the modules table).

Data type exports declare native storage metadata. Apply preserves that declared
storage instead of accepting base-uSync editor-default normalization. Existing
shared data type editor or storage changes are blocked before mutation because
they can affect destination-only content, unless Umbraco reports that no stored
value uses the data type (for example a fresh site's built-in types); a data type
used by an element type always counts as used. The same applies to changing or
removing a property. Property removal, storage/variation
changes, composition removal and other unsupported schema migrations require an
explicit migration. Older experimental manifests without storage metadata must be
exported again with the current version.

## Custom property editors

Unknown custom editors fail closed. Declare verified behavior explicitly:

```csharp
umbraco.AddFerryUmbracoFull(options =>
{
    options.ScalarEditors.Add("Custom.PlainText");
    options.MappedEditors.Add("Custom.Relations");
});
```

Use a scalar contract only for values that contain no site-local IDs, file paths
or entity references. A mapped contract additionally requires an installed
base-uSync mapper. The adapter checks mapped round trips and declared references
before saving content; declaring an alias does not create a mapper automatically.
Validate your custom editor on two disposable sites with different local IDs.

## Explicit publication

Publication selects destination content keys and cultures, obtains a fresh
publication preview, then requires its fingerprint in a separate apply request.
A sole `*` explicitly requests every currently available culture; invariant content
also uses `*`. Specific culture selections remain specific. An unpublished
ancestor must be explicitly selected where supported or published separately.
An invariant child beneath an unpublished culture-variant ancestor requires that
ancestor to be published first. Publication schedules must be handled separately.

The service validates properties and checks current draft/schema/ancestor and
language configuration state. Missing mandatory cultures must already be published
or explicitly selected; they are never silently added.
It does not infer source publication, publish unselected ancestors, unpublish,
change schedules or perform an automatic rollback. Completed items stay published
if a later item fails. `OutcomeUnknown` means a native call may have changed that
item before throwing; inspect its state before obtaining a new preview.

## Recovery and concurrency

The optional journal writes the selected destination draft before-state (or the
full snapshot for adapters without scoped planning), attempted operation and
approved fingerprint before mutation, followed by an independent outcome.
A missing outcome means completion is unknown. Publication recovery contains draft
state, not a copy of every previous published version; it cannot reverse publication.
Assets referenced by recovery records must remain in the configured asset store.
Retention and site/database backups remain host responsibilities.

One operation gate covers the following:

- inbound sync
- backoffice source export and planning
- Pull, package and snapshot apply
- durable jobs

Where the backoffice package is installed, the gate also holds a cluster-wide lease while each operation runs. The lease
is a single `cmsCommunitySyncLease` row in the Umbraco database, so instances that share the database run one
Ferry operation at a time. The lease works as follows:

- An instance claims it with a conditional update and renews it every 30 seconds.
- Claiming waits until the lease is free. If the caller's request is canceled, it gives up without taking the lease.
- An instance that stops without releasing the lease loses it after two minutes.
- Expiry uses each instance's UTC clock, so keep instance clocks synchronized.

A receiver-only host without the backoffice package keeps the process-local gate.

Preview fingerprints reject changes before application. Neither safeguard locks external CMS editors or other writers
for the entire operation. Use appropriate operational coordination for actively edited sites.

There is no implicit deletion, account replication, executable template/script
deployment, or guarantee that every third-party editor works without an adapter.
