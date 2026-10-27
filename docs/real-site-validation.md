# Real-site validation (2026-09-28)

Ferry was installed into a copy of a production client site and exercised between two local
instances. This records what a real site exposed that the synthetic E2E fixtures did not.

## Setup

- Site: an agency client site on Umbraco 17.5.3 with Contentment, Block List, MetaMomentum and
  Google Maps editors; Azure Blob media storage.
- Source: fresh SQL Server database seeded from the site's own schema and content export — 9,182 documents, 5,168 media,
  299 document types, 496 data types, 45 templates. Media files replaced by placeholders in Azurite.
- Target: fresh SQL Server database; schema imported from the same export (as a deployment would),
  content and media pushed with Ferry.
- Installing Ferry required Umbraco 17.6.2 and EF Core 10.0.10 (the site pinned
  17.5.3 / 17.0.2 / 10.0.6).
- Driver: `tests/e2e/realsite.spec.ts` (`COMMUNITY_SYNC_SUITE=realsite`, manual only).

## Fixed

| Finding | Fix |
| --- | --- |
| A media record whose file is missing from Azure storage made preview return an opaque **500** (the provider throws `RequestFailedException`). | `MediaStorageFiles.Open` turns any storage failure into an error naming the item; preview returns 400 with that detail. |
| An unsupported media file (e.g. `.svg`) failed with no item named. | The error names the item and file. |
| Selection errors returned a generic 400 and were not logged. | Logged; administrators see the detail, delegated editors keep the generic message. |
| **Dangling references blocked pushes.** Content referenced deleted documents and media; 8 of 9 tried subtrees failed. | Soft references to missing or recycle-bin items are skipped at the source and reported as grouped review warnings. Roots and hard dependencies still fail closed. On apply, every produced reference must still be approved; an approved one may be absent only when its target is neither in the transfer nor on the destination. |
| **Full-site push exceeded the 8 MB manifest limit** (and the size check ran only after a 5-minute export). | Oversized administrator pushes are split into dependency-ordered batches (at most 4 MB and 250 items each), exported once, and reviewed and applied batch by batch (`preview/batches/{id}/next`). |
| One batch of 392 media updates outlived the remote client's 2-minute timeout. | Batches are capped at 250 items and the remote client allows 10 minutes per request, like the asset client. |

## Fixed in the follow-up round (2026-09-29)

| Finding | Fix |
| --- | --- |
| The packages pinned exactly Umbraco 17.6.2. | Range `[17.5.0, 18.0.0)`; the real site installs on its own Umbraco 17.5.3. `Microsoft.OpenApi` is pinned to the patched 2.9.0. |
| Pushing schema into a fresh install collided with its built-in data types. | Data types may be renamed; renames run before new data types are allocated; a name may move from a destination data type renamed in the same transfer or unused there. Apply still verifies every key. |
| Template Razor already shipped with the site's code blocked template creation. | A Views file identical to the incoming Razor is adopted. Razor is compared as Umbraco stores it (no BOM, no trailing whitespace), so adopted templates stay Unchanged. |
| Batching spread a site's schema across batches, losing allowed child types. | Schema comes first and does not count toward the 250-item batch cap. |
| SVG media were not transferable. | Static SVGs transfer after a strict safety check on export and again on the destination (no script, event handlers, foreignObject, external links or DTDs). |
| Contentment Data List / Data Picker had to be opted in as untracked scalars. | A Ferry mapper keeps the value, reports its `umb://` references and exports compact JSON so repeats compare equal. Value-only editors can be opted in through `Ferry:Editors:ScalarEditors`. |
| Upload autofill values (`umbracoBytes` etc.) made repeat pushes report Updates. | Media differing only in autofilled values is Unchanged. |
| The eye-dropper colour picker was refused. | `Umbraco.ColorPicker.EyeDropper` and `Umbraco.EmailAddress` are built-in scalars. |
| Pull and package imports kept the 8 MB limit. | Bounded by `Ferry:Backoffice:MaximumPackageBytes` (default 256 MB); the transport request limit is not applied to local applies. |
| A large batch exceeded the 64 MB recovery record limit. | Default raised to 256 MB (a record keeps the before-state of everything a batch touches). |
| Durable pushes could not continue batched transfers; slow sites got no guidance. | 'Review next batch' after a durable job completes; interrupted applies suggest durable transfer. |

## Remaining observations

1. **Site behaviour, not Ferry:** the client site's save handlers add reciprocal links (lawyers,
   insights, location, practices, awards) and re-sort Insights year/month folders on every save, so about
   200 of ~8,500 documents differ again after each push. Its handlers also resolve nodes by production
   integer ids (`GetById(2906)`), which fails on any other database; the test copy uses the node key.
2. Durable transfer jobs remain the answer for destinations whose saves are slower than ~2 s per item.

## Verified end to end

- Seed preflight: compatible v6 peers, shared Templates and Domains features, empty destination detected.
- A real media folder (84 items): preview, apply 82/82 in 5.9 s, including recovery from an earlier apply
  that stopped on a storage error (restore point captured first).
- Selected tree (Practices, 13.6 MB, 1,300+ entities with references): 8 batches, every batch previewed
  without errors and applied (466 content created), with unresolved-reference warnings instead of failures.
- Full site (123 MB manifest, 15x the old limit): split into 64 batches; every batch previewed without errors
  and every batch with changes applied Completed — 14,105 changes including 8,380 content and 4,720 media
  created, with 1,301 unresolved-reference warnings. About 10 minutes of previews and 62 minutes of applies.
  A repeat previewed 9,011 of 9,182 documents as Unchanged; the rest are open finding 4.
- Unauthenticated transport requests are rejected (401).
- Fresh Umbraco 17.5.3 install, no schema import (package floor): a selected tree whose references reach most
  of the site (114 MB) pushed schema and content in 43 batches — 166 data types, 236 document types, 39
  templates, 1,635 media and 8,426 documents. A repeat previewed all schema, templates and media and 8,289
  of 8,426 documents as Unchanged (the rest is remaining observation 1).
- Existing target: the Settings tree (115 MB, 43 batches) with restored SVG media and references to
  recycle-bin items — every batch applied; 10 SVG files created; a repeat previewed all 1,722 media as
  Unchanged.

# Second real site: a whole-site Get (2026-10-24)

A second agency client site, an accounting firm's site upgraded from Umbraco 13, exercised Ferry 0.2.0 the other
way round: a fresh install **got** the whole site from a copy of it.

## Setup

- Site: Umbraco 17.7.1 with Umbraco Forms, Umbraco Engage, Azure Blob media, Azure SSO, 2FA, Skybrud
  Redirects, MetaMomentum, Google Maps and Block List.
- Source: the site's local development database (SQL Server) with **2,076 documents, 4,041 media, 165 document types,
  472 data types and 28 templates**. Its file export holds schema only, so the content came from the database. Media
  files were replaced by placeholders on local disk (the development storage account was not reachable).
- Target: a fresh install on **SQLite**, with Engage removed (it refuses SQLite). The target ran
  `POST pull/preview` (`fullSite: true`) and `pull/{id}/apply` against the source over the peer protocol, so no
  backoffice account was needed on the source.
- Ferry's own tables and migration keys were dropped from the source database afterwards; it matches its prior state.

## Fixed

| Finding | Fix |
| --- | --- |
| `.jfif` (22 files) and `.heic` were not allowed media extensions; one such file blocked the whole transfer. | `.jfif`, `.jpe`, `.heic` and `.heif` are allowed static image files. |
| A stored value whose segment the property no longer varies by (an old A/B-test variant left after an upgrade) failed the plan: *Property culture/segment does not match schema variations.* | Export skips values Umbraco never reads (culture or segment not matching the property's variation) and logs each one on the source. |
| A template whose Razor declares `Layout = "Master.cshtml"` but whose database row records no master was created before its master: *MasterTemplateNotFound*. | Export takes the parent from the Razor layout, as Umbraco does when it creates the template; a layout that is not a template on the site is refused with a clear message. |
| A template with no view file has empty Razor; Umbraco writes its default view on create, so the template then never matched and, being create-only, blocked every later transfer. | Export sends the default view Umbraco would create. After creating a template, Ferry also checks that the stored Razor equals the approved bytes. |
| The site's save handlers looked nodes up by production integer ids and created year/month folders on save, so the import failed on a null node. | `FerryImport.IsActive` is true while Ferry applies a transfer; site handlers can skip work the transfer already carries. |
| Block List values never re-saved since the upgrade from 13 (713 of 732) keep `contentUdi`/`udi` beside the keys; the import check saw `contentUdi` become null and blocked: *Portable mapping … would lose or change data*. | The check treats a legacy block UDI and its key as the same block when they agree. The error now names the first differing JSON path and both values. |
| **Every page below the root lost its template** on a full-site transfer: the export walked the tree with Umbraco's `loadTemplates: false`, and the destination snapshot used the same walk, so a repeat preview did not notice. | The full-site walk loads templates. 1,685 of 2,076 pages carry a template on both sides. |
| A repeat preview reported 1,064 of 2,076 documents as Updates although nothing had changed: dates carried a `Z` from SQL Server but not from SQLite, Umbraco 17 adds an empty `blocks` object to rich text, and an empty picker is an explicit null on one side and absent on the other. | Dates are exported as wall-clock time. Content comparison uses canonical values: legacy block identities, empty rich-text blocks and empty values compare as unchanged. |

## Verified end to end

- Preview: 6,801 operations, no errors or warnings, 77 s (export included).
- Apply: **Completed, 6,776 of 6,776** in 71 s, restore point captured.
- Repeat preview: all documents, document types, data types, templates and 4,040 of 4,041 media **Unchanged**.

## Remaining observations, resolved

1. **Duplicate sibling name.** The source holds two root media folders named "Engage"; Umbraco makes sibling names
   unique, so the target stores the second as "Engage (1)" and each repeat planned an Update. Fixed in #32: an item
   that Umbraco renamed because a destination sibling holds its source name plans as unchanged.
2. **SVG media type Update.** It did not recur in the code-first run below, where every media type planned as
   unchanged.
3. **Tables with the backoffice disabled.** This is by design: the transport uses the lease table, and the full adapter
   has its own tables. The README explains how to remove them (#32).
4. **Code-first schema.** `SchemaBuilder` now covers tabs, templates, variations and data types, and the site adopted
   code-first schema (#30). See the next section.

# Second real site: adopting code-first schema (2026-10-24)

The same site moved its backoffice-made schema to code with `SchemaBuilder`.

## Setup

- Ferry wrote the source site's schema as one migration that keeps every key. It came to 11,600 lines:
  - 1 language;
  - 463 data types (block editors configured after their element types);
  - 28 templates, layouts first;
  - 9 media types;
  - 165 document types with 81 tabs and 129 groups, compositions first;
  - allowed children.
- A fresh SQLite install of the same site code ran that migration at startup, with `Ferry:Full:ContentOnly` on, then
  got the whole site from the source as before.

## Fixed while adopting

| Finding | Fix |
| --- | --- |
| Templates were created in database-master order, but Umbraco takes a new template's master from its view: *MasterTemplateNotFound*. | The generator orders templates by their views' `Layout`. |
| A group named "404" has no alias Umbraco can derive (aliases cannot start with a digit). | The generator writes the stored alias whenever it differs from the derived one. |
| The site was upgraded from an old version, so its built-in media types carry legacy property keys (`00000009-…`); a fresh install has others, and all six built-in media types differed. | An explicit key on a group or property also re-keys an existing one. |

## Verified end to end

- The migration created every schema item on the fresh install, with no errors.
- Content-only Get preview: no errors; all **684 schema items Unchanged** (472 data types, 165 document types, 9 media
  types, 9 media type variations, 28 templates and 1 language).
- Apply: **Completed, 6,117 of 6,117**.
- Repeat preview: everything **Unchanged** except the duplicate-name media item, which #32 later fixed.
- Running the migration a second time converged all 694 items and created nothing; the preview stayed unchanged.
- The source database was restored to its prior state, and the trial copy was deleted.

# Real-site check: generated schema migrations (0.6.0-beta.1, 2026-10-27)

A client site upgraded from Umbraco 13 to 17 was moved to [generated migrations](code-first-schema.md#generated-migrations)
the way a developer would.

## Setup

- On a development copy with `Ferry:Schema:Migrations` writing enabled, **Create migration** wrote the adoption
  migration of the whole schema, then a schema change in the backoffice became a second, change-only migration.
- A rebuilt fresh install of the same site code, content-only, ran both migrations at startup, then got the whole site
  from the development copy.

## Fixed while checking

| Finding | Fix |
| --- | --- |
| Upgraded sites have properties outside every group; the adoption refused them, and the refusal surfaced as a 500. | `SchemaBuilder` states group-less properties on the type itself, the generator writes them there, and moving a property out of every group is `MovePropertyAsync(type, alias, "")`. A schema Ferry cannot state is a 409 with the reason. |
| On a fresh install the adoption failed on built-in data types whose keys differ from the upgraded site's (*Content Picker*). | `EnsureDataTypeAsync` with a stated key adopts an unused namesake and re-keys it, as transfers do. |
| A template whose `Layout` names a plain view (with extension) failed with *MasterTemplateNotFound*. | Such a template is created without a master, keeping its view, also on name changes and renames. |
| The failed step was not fully taken back: Umbraco rolled back the database, but its caches still served what the step had created, and the template views stayed. | Each step runs in a scope that also covers view files; the caches are cleared when a step fails, and the failure is recorded after the rollback. |
| Pages that no longer fit their type's root or child rules were refused when their type was already identical on the destination. | They are copied where the source has them when the destination's type is the source's, including unchanged types (content and media). |

## Verified end to end

- The rebuilt site **Applied** both migrations at startup, with no drift.
- Content-only Get preview: no errors; all **330 schema items Unchanged**.
- Apply: **2,512 content and media items** completed.
- Repeat preview: everything **Unchanged**.
- The development database was restored to its prior state.
