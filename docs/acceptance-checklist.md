# Completion criteria

Scope: content sync plus separate explicit publication. Checked items cover Umbraco 17.6.2 and the tested cases
only. Results, commands and artifacts are in the [validation record](validation-record.md); all are local, CI
evidence is pending. No commercial parity claim is made.

## Automated acceptance completed

- [x] Isolated SDK; restore/build/test with package validation.
- [x] Two real SQLite sites over loopback HTTPS with different numeric IDs.
- [x] Draft tree transfer keeps keys, hierarchy, values and live versions.
- [x] Opt-in administrator moves of existing Content/Media trees (`AllowExistingTreeMoves` / `allowMoves`).
  Preview shows affected descendants and binds state to approval; stale edits reject. Push/Pull 3/3; browser toggle
  verified. Delegated moves and deletion unsupported.
- [x] Receiver-only administrator trash of 1–100 explicit roots (`Ferry:Full:AllowExistingTreeTrash`, plus
  `TrashPreview`/`TrashApply` grants). One-use approval; stale state, recycled or top-level roots and scheduled
  branches are refused. Omission never trashes; nothing is deleted or emptied. Journal is manual recovery evidence
  only. 3/3 (`artifacts/e2e/run-fe728d8adbe5/results.json`).
- [x] Full-site Dictionary Items keep GUID, hierarchy, translations and languages; opt-in `dictionary-item`
  capability; moves, deletions and translation removals reject. 1/1 (`artifacts/e2e/run-d84b5395c2e5/results.json`;
  `artifacts/package-install/run-dictionary-fixed-20260924/result.json`).
- [x] Published source-version selection for invariant and variant content: published cultures set the scope,
  unselected destination drafts persist, unpublished cultures and required unpublished ancestors reject. Draft is
  the default. 6/6 (`artifacts/e2e/run-8fdee911be35/results.json`); earlier-package browser 19/19
  (`artifacts/e2e/browser-snapshot-final/results.json`).
- [x] Repeat import unchanged, destination-only preservation, stale approval rejection.
- [x] Template assignments kept when keys match; template files stay site code; missing templates rejected.
- [x] Scheduled target content rejected before writes.
- [x] Missing languages, document/data/media types and compositions created.
- [x] Nested block dependency closure and reciprocal content references.
- [x] Schema identity collisions and destructive shared data type changes rejected.
- [x] Native data type storage kept; changes needing migration blocked.
- [x] Invariant/culture Content values and default/named segments (tested scenarios).
- [x] MediaPicker3 values map to destination Media, unchanged on repeat (2/2); not all relational editors.
- [x] Segment-varying Media TextBox values converge (1/1); not all segmented editors.
- [x] Culture-varying Media name/caption/`umbracoFile`: Push/Pull 2/2 (`run-d96fcf3e9db4`), SQL Server restart 2/2
  (`run-7cc1d7cd178d`). Proves Ferry persistence, not native display (Umbraco reads the names as `null`).
- [x] Content UploadField via hash-addressed assets with exact byte checks. Published uses immutable snapshots;
  publications without one fail closed. 6/6 (`artifacts/e2e/run-c7b6236be7ec/results.json`); SQL Server source 4/4
  (`run-148ef4ea5e5e`), target 2/2 (`run-923dbb295bb3`). Arbitrary culture setups, multi-node and hosted CI untested.
- [x] Optional culture-scoped transfer, bound into manifest and approval; peers without it fail closed; creates need
  default and mandatory cultures (`run-ece7838074c4`). Transfer/publication 21/21, Pull 4/4 (`run-683eb6a1e837`).
- [x] Content/media pickers, rich-text links, embedded images.
- [x] Media length/hash validation, native target paths, custom media metadata.
- [x] Optional asset probe skips repeat network bytes on Push and Pull; old peers fall back. Push 1/1
  (`run-c8985f54771f`), Pull 4/4 (`run-b2324d89cce4`), zero repeat GET/PUT.
- [x] Selected-root closure includes ancestors, schema and referenced entities.
- [x] Scoped destination reads (`IScopedSyncDestinationStore`): unrelated edits do not stale approval. 1/1
  (`run-ae4d8657cce4`). Recovery records default to 64 MiB and are not atomic rollback.
- [x] Unrelated invalid editors/media ignored; selected invalid dependencies reject.
- [x] Peer capabilities declare protocol, adapter, kinds, operations and limits; incompatible formats reject before
  export or writes.
- [x] Named peers: operation scopes, rotation tokens, live reload, HMAC-bound expiring approvals; invalid policy
  fails closed.
- [x] Unsupported-editor diagnostics and adapter extension points.
- [x] Hard dependency ordering, cyclic soft references, partial-write reporting.
- [x] Administrative API connections, preview/apply, ownership, single-use approvals.
- [x] Optional preview names/paths fall back to Kind/Key without affecting approval.
- [x] Separate publication approval with culture, ancestor and mandatory-language checks; drafts never imply
  publication.
- [x] Tests for cancellation, recovery, limits, TLS and process-local locking.
- [x] Opt-in durable Push (destination advertises `durable-transfer-jobs`) and local Pull (`EnableDurableLocalPull`):
  owner-bound idempotent admission and status, rechecks at admission and execution, staged Media ≤ 100 MiB. Lost or
  interrupted work is `OutcomeUnknown`; no automatic retry, rollback or replay. Not for delegated Push or
  publication.
- [x] NuGet consumer restore/build/publish, provenance, static assets.
- [x] 24 App_Plugins assets byte-verified and import-resolvable (not rendered-browser acceptance).
- [x] Publication picker/workflow and operation history, 1/1.
- [x] npm and NuGet audits: zero advisories.
- [x] Setup/scope/failure/version docs and license notices.

## Remaining manual/release acceptance

- [x] Delegated Push: group alias, connection, roots, cultures, native Read permission, default deny; revocation
  between preview and apply, 1/1 (`artifacts/e2e/run-2c2a790f39a7/results.json`).
- [x] Delegated Pull: grant, local root, permitted remote root/culture, draft only; no full-site Pull or schema.
- [x] Administrator draft Pull: typed roots, closure, verified assets, drift checks, recovery journal.
- [x] Remote Browse: paged roots and descendants with ancestry checks, revocation and malformed-response handling;
  2/2.
- [x] BrowseSearch (name only): own grant, no SQL wildcards, terms 2–128 chars, pages ≤ 50, offsets ≤ 10,000; 2/2.
- [x] Field comparison from the planning snapshot; target values need an Export grant and are hidden from delegated
  users.
- [x] Browser flows (dashboard, transfer, publication, history, remote selection), earlier package, 19/19.
- [ ] Visual layout, accessibility, cross-browser, browser lifecycle and production topology.
- [x] Content culture-scope input verified in Chromium; Media has no culture scope.
- [x] Publication/history 1/1; independent re-review found no P1/P2 issues.
- [ ] Operational acceptance on the real hosting, database, filesystem, custom editors, backup/restore and
  concurrency setup.
- [ ] Capacity beyond the documented request, manifest and BrowseSearch bounds.
- [ ] Maintainer release review and deliberate public package publication, if desired.

## Limits

- Cancelling cannot roll back or stop a remote write already started.
- Recovery records report before-state; backups and restore drills are operational work.
- Nothing is deployed or published automatically.
- Out of scope: implicit deletion, user/member replication, script/template deployment, commercial branding.
