# Real-site validation (2026-09-28)

Ferry was run between two local copies of a production client site to find what synthetic E2E fixtures miss.

**Setup.** Umbraco 17.5.3 with Contentment, Block List, MetaMomentum, Google Maps and Azure Blob media. Source: fresh
SQL Server database seeded from the site's export — 9,182 documents, 5,168 media, 299 document types, 496 data types,
45 templates; media files replaced by Azurite placeholders. Target: fresh SQL Server database with the same schema
imported; content and media pushed with Ferry. Driver: `tests/e2e/realsite.spec.ts`
(`COMMUNITY_SYNC_SUITE=realsite`, manual only).

## Fixed

| Finding | Fix |
| --- | --- |
| Missing Azure media file made preview return an opaque 500. | Error names the item; preview returns 400. |
| Unsupported media file (e.g. `.svg`) failed without naming the item. | Error names item and file. |
| Selection errors were generic and unlogged. | Logged; administrators see detail, delegated editors the generic message. |
| **Dangling references blocked pushes** (8 of 9 subtrees). | Soft references to missing or recycled items are skipped with grouped warnings; roots and hard dependencies still fail closed. On apply, an approved reference may be absent only if its target is in neither the transfer nor the destination. |
| **Full-site push exceeded the 8 MB manifest limit**, found after a 5-minute export. | Administrator pushes split into dependency-ordered batches (≤ 4 MB, ≤ 250 items), exported once, reviewed and applied in turn (`preview/batches/{id}/next`). |
| A 392-item batch outlived the 2-minute client timeout. | 250-item cap; 10-minute request timeout. |

## Fixed in the follow-up round (2026-09-29)

| Finding | Fix |
| --- | --- |
| Packages required exactly Umbraco 17.6.2 and EF Core 10.0.10 (the site pinned 17.5.3 / 10.0.6). | Range `[17.5.0, 18.0.0)`; `Microsoft.OpenApi` pinned to patched 2.9.0. |
| Schema push collided with a fresh install's built-in data types. | Data types may be renamed before new ones are allocated; every key is still verified. |
| Site-shipped template Razor blocked template creation. | An identical Views file is adopted (compared without BOM or trailing whitespace). |
| Batching lost allowed child types. | Schema goes first, outside the batch cap. |
| SVG media not transferable. | Static SVGs pass a strict check on both sides (no script, handlers, foreignObject, external links, DTDs). |
| Contentment Data List / Data Picker needed opting in. | Built-in mapper keeps values and `umb://` references; other value-only editors via `Ferry:Editors:ScalarEditors`. |
| Upload autofill values made repeats report Updates. | Ignored in comparison. |
| Eye-dropper colour picker refused. | `Umbraco.ColorPicker.EyeDropper` and `Umbraco.EmailAddress` are built-in scalars. |
| Pull and package imports kept the 8 MB limit. | `Ferry:Backoffice:MaximumPackageBytes` (default 256 MB). |
| A large batch exceeded the 64 MB recovery record limit. | Default 256 MB. |
| Durable pushes could not continue batches. | 'Review next batch' after a durable job; interrupted applies suggest durable transfer. |

## Verified end to end

| Scenario | Result |
| --- | --- |
| Seed preflight | v6 peers compatible, shared features and empty destination detected. |
| Media folder, 84 items | 82/82 applied in 5.9 s, incl. recovery from an earlier storage-error stop. |
| Selected tree, 13.6 MB, 1,300+ entities | 8 batches, 466 content created, warnings instead of failures. |
| Full site, 123 MB (15x old limit) | 64 batches, 14,105 changes (8,380 content, 4,720 media), 1,301 reference warnings; ~10 min preview, 62 min apply. Repeat: 9,011 of 9,182 Unchanged. |
| Unauthenticated transport request | 401. |
| Fresh 17.5.3 install, no schema import, 114 MB | 43 batches: 166 data types, 236 document types, 39 templates, 1,635 media, 8,426 documents. Repeat: all but 137 documents Unchanged. |
| Existing target, Settings tree, 115 MB | 43 batches incl. SVGs and recycle-bin references; repeat: all 1,722 media Unchanged. |

## Remaining observations

1. **Site behaviour:** the site's save handlers add reciprocal links and re-sort year/month folders, so ~200
   documents differ after each push. They also look up nodes by production integer id (`GetById(2906)`).
2. Destinations slower than ~2 s per saved item should use durable transfer jobs.

# Second real site: whole-site Get (2026-10-24)

A second client site, upgraded from Umbraco 13, ran Ferry 0.2.0 in the other direction: a fresh install **got** the
whole site.

**Setup.** Umbraco 17.7.1 with Forms, Engage, Azure Blob media, Azure SSO, 2FA, Skybrud Redirects, MetaMomentum,
Google Maps and Block List. Source: the development SQL Server database — 2,076 documents, 4,041 media, 165
document types, 472 data types, 28 templates; media files as local placeholders. Target: fresh **SQLite** install
without Engage (it refuses SQLite), calling `pull/preview` (`fullSite: true`) and `pull/{id}/apply` over the peer
protocol. Ferry's tables were removed from the source afterwards.

## Fixed

| Finding | Fix |
| --- | --- |
| `.jfif` and `.heic` files blocked the transfer. | `.jfif`, `.jpe`, `.heic`, `.heif` allowed. |
| Values for a segment the property no longer varies by failed the plan. | Export skips and logs values Umbraco never reads. |
| Template with `Layout = "Master.cshtml"` but no stored master: *MasterTemplateNotFound*. | Parent taken from the Razor layout, as Umbraco does. |
| Template with no view file never matched after create and blocked later transfers. | Export sends Umbraco's default view; created Razor is checked against approved bytes. |
| Site save handlers failed during import. | `FerryImport.IsActive` lets handlers skip work during an apply. |
| Block List values with legacy `contentUdi`/`udi` (713 of 732) were blocked as data loss. | Matching legacy UDI and key count as the same block; errors name the first differing JSON path. |
| **Pages below the root lost their template** on full-site transfer, unseen by repeat preview. | Full-site walk loads templates (1,685 of 2,076 pages have one). |
| Repeat preview showed 1,064 false Updates (date `Z`, empty rich-text `blocks`, null vs absent). | Wall-clock dates; canonical comparison. |

**Verified:** preview 6,801 operations, no errors, 77 s; apply **6,776 of 6,776** in 71 s with a restore point;
repeat preview all **Unchanged** except 1 of 4,041 media.

**Remaining observations, resolved:**

1. Duplicate sibling media folder names re-planned an Update each time; fixed in #32.
2. An SVG media type Update did not recur in the code-first run.
3. Ferry tables with the backoffice disabled are by design; the README explains removal (#32).
4. Code-first schema: `SchemaBuilder` covers tabs, templates, variations and data types; adopted in #30.

# Second real site: adopting code-first schema (2026-10-24)

Ferry wrote the site's backoffice schema as one key-preserving `SchemaBuilder` migration (11,600 lines: 1 language,
463 data types, 28 templates, 9 media types, 165 document types, dependencies first). A fresh SQLite install ran it
at startup with `Ferry:Full:ContentOnly`, then got the site.

| Finding | Fix |
| --- | --- |
| Templates ordered by database master: *MasterTemplateNotFound*. | Ordered by views' `Layout`. |
| Group "404" has no derivable alias. | Stored alias written when it differs. |
| Legacy property keys on built-in media types. | Explicit keys re-key existing groups and properties. |

**Verified:** all **684 schema items Unchanged** in preview; apply **6,117 of 6,117**; repeat all Unchanged except
the duplicate-name item (later fixed); a second migration run created nothing. Source restored, trial copy deleted.

# Generated schema migrations (0.6.0-beta.1, 2026-10-27)

A site upgraded from Umbraco 13 moved to [generated migrations](code-first-schema.md#generated-migrations): **Create
migration** wrote the adoption migration, then a backoffice change produced a change-only one. A fresh content-only
install ran both, then got the site.

| Finding | Fix |
| --- | --- |
| Group-less properties refused, as a 500. | Stated on the type; `MovePropertyAsync(type, alias, "")`; unstatable schema is a 409. |
| Built-in data types with other keys (*Content Picker*). | `EnsureDataTypeAsync` adopts and re-keys an unused namesake. |
| `Layout` naming a plain view: *MasterTemplateNotFound*. | Created without a master. |
| Failed step left caches and views behind. | Step scope covers views; caches cleared on failure. |
| Pages breaking root/child rules refused on an identical type. | Copied as on the source. |

**Verified:** both migrations applied with no drift; **330 schema items Unchanged**; **2,512 items** applied; repeat
all Unchanged. Development database restored.
