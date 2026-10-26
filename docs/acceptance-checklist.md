# Completion criteria

This tracks the implemented content-sync and separate explicit-publication scope.
The experimental Full v5 checkpoint reports 433/433 ordinary .NET tests, a fresh
exact-NuGet fixture-consumer package install through an isolated Docker SDK, Full
transfer/publication 22/22, exact-package two-site source-version Published UploadField 6/6, and exact-NuGet culture-Media Push/Pull 2/2, including a
SQL Server-target restart run. Commands and artifact paths are in the
[validation record](validation-record.md). All run files live in ignored `artifacts/`
and are local evidence; CI evidence is pending. Checked items apply only to Umbraco
17.6.2 and the specific tested cases, not every site configuration. No commercial
parity claim is made.

## Automated acceptance completed

- [x] Official isolated SDK; normal restore/build/test with package validation.
- [x] Two independent real SQLite sites over loopback HTTPS with different numeric IDs.
- [x] Draft tree transfer preserving stable keys, hierarchy, values and live versions.
- [x] Administrator opt-in move of existing Content/Media trees. A Full destination
  must enable `AllowExistingTreeMoves`; a Push/Pull preview must explicitly request
  `allowMoves`. Preview exposes path and affected-descendant impact, binds the
  affected branch and publication state to approval, and stale edits reject before
  movement. Native moves carry destination-only descendants. The installed-package
  two-site Push/Pull suite passed 3/3. Native Content/Media transfer modals and
  Settings dashboard expose a default-off toggle and passed browser verification.
  Delegated moves and deletion remain unsupported.
- [x] Receiver-only administrator tree trash of explicit Content/Media destination
  roots. `Ferry:Full:AllowExistingTreeTrash` is default-off and must be
  enabled; named peers need separate `TrashPreview` and `TrashApply` grants.
  Preview accepts 1–100 unique, non-overlapping roots and shows full subtree path,
  affected descendants and published descendants. It binds branch, ancestor and
  publication state to a one-use approval; stale state rejects before Umbraco moves
  the root to its native recycle bin. Recycled or top-level roots and Content branches
  with scheduled publication are blocked. Transfer omission never trashes, and this
  feature neither deletes missing items nor empties a recycle bin. The correlated
  journal before-state is manual recovery evidence, not automatic rollback or
  published-version restoration. The FINAL2 packaged Full/Full two-site trash suite
  passed 3/3, including Content/Media recycle-bin descendants, journal correlation,
  stale and replayed approval rejection, and ordinary-transfer omission
  (`artifacts/e2e/run-fe728d8adbe5/results.json`).
- [x] Full-site Dictionary Item preview/apply preserves stable GUID identity, parent
  hierarchy, translations and language dependencies. This is full-site only; selected
  Content/Media behavior is unchanged. Moves and deletions are unsupported, and
  destination translation removals reject. The `dictionary-item` capability is
  opt-in, so older peers reject that kind. System audit identity is
  `Umbraco SuperUserKey`. NuGet consumer suite passed 1/1 in
  `artifacts/e2e/run-d84b5395c2e5/results.json`; package evidence is in
  `artifacts/package-install/run-dictionary-fixed-20260924/result.json`.
- [x] Published source-version selection supports invariant and variant Full content.
  For variants, the current source `PublishedCultures` set the effective culture scope;
  each culture's name, template and published value transfer per segment, while drafts
  in unselected destination cultures persist. Selecting an unpublished source culture
  rejects. Full-site selection omits unpublished nodes and fails closed when an omitted
  unpublished ancestor is required. Draft remains the default; destination publication
  is separate. Peers without the version capability reject the request. Final NuGet
  consumer source-version suite passed 6/6 in
  `artifacts/e2e/run-8fdee911be35/results.json`, including Published UploadField
  same-path A/B isolation, missing-snapshot rejection before writes, and partial
  culture carry-forward after an en-US-only republish. Earlier-package browser suites
  passed 19/19 in `artifacts/e2e/browser-snapshot-final/results.json`; they predate
  the current production commit.
- [x] Repeat import unchanged, destination-only preservation and stale approval rejection.
- [x] Existing installed template assignments are retained when their keys match;
  executable template files and template hierarchies remain site code. The current
  exact-package Full run (22/22) includes a greenfield missing-template rejection.
- [x] Reject scheduled target content before writes.
- [x] Create missing languages, document/data/media types and compositions.
- [x] Nested block dependency closure and reciprocal content references.
- [x] Reject schema identity collisions and destructive shared data type editor changes.
- [x] Preserve declared native data type storage; block changes requiring migration.
- [x] Invariant/culture Content values and default/named Content segments in tested
  real-site scenarios.
- [x] Full/Full relational MediaPicker3 values map to the selected destination Media
  identity, with unchanged repeat preview/apply (2/2 E2E cases). This does not imply
  support for arbitrary relational Media editors.
- [x] Full/Full Segment-varying scalar Media TextBox values transfer with invariant
  values and case-varied named segments, then converge to Unchanged on repeat (1/1).
  Arbitrary segmented editors remain unsupported.
- [x] Full/Full culture-varying Media for the tested name/caption/`umbracoFile`
  shape. A clean exact-NuGet two-site Push/Pull suite passed 2/2, including distinct
  en-US/fr-FR PNG bytes, captions, Ferry durable culture-name metadata,
  unchanged replay, and a fresh target process (`run-d96fcf3e9db4`); the SQL
  Server-target restart run also passed 2/2 (`run-7cc1d7cd178d`). Umbraco 17.6.2
  natively reads these culture names as `null` after a fresh Media read; this proves
  Ferry transfer persistence, not native Backoffice display or arbitrary
  culture-varying Media editor support.
- [x] Full/Full Content UploadField transfer uses hash-addressed assets and verifies
  exact destination bytes. Draft source covers changed source bytes and `Unchanged`
  replay. Published source is bounded to immutable publish-time
  snapshots: instrumented two-site source-version E2E 6/6 proves same deterministic path
  A/B isolation, exact Published A versus Draft B bytes, repeat `Unchanged`, a
  missing-snapshot preview rejection before target writes, and en-US-only partial
  republish carrying immutable fr-FR bytes forward after its live file is overwritten
  (`artifacts/e2e/run-c7b6236be7ec/results.json`). It also verifies native new-content
  `SaveAndPublish`: immutable bytes captured before `VersionId=0` is assigned bind to
  the resulting `PublishedVersionId`, transfer exactly, and replay unchanged.
  Preexisting publications without a snapshot fail closed on Published export.
  Exact-package SQL Server source E2E 4/4 verifies the snapshot
  table, `PK_cmsCommunitySyncPublishedContentAsset`, and one saved row
  (`artifacts/e2e/run-148ef4ea5e5e/results.json`); SQL Server target culture-Media
  E2E 2/2 verifies table/PK creation with zero snapshot rows as expected
  (`artifacts/e2e/run-923dbb295bb3/results.json`). The tested culture-varying shape
  is limited to en-US-only republish/fr-FR snapshot carry-forward; arbitrary
  configurations, multi-node hosting, hosted CI, and production topology remain
  untested.
- [x] Optional Full-mode culture-scoped transfer includes selected variant
  names/values and invariant values, preserves unselected destination variants, and
  binds the scope into the frozen manifest and approval fingerprint. A Pull peer
  without the capability fails closed; creating a scoped variant item requires the
  default and mandatory cultures. Full package E2E rejects a French-only create when
  en-US is mandatory: `run-ece7838074c4`. Full transfer/publication passed 21/21 and
  admin Pull 4/4 in preceding package `run-683eb6a1e837`.
- [x] Content/media pickers, rich-text links and embedded image references.
- [x] Media length/hash validation, native target paths and custom media metadata.
- [x] Optional asset-availability optimization: authenticated bounded extension-gated
  probe verifies staged hash/length; Push, Pull and generic client skip repeat network
  bytes; old peers fall back to full transfer. Target media remains locally re-exported
  and staged during planning, so only network byte transfer is saved. Cache eviction
  falls back safely. Push media passed 1/1 in `run-c8985f54771f` and Pull passed 4/4
  in `run-b2324d89cce4`; proxy-private counters asserted zero repeat GET/PUT transfers.
- [x] Selected-root closure includes required ancestors, schema and referenced entities.
- [x] In Full mode, `IScopedSyncDestinationStore` reads only destination entities in the dependency
  closure and external direct prerequisites; the same bounded snapshot drives approval
  fingerprints and recovery before-state. Unrelated destination edits do not stale
  approval, while selected-entity or prerequisite edits do. Adapters without scoped
  destination support retain full-snapshot behavior. Scoped E2E passed 1/1 in
  `run-ae4d8657cce4`; the recovery journal remains limited to 64 MiB per record by
  default and is not an atomic rollback.
- [x] Full-mode source selection ignores unrelated invalid editors/media while
  selected invalid dependencies still reject; all six typed roots match full-snapshot closure.
- [x] Authenticated peer capabilities declare the implemented protocol, adapter,
  entity kinds, operations and effective limits; incompatible Full/Draft formats
  reject before a poisoned source selection can export or write the destination.
- [x] Named receiver peers with explicit operation scopes, rotation tokens, live
  policy reload after host configuration publication, and HMAC-bound expiring
  transfer/publication approvals. Invalid policy values fail closed before receiver I/O.
- [x] Unsupported editor diagnostics and documented explicit adapter extension points.
- [x] Hard dependency ordering, cyclic soft references and partial-write reporting.
- [x] Administrative API connections, preview/apply, ownership and single-use approvals.
- [x] Bounded optional preview names/paths from frozen Full manifests; malformed,
  custom or unavailable projections fall back to Kind/Key without affecting approval.
- [x] Separate publication approval, selected cultures, ancestor validation and
  mandatory-language protection; publication apply rechecks enabled/destination
  configuration after capability negotiation; draft transfer does not infer publication.
- [x] Ordinary tests for cancellation, recovery, limits, TLS and process-local locking.
- [x] Opt-in durable Backoffice Push and local Pull: an administrator can select
  durable Push during review
  only when the destination advertises `durable-transfer-jobs` for its authenticated
  `Apply` peer. Before one bounded receiver admission POST, the Backoffice rechecks
  the preview's destination capability, current configuration and administrator
  access, then persists an owner-bound idempotency mapping. The receiver binds
  admission and status to that peer owner and `Apply` permission; same
  owner/key/request returns the original receipt and a changed request conflicts.
  The saved mapping supports receipt recovery by idempotency key and status recovery
  by operation ID. Lost admission/status confirmation and interrupted receiver work
  remain `OutcomeUnknown` and require destination inspection; no automatic retry,
  rollback, cancellation or replay is claimed. Local Pull is separately opt-in through
  `EnableDurableLocalPull`, using a separate local-Pull job kind and owner binding.
  At admission and worker execution it rechecks the configured source, credential,
  current Pull grant and native permissions. Staged Media assets are preflighted at
  both points, then consumed through independently verified streams; each asset is
  limited to 100 MiB. Its idempotency admission and
  receipt/status recovery are owner-bound, so it cannot cross into receiver-Apply
  jobs. Durable Push remains unavailable to delegated Push and publication. The
  latest local test totals and the packaged Media Pull, Push and Full E2E evidence
  are listed in the [validation record](validation-record.md); those artifact files
  are ignored and CI evidence is pending.
- [x] Local NuGet consumer restore/build/publish, provenance and static assets.
- [x] Final package's 24 Ferry App_Plugins assets byte-verified and public-base uSync
  asset mounted in consumer; served import-resolution probes passed (these are not
  rendered-browser acceptance).
- [x] Native publication picker/workflow and administrator operation history implemented;
  final-package publication/history real-site scenario passed 1/1.
- [x] Full registration of real base-uSync services/handlers and NuGet coexistence;
  production packages exclude the fixture probes.
- [x] Native base-uSync exports and updated XML values, unchanged repeats,
  disabled handler behavior, custom-mapper selection and cancellation semantics.
- [x] Final npm and NuGet dependency audits report zero advisories.
- [x] Setup/scope/failure/version documentation and original/upstream license notices.

## Remaining manual/release acceptance

- [x] Delegated editor Push package and real-site acceptance: explicit group alias,
  connection, local roots, allowed cultures, native Umbraco Read authorization,
  and default-deny behavior. The final Dictionary-capable package passed its focused
  two-site suite 1/1 in `artifacts/e2e/run-2c2a790f39a7/results.json`, including
  grant revocation between preview and apply.
- [x] Delegated editor Pull final-package scenario: explicit valid Pull grant,
  existing local root, permitted remote root/culture, native permission, and
  draft-only behavior. Full-site delegated Pull is prohibited; schema changes are
  denied.

- [x] B2 administrator opt-in draft pull preview/apply final-package validation,
  including typed roots, dependency closure, verified assets,
  capability/configuration drift and recovery journaling.

- [x] B2 bounded remote Browse metadata API real-site evidence. Configured remote
  roots, including nested roots, appear in a virtual paged list; delegated editors
  can navigate descendants after exact ancestry and direct-child checks. Prior and current-package
  scenarios and ordinary regressions cover separate Browse permission/capability negotiation,
  1–100 direct-child pages, absent readers, revoked grants before reads, malformed
  remote JSON, and human breadcrumbs. Native Content/Media actions now consume
  Browse. The latest package also passed 2/2 dedicated Browse cases.
- [x] Optional B2 BrowseSearch name-only metadata API. It has a distinct machine
  grant and opt-in capability extension, keeps Browse's local/delegated scope
  proofs, rejects SQL wildcard terms, limits terms to 2–128 characters, result pages
  to 50 and offsets to 10,000, and never searches properties or returns entity data.
  The latest package passed 2/2 dedicated BrowseSearch real-site cases.
- [x] Administrator Push/Pull field comparison uses the planning snapshot and
  bounds supported scalar Content/Media values. Receiver Preview needs a current
  Export grant before target values are returned; delegated responses omit them.
  Ordinary authorization/projector tests and latest-package real-site Push/Pull
  assertions passed. The native browser suite exercised the comparison view.

- [x] Earlier-package native Backoffice browser flows: three suites covering dashboard,
  transfer, publication, history and browse-authorized remote selection passed 19/19
  against two disposable Umbraco sites in a Playwright MCP image container
  (`artifacts/e2e/browser-snapshot-final/results.json`).
- [ ] Broad visual layout, accessibility, cross-browser behavior, browser lifecycle
  and production topology acceptance. The local container result is not hosted CI or
  cross-browser evidence.
- [x] Content transfer modal optional localized culture-code input, default-all
  behavior, and selected-scope review verified in Docker Chromium; Media transfer
  does not offer culture scope.
- [x] Final-package publication/history scenario passed 1/1; Astra re-review found
  no remaining P1/P2 issues.
- [ ] Operational acceptance on the intended hosting/database/filesystem topology,
  with its installed custom editors, backup/restore process and concurrency policy.
- [ ] Large-site transfer capacity beyond the documented request, manifest and
  BrowseSearch bounds.
- [ ] Maintainer release review and deliberate public package publication, if desired.

Cancellation controls exist; aborting a request cannot promise rollback or prevent
an already-started remote write. Recovery records report before-state and known
outcomes; full site backups and host-specific restore drills remain operational work.
No production service or public package is deployed automatically.

Implicit deletion, user/member replication, executable script/template deployment
and commercial product branding are outside the documented scope.
