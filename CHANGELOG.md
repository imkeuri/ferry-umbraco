# Changelog

All notable changes to Ferry. Versions follow [Semantic Versioning](https://semver.org/); while Ferry is pre-1.0,
minor versions may contain breaking changes.

## 0.6.0-beta.1

### Schema as generated C# migrations
- **Generated migrations.** With `Ferry:Schema:Migrations` enabled on a development site, schema edits in the
  backoffice keep a draft migration (`_PendingSchemaChanges.cs`, never compiled) up to date, and **Create migration**
  (Settings › Ferry › Advanced, or `POST /umbraco/management/api/v1/community-sync/schema/migrations`) turns it into a
  timestamped `SchemaBuilder` migration and adds it to the generated plan file `FerrySchemaPlan.g.cs`. The first one
  adopts the site's whole schema; later ones contain only what changed. See
  [generated migrations](docs/code-first-schema.md#generated-migrations).
- **Per-environment history.** Every environment runs the listed migrations it has not run yet, in step id order, at
  startup. A failing migration is rolled back, blocks the later ones, and is shown on the Advanced tab and by the new
  **Ferry schema migrations** health check; the site keeps running and the next start retries it.
- **Drift.** Schema changed outside the migrations (for example directly on live) is listed on the Advanced tab and by
  the health check until it is resolved, across deploys: a migration that changes a drifted item does not hide it.
  Administrators can **Accept current schema** (Advanced tab, or
  `POST …/community-sync/schema/migrations/accept`, all items or selected keys) to take the schema as it is there.
- **Create migration** refuses while the plan lists migrations the database has not run, so a teammate's change is
  never undone by a diff against a database without it.
- **New `SchemaBuilder` steps**: `Remove…Async` for every schema kind and for properties, groups, tabs and
  compositions; `Rename…Async` for document types, media types, templates, properties, groups and tabs;
  `MovePropertyAsync`. Removals refuse when stored values exist unless you pass `allowDataLoss: true` by hand.
- `.Folder(...)` in `Ensure…` now moves an existing item into the stated folder (`.Folder("")` = root).
- Files are written only in the Development environment, outside Umbraco's Production runtime mode, inside
  `ProjectPath`. Member types are not covered.
- Sites with a hand-written 0.5 schema plan keep it running; to switch, create a first (adoption) migration and remove
  the old plan registration in the same commit.

### Breaking
- `SchemaCodeExport` is created through dependency injection only; its constructor is now internal. Resolve it, or
  `ISyncSchemaCodeExport`, from the container.
- `SchemaBuilder` and `UmbracoFullSyncStore` have new optional constructor parameters. Source that calls them
  compiles unchanged, but code compiled against 0.5 that constructs them directly must be rebuilt (binary break).

### Behaviour changes
- `EnsureDataTypeAsync` with a stated key adopts an unused data type of the same name (re-keying it), as transfers
  do, instead of refusing; a namesake in use is still refused.
- A template whose view's `Layout` names a plain view rather than a template is created without a master template
  (in `SchemaBuilder` and transfers), instead of failing with *MasterTemplateNotFound*.
- Pages and media that no longer fit their type's root or child rules are copied where the source has them also when
  their type is unchanged on the destination; for media, the root and child rules are relaxed the same way as for
  content.
- `.Folder(...)` in `Ensure…` moves an existing item into the stated folder; before, it applied only to new items.
- `UmbracoMediaTransfer.ValidateAsync` has a new overload taking the unchanged schema items; the 0.5 overload is kept.

## 0.5.0-beta.1

### Self-contained
- **Self-contained.** Ferry no longer depends on any other synchronisation package. Schema is written and read by
  Ferry's own serializer and importer on Umbraco's services, and property values by Ferry's own value mappers, built
  on Umbraco's reference tracking. Sites that also run another synchronisation tool keep working side by side.
- **Value mapper API**: `IFerryValueMapper` and `AddFerryValueMapper<T>()` let you add support for your own property
  editors; see [extending Ferry](docs/extending.md).
- Language keys are derived from the ISO code, and built-in member property keys from the member type and alias, so
  every site agrees on them.
- **Transfer formats are now `communitysync.full.v7` / `v8`.** Upgrade both sites together: 0.4 and 0.5 sites refuse
  to exchange transfers or packages with each other.

## 0.4.0-beta.1 — first public release

### License and distribution
- **Ferry is now free to use and closed source**, under the [Ferry Freeware License](LICENSE): free for any site,
  including commercial work; no redistribution, modification or reverse engineering. Earlier builds were never
  published.
- Packages ship obfuscated, without source, symbols or repository links. `scripts/release.py` builds and checks them;
  the package E2E checks run against the same obfuscated build.

### Package data in transfers
- **Package providers**: a package can add data it keeps outside content (redirects, forms, …) to Ferry transfers
  by implementing `IFerryPackageProvider`. Items keep their keys, show in the review with their changed fields, and
  are written after the pages and media they point at. Off by default: set `Ferry:Full:AllowPackageItemTransfer` on
  both sites. A site without the provider refuses those items before anything is written. See
  [extending Ferry](docs/extending.md).
- **`Ferry.Skybrud.Redirects`** carries Skybrud redirects. Destination URLs must be site paths or http(s) URLs.
- **`Ferry.Umbraco.Forms`** carries Umbraco Forms definitions with their workflows, and accepts the form and theme
  pickers. Workflow view paths must stay inside the site's views, and address settings must be public http(s) URLs.
- **`Ferry:Full:AdditionalMediaExtensions`** allows a site's own static media types (for example `.pdn`). Types a
  browser or the server can run are refused.

### Fixes from two more real-site trials (Umbraco 17: 2,800 items with 19 redirects; 6,600 items with a form)
- Templates whose `Layout` is a plain view rather than a template transfer, including over an existing view file.
- Pages that no longer fit their type's root or child rules copy as the source has them when the type comes along.
- Blueprints kept in a blueprint folder no longer stop a whole-site export.
- The display-only `Umbraco.ListView` property of upgraded sites is accepted.
- Legacy `{localLink:umb://…}` links in rich text inside blocks no longer block the import.
- On SQLite, Ferry's lease renewal no longer commits in the middle of an entity write, where Umbraco's relation
  tracking would fail with "database is locked" after retrying for minutes.
- Legacy `{localLink:1234}` links by integer id approve the page they resolve to, so the import no longer refuses
  them as unapproved references.
- A page whose type varies by culture but that exists in no language is left out of a whole-site export with a
  warning, instead of stopping it.
- Changing a data type's editor or storage, or changing or removing a property, is allowed when no stored value uses
  it (a fresh site's built-in types). Element types always count as used, since block values are stored in pages.
- Block values written in another order compare equal.
- A peer request refused with 422 is logged with its cause on the refusing site.
- The "would lose or change data" message shows both values as text where they differ.

## 0.3.0-alpha.1 — 2026-10-24

### Code-first schema
- **`SchemaBuilder` covers the whole schema** (#30):
  - data types, with their portable configuration;
  - templates (the view file ships with the site; the layout comes from its `Layout`);
  - languages, media types and custom relation types;
  - document types with tabs and nested groups, folders, allowed and default templates, list views, variations,
    history cleanup and every property setting.
  Definitions are written through the same serializers transfers use, so a migration produces exactly the schema
  a content-only transfer compares. Nothing is removed, and destructive changes are refused.
- **Adopt code-first on an existing site** (#30, #33):
  - **Settings › Ferry › Advanced › Download schema as code**, or `GET community-sync/schema/code`, writes the site's
    schema as one migration that keeps every key.
  - The download is a zip with one partial-class file per schema kind; `format=cs` returns a single file.
  - Validated on a real client site (165 document types, 463 data types): a fresh content-only install ran the
    migration and got 6,117 items with every schema item unchanged.

### Backoffice
- **Spanish translation** (#31). Every term the backoffice uses now has English and Spanish text, including the
  workspace tab labels; a test keeps it that way.
- **Accessibility checks** with axe in the light and dark themes (#31); the Danger zone heading contrast is fixed.
- **Queue changes survive a reload** (#32): clearing the queue and reloading at once no longer brings items back.

### Fixes
- **Real-site Get fixes** (#29):
  - non-root pages kept their templates;
  - template layouts come from the Razor `Layout`;
  - `.jfif`, `.jpe`, `.heic` and `.heif` media are allowed;
  - orphan segment values are skipped;
  - `FerryImport.IsActive` lets site handlers skip work during an apply;
  - legacy block UDIs, SQL Server and SQLite dates, empty values and empty rich-text blocks no longer plan as updates.
- **Items Umbraco renamed "Name (n)"** because a destination sibling holds the source name plan as unchanged (#32).
- The packaged dashboard imported a chunk that was not committed; CI now fails when the committed backoffice build
  differs from a fresh one (#31).
- **SQLite: a durable apply could stall for minutes** while its restore point was saved. Ferry's database work read and
  then wrote in one deferred transaction; when another request committed in between, SQLite refused the write
  (`SQLITE_BUSY_SNAPSHOT`), which waiting never fixes, and the provider kept retrying it. Ferry's write work now takes
  SQLite's write lock first, as Umbraco does.
- The E2E fixture uses SQLite `Cache=Private`, which ends an intermittent Umbraco database deadlock in UI tests (#32).
  The README now recommends SQL Server for production sites that receive transfers.

## 0.2.0-alpha.1 — 2026-10-23

### Renamed and standalone
- **CommunitySync is now Ferry** (#19). Packages are `Ferry.Core`, `Ferry.Transport`, `Ferry.Umbraco` and
  `Ferry.Backoffice`. Configuration lives under `Ferry`; a site with only a `CommunitySync` section keeps working.
  Database tables, routes, headers, permission verbs and file formats keep their CommunitySync names, so existing
  sites and peers interoperate. See *Upgrading from CommunitySync* in the README.
- **Standalone package** (#20). Ferry has its own workspace under Settings › Synchronisation and needs no other
  synchronisation package.

### Backoffice redesign
- **Send and Get** replace Push and Pull throughout the interface (#21).
- **Pickers instead of GUID fields**, with a key fallback for items that exist only on the other site (#21).
- **Review screen** leads with a summary ("4 new pages"), calls out schema changes, moves and templates, and keeps
  the full list and unchanged items behind toggles (#22); the Publish review follows the same layout (#27).
- **Overview, Sites, Packages and Advanced tabs** (#23): connected-site diagram, whole-site Send and Get,
  activity in plain sentences, a Connect a site wizard with pairing codes, drag-and-drop package import, and a danger
  zone for recycle-bin moves and seeding.
- **Top-bar Ferry panel** with Queue and Activity tabs, and an *Add to queue* action (#23).
- Side-panel buttons sit in the panel footer (#24); compact site cards, a single Synchronisation heading, and
  theme-aware colours (#25); Umbraco form controls, first-run guidance, a Managed in config badge and
  visible keyboard focus (#27).
- Settings-tab text is translatable through `ferry_*` keys (#26, #27).
- Connection checks on the Sites tab are cached for five minutes (#26).

### Features
- **Editors see their own activity:** `GET community-sync/operations/mine` (#26).
- **Code-first schema:** `SchemaBuilder` with stable, alias-derived keys (#18).
- **Content-only sites:** `Ferry:Full:ContentOnly` rejects transfers that would change schema (#17).
- **Granular permissions** on top of delegated grants (#16) and a **server-side per-user transfer queue** (#14).
- **Package import at startup** (#12), a **cluster operation lease** (#11) and **bulk-apply suspensions** (#9).

### Fixes and maintenance
- Audited transitive package versions (#10) and editor reference coverage (#13).
- The E2E harness proxy streams responses in TLS-record chunks; browser specs record failed requests (#25, #26).
- The Settings workspace source is TypeScript.

## 0.1.0-alpha.1

First experimental release as CommunitySync: reviewed Full-mode Push and Pull, packages, snapshots, publication,
delegated editors and the native backoffice dashboard. No package was published.
