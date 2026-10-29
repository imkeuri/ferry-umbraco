# Supported scope

Tested baseline: Umbraco 17.6.2 on .NET 10; the package name does not imply support
for another major.

Supported between two sites: invariant draft text, hierarchy and stable
identities; draft changes to live content; missing document/data types and
compositions; language creation and en-US/fr-FR values; rich-text local links and
embedded images (with native legacy-link normalization); reciprocal content pickers;
nested Block List content/settings and schema closure; selected subtrees with
referenced entities; repeat imports without changes or duplicates; default and
named-segment values; existing template assignments (template files and hierarchies
are not transferred); explicit culture publication and mandatory-language protection.
Scheduled destination and schema identity conflicts reject before writes.

| Capability | Limits |
| --- | --- |
| Image media, new media types, scalar metadata, MediaPicker3 references | Full mode; picker identities map to destination Media keys |
| Segment-varying scalar Media | Full mode: TextBox, invariant values, case-varied segment identities, unchanged replay |
| Culture-varying Media names, captions, files | Distinct en-US/fr-FR captions and bytes, names kept in Ferry's durable store, repeat `Unchanged`. Umbraco 17.6.2 returns native culture names as `null` on a fresh read, so the Backoffice does not show them. |
| Content UploadField | See [exclusions](#explicit-exclusions-and-fail-closed-behavior) |
| Block Grid, Multinode Treepicker, Multi URL Picker | Documents in Block Grid blocks (with element and data types), MNTP documents/media, Multi URL Picker document/media links. Values identical; media link `url` is the destination path; external links kept; repeat `Unchanged`. Not covered: Block Grid areas, nested grids, Single Block. |
| Full-site Dictionary Items | Keeps GUID identity, hierarchy, translations, language dependencies. No moves or deletion; deleting a destination translation rejects. Opt-in `dictionary-item` capability (older peers reject). Audit identity `Umbraco SuperUserKey`. |
| Scoped destination preview/apply, recovery before-state | — |
| Tree moves / tree trash | See [below](#selected-transfers-and-operational-limits) |
| Published source version; culture-scoped transfer | See [below](#selected-transfers-and-operational-limits) |
| Administrator preview/apply and approval ownership | — |
| Peer capabilities, Full/Draft format rejection | — |
| Named receiver peers, reload fail-closed, approval envelopes | See [named receiver policies](#named-receiver-policies) |
| Administrator draft pull | See [administrator pull](#administrator-pull) |
| Update field comparison | Bounded Content/Media differences in admin previews; only known scalar editors show values; receiver preview needs a current Export grant for target values |
| Schema differences in the review | Changed schema items (document, media and data types, templates) appear in the review as a change table of what differs, not only as a count; the review also notes that every page using them changes too. |
| Typed Media push | Destination kind preflight before export |
| Settings dashboard, transfer, publication, history | Layout, accessibility, cross-browser and production topology untested. |
| Delegated editor Push | One connection; exact group alias; local roots; allowed cultures; native Read; `Ferry.Push` ([permissions](#user-group-permissions-for-delegated-editors)). No verb: 403. |
| Delegated editor Pull | Explicit grant, existing local root, permitted remote root/culture, native permission, `Ferry.Pull` on updated items and create parents. Draft-only; no full-site or schema changes. |

No commercial parity is claimed. Ferry is standalone; its Backoffice is at Settings →
Synchronisation → Ferry. Full transfer saves through Umbraco's native services, so
other packages' save handlers fire normally. Schema and media changes go to live
definitions and files; publishing content is separate, unless an administrator ticks
*Publish on <site> after sending*, which runs the normal publication review and apply after
the send and stops at the review when it reports errors. Back up the site and database
before using it on a real site.

## Selected transfers and operational limits

**Scoped planning.** Full mode implements `IScopedSyncExportStore` (a root selection
resolves its source closure before serializing or opening media) and
`IScopedSyncDestinationStore` (preview/apply reads only closure entities and external
direct prerequisites). Other adapters use full snapshots. A Language root lookup by
portable key may enumerate serializer-derived language identities.

- Approval fingerprints that snapshot: edits to incoming entities or their
  prerequisites invalidate it; unrelated edits do not.
- Schema alias collisions and shared-schema checks run at preview and apply; invalid
  closure entities reject the transfer.
- The closure includes ancestors, schemas and referenced entities, which may be
  updated. Review the whole plan.
- Recovery records use the same snapshot.

**Asset availability.** An authenticated, bounded probe reports whether a peer
already staged an asset's hash and length, so Push, Pull and typed clients skip
repeat network bytes. Older peers and cache eviction fall back to full transfer.
Descriptors stay in the manifest, fingerprint and recovery records. Target media is
still exported and staged locally (avoiding that is roadmap work).

**Culture scope (optional).** Limits Content variant transfer to selected cultures,
frozen in the manifest and fingerprint. Selected names/values and invariant values
transfer; other destination variants are kept. Pull peers without the capability are
rejected before export. Creating a scoped item needs the default and mandatory
cultures. The Content modal's culture input defaults to all; Media has no scope.

**Published source version (optional; Draft is default).** The source's
`PublishedCultures` set the scope; each transfers its name, template and published
value per segment. Other destination drafts are kept. Selecting an unpublished culture
rejects. Full-site selection omits unpublished nodes and fails closed if a published
node needs an omitted ancestor. Results land as destination drafts. Peers without the
capability reject.

**Tree moves.** Set `allowMoves: true` on a Push or Pull preview (default false; a
toggle in the transfer modals and Settings dashboard). The destination must enable
`Ferry:Full:AllowExistingTreeMoves` and advertise `existing-tree-move`. Preview shows
old/new paths, descendant count, publication impact and field changes; approval
freezes the subtree and publication state, and stale approval rejects. The move
carries destination-only descendants and may affect a published path, but never
publishes. Administrators only; no deletion.

**Tree trash.** A separate receiver-only administrator operation; omitting an item
from a transfer never trashes it.

- Requires `Ferry:Full:AllowExistingTreeTrash` (default false) and separate
  `TrashPreview`/`TrashApply` peer operations. No other grant, including delegated
  ones, permits trash.
- 1–100 unique, non-overlapping roots. Recycled or top-level roots, and Content with a
  publication schedule in the branch, reject.
- Preview shows paths, descendant and published-descendant counts. The 15-minute,
  owner-bound, single-use approval freezes branch, ancestors and publication state;
  any change rejects as stale.
- Apply uses the native recycle bin and never empties it. The before-state is
  journaled under a returned operation ID for manual recovery; there is no rollback or
  restore of published versions or files. Check the recycle bin and journal before
  retrying an unknown outcome.

**Capabilities.** Peers publish an authenticated, no-store declaration (protocol/schema
version, adapter, kinds, operations, limits), checked before export or staging and
again before apply. Full and DraftText formats are incompatible. Publication has its
own operations and approval.

| Boundary | Limit |
| --- | --- |
| JSON requests | 8 MiB default, up to 64 MiB |
| Backoffice frozen manifest | 8 MiB |
| Typed client manifest/JSON response | 16 MiB |
| Typed client request timeout | Two minutes |
| Adapter media export | 100 MiB per file, regardless of transport limits |
| Recovery journal (optional) | 64 MiB per record default; no atomic rollback |
| Durable job store (optional) | 16 jobs (1–64), 64 MiB records (1–512, not below the JSON limit), 1,000 terminal records (1–1,000); admission timeout 30 s (1–120) |

Each transfer builds one whole manifest: no paged protocol, resumable upload or
background continuation. These are not tested large-site capacity figures.

### Durable Push and local Pull

- **Push**: offered at review when the destination advertises `durable-transfer-jobs`
  for its `Apply` peer (only with its private job store and journal). Rechecks
  capability, configuration and access before one admission POST. Not for delegated
  Push or publication.
- **Local Pull** (`EnableDurableLocalPull`): `LocalPull` job kind with its own owner
  binding. At admission and execution it rechecks source, credential fingerprint,
  grant and native permissions, and preflights staged Media (100 MiB each, read via
  verified streams). Bearer tokens are never stored.
- Both: owner-bound idempotency (same request returns the original receipt; a changed
  one conflicts), refreshable receipt and status, a browser recovery key, and work
  continues after the browser stops waiting.
- Lost responses, interruptions or restarts give `OutcomeUnknown`; inspect before
  retrying. No automatic retry, rollback, cancel or replay. Single-process queue.

## Named receiver policies

A receiver uses one optional legacy bearer token (all operations) or named peers with
id, rotation tokens, enabled flag, revision and an allow-list of: capabilities,
export, preview, apply, asset read/write, publication preview/apply, recovery read,
browse, BrowseSearch (advertised only on request). Named peers scope the machine
credential only, not user groups, roots or cultures.

`AddFerryTransportFromConfiguration` re-reads policy per request after a reload;
invalid policy fails closed. Request and asset limits are startup settings. Bump the
revision on every change. Approvals are HMAC-protected, process-local and expire in 15
minutes; restarts, scale-to-zero or other instances invalidate them (`410 Gone`), so
run one receiver instance. They are not a replay ledger. See the
[peer-policy contract](research/peer-policy-design.md).

## User-group permissions for delegated editors

Two verbs, **Send with Ferry** (`Ferry.Push`) and **Receive with Ferry**
(`Ferry.Pull`), are assigned in Users per document or as a group default
(media always uses the default). Delegated editors need the verb plus their grant and
native permissions; administrators are exempt. `Ferry:Backoffice:RequireGranularPermissions`
(default `true`) disables the check. The first start after upgrading gives each
`DelegatedEditors` group its verb once; later groups need it assigned manually.

## Administrator pull

Requires a connection with `AllowPull` true. Preview takes the full site or 1–1000
roots, stages verified assets and freezes an owner-bound 15-minute approval. Apply
rechecks state and writes drafts via the recovery journal; it never publishes,
deletes, schedules or queues a durable job.

**Browse** needs an HTTPS source and pull preflight (source Browse and Export, local
Preview and Apply, matching format and kind); a peer may be granted Browse alone. It
pages configured roots (1–100 items: key, name, breadcrumb, child flag, cultures),
using one ancestor lookup per page (last 16 IDs; ellipsis when truncated). No integer
paths, properties, payloads or media bytes. Ordered by `sortOrder` without guarantees
for ties or concurrent changes; 3 MiB response ceiling. Delegated navigation verifies
ancestry and each child.

**BrowseSearch** applies the same checks and searches names only: 2–128 characters,
`%`, `_` and `[` rejected, 50 per page, offset up to 10,000.

Delegated previews hide field differences. Delegated Pull grants scope roots and
cultures and cannot request full-site or schema changes. Experimental; not
production-ready.

## Explicit exclusions and fail-closed behavior

Untested values reject before writes:

- **Culture-varying Media** beyond the tested name/caption/`umbracoFile` shape;
  segment-varying Media beyond TextBox.
- **Published-source `UploadField`** without a matching immutable publish-time
  snapshot (`PublishedVersionId`, property/culture/segment, raw value); missing,
  corrupt, preexisting or mismatched snapshots fail closed. New `SaveAndPublish`
  content is captured before the version exists and bound afterwards; an en-US-only
  republish carries the fr-FR snapshot forward. SQL Server stores them in
  `cmsFerryPublishedContentAsset`. Draft-source uses hash-addressed
  descriptors with byte checks. Untested: other culture-varying UploadField setups,
  other file editors, multi-node hosting, production topology.
- **Relational Media editors** other than MediaPicker3.
- **Custom editors** without a registered contract ([below](#custom-property-editors)).
- **User and Member references** and arbitrary relation types.
- **Template files and hierarchies**, unless both peers enable
  [executable templates](#optional-modules); otherwise the template must exist at the
  destination.
- **Schema migrations**: storage/variation changes, property or composition removal.

## Optional modules

Off unless stated. Any transfer opt-in moves a site to protocol/schema 2
(Full format v6), which negotiates only with v6 peers and needs the
capability on both; default sites stay on protocol 1 (Full format v5).

| Module | Enable | Contract and limits |
| --- | --- | --- |
| Executable templates | `Ferry:Full:AllowTemplateTransfer`, both peers | Create-only Razor as SHA-256 assets (1 MiB each; 16 MiB/200 per manifest). Aliases `[A-Za-z0-9_]`; `_ViewStart`/`_ViewImports` blocked; alias/key, duplicate and existing `Views/*.cshtml` collisions reject (fails closed without a content root). Parents first; a stored alias or `Layout` parent differing from the approval is removed. Shows an executable-code warning. No updates, renames, deletions; rendering unproven. |
| People | `Ferry:Full:AllowPeopleTransfer`, both peers | Full-site. User groups (sections, fallback and document permissions, languages, start nodes), users (groups, start nodes, language), member groups/types, members (identity, approval on create, groups, invariant text/textarea/email/integer/decimal/true-false/date values). Never administrators, their group, the super-user or API users. **No passwords, security stamps, lockout, login state or tokens**; reset passwords. Collisions on name/alias/user name/email reject; other editors and permission types fail closed; max 10,000 members. |
| Domains | `Ferry:Full:AllowDomainTransfer`, both peers | Default culture and ordered hostnames travel with the node. Taken or duplicated hostnames, wildcard/unsafe names and non-BCP-47 cultures reject. Apply replaces the node's set; no domains never clears. |
| Offline packages | Administrators | `.ferry.zip`: header (capabilities, manifest) plus `assets/<sha256>` blobs. Rejects unexpected names, traversal, duplicates, undeclared/missing blobs, entries over `MaximumPackageBytes` (256 MiB), unsupported versions, hash mismatches (even cached). Pull planner, one-time approval, journal; never publishes. No commercial format compatibility. |
| Startup import | `Ferry:Backoffice:ImportOnStartup:Enabled`, `Files` (default `umbraco/Ferry/import-on-startup.ferry.zip`, relative to the content root) | Validated like an upload, applied under one gate hold with journal, restore point and history (actor `startup`) before the site reports started. Errors block apply; never publishes. File renamed `.imported`/`.failed` with a `.result.json`, so it never runs twice; other instances plan it unchanged. |
| Snapshots and restore points | Administrators; `CreateRestorePoints` on by default | Snapshots (full site or roots) in `cmsFerrySnapshot`, shared by instances; compare or restore. Restore points capture every touched entity before each local apply (import, restore, Pull, received Push, durable); capture failure aborts (409). Restores write drafts; they do **not** delete newer entities, restore published versions, files, secrets or infrastructure. `MaximumSnapshots` (50) evicts oldest restore points, never manual snapshots. |
| Relations | `Ferry:Full:AllowRelationTransfer`, both peers | Full-site. Custom Document/Media relation types and relations; never system types. Identity is (type, parent, child); added or comment-updated, never deleted. Alias/object-type collisions reject. |
| Document blueprints | `Ferry:Full:AllowBlueprintTransfer`, both peers | Full-site, full content pipeline; folders not transferred (blueprints land at root). |
| Bulk apply suspensions | On; `Ferry:Full:BulkApply:Suspensions` (`None`, `ScheduledPublishing`, `Examine`, `DocumentCache`, `All`), `MinimumOperations` (50) | Large batches pause scheduled publishing, Examine and document cache via `Suspendable`, resuming on every exit. Resuming Examine rebuilds all indexes, hence the threshold. Overlaps are reference-counted; failed resumes are logged. Process-local. |
| Send or get everything | Administrators; *Send everything to…* / *Get everything from…* on the Content and Media section roots | Selects every top-level item of that tree (up to 1000) with descendants, never the whole site. Send reads this site's tree; Get asks the source for its top-level items at review. Oversized sends split into batches as usual; Get is one review (use *Get in the background* for large trees). An empty tree shows *Nothing to send*. |
| Transfer queue | Users with Ferry access; `GET`/`PUT ferry/queue` | Up to 1000 roots per user in `cmsFerryQueue`, across browsers; cleared after transfer. Older browser queues upload once; servers without the endpoint keep browser-only queues. Trees show "Queued for transfer". Grants nothing. |
| Content-only sites | `Ferry:Full:ContentOnly`, receiver | Rejects any transfer or import that would create, update or move document/media/member types, data types, languages, templates, media-type variations or relation types, listing up to 20 (kind, alias, key). Unchanged schema is fine. Items breaking root/child rules are placed as at the source when its type is in the transfer. Checked at review and apply. Dictionary and members unaffected. |
| Code-first schema (`SchemaBuilder`) | Your migrations; see [code-first schema](code-first-schema.md) | `Ensure…` creates or converges data types, templates, languages, media and document types; never removes, refuses destructive changes. Keys are RFC 4122 v5 UUIDs from aliases. `Remove…Async` (refused with stored values unless `allowDataLoss: true`), `Rename…Async`, `MovePropertyAsync`. `GET …/ferry/schema/code` exports a key-preserving migration. |
| Generated migrations | `Ferry:Schema:Migrations:Enabled`; `WriteDrafts`, `ProjectPath` on dev; see [generated migrations](code-first-schema.md#generated-migrations) | **Create migration** writes a timestamped migration and plan file (first adopts the schema). Pending ones run at startup in order; a failure rolls back with its views, blocks later ones and shows on the Advanced tab and a health check. Drift listed until resolved or **Accept current schema**. No member types. |
| Package data | `Ferry:Full:AllowPackageItemTransfer` and a provider on both peers (`AddFerrySkybrudRedirects()`, `AddFerryUmbracoForms()`, `AddFerryPackageProvider<T>()`) | Keyed `PackageItem` entities. Full-site carries all; selected carries items whose pages/media are all selected; items pointing at missing/binned content are skipped and logged. Never deleted. Missing providers refuse before writes. Skybrud: site paths or http(s) only. Forms: definitions and workflows only; forms missing a prevalue/data source at the destination are refused. See [extending Ferry](extending.md). |
| Site seed | Administrators | `seed/preflight` reports compatibility, emptiness (with Browse) and shared features; the seed is a full-site Push review, so reruns apply remaining differences. |

## Schema storage and migrations

Data type exports carry native storage metadata, which apply keeps. Changing a data
type's editor or storage, or changing or removing a property, is blocked unless
Umbraco reports no stored values (element-type use always counts). Composition
removal and other migrations need explicit code. Re-export older manifests without
storage metadata. For schema deployed with code, use `Ferry:Full:ContentOnly`.

## Custom property editors

Unknown custom editors fail closed. Declare verified behavior explicitly:

```csharp
umbraco.AddFerryUmbracoFull(options =>
{
    options.ScalarEditors.Add("Custom.PlainText");
    options.MappedEditors.Add("Custom.Relations");
});
```

Scalar contracts are only for values without site-local IDs, file paths or entity
references. Mapped contracts need an installed value mapper (declaring the alias does
not create one); round trips and references are checked before saving. Test on two
sites with different local IDs.

## Explicit publication

Select destination keys and cultures, get a fresh preview, then apply with its
fingerprint. A sole `*` means all available cultures (and invariant content).
Unpublished ancestors must be selected or published first; invariant children of an
unpublished variant ancestor need it published first. Schedules are separate.

Properties, draft, schema, ancestor and language state are validated. Missing
mandatory cultures are never added silently. It never infers source publication,
publishes unselected ancestors, unpublishes, changes schedules or rolls back;
completed items stay published if a later one fails. On `OutcomeUnknown`, inspect the
item before a new preview.

## Recovery and concurrency

Before mutation, the optional journal records the draft before-state, operation and
fingerprint, then the outcome; a missing outcome means unknown completion. It cannot
reverse publication. Referenced assets must stay in the asset store. Retention and
backups are the host's job.

One operation gate covers inbound sync, export and planning, Pull/package/snapshot
apply and durable jobs. With the backoffice package it also holds a cluster lease
(`cmsFerryLease` row) so instances sharing a database run one operation at a
time: claimed by conditional update and renewed every 30 seconds; waits until free (a
canceled request gives up); lost two minutes after an instance stops; expiry uses UTC
clocks, so keep them synchronized. Receiver-only hosts use a process-local gate.

Fingerprints reject changes before apply, but nothing locks other editors during an
operation; coordinate on busy sites.

There is no implicit deletion, account replication, executable template/script
deployment outside the opt-in [optional modules](#optional-modules), or guarantee that every
third-party editor works without an adapter.
