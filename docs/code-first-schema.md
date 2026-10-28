# Code-first schema with SchemaBuilder

Ship schema as reviewed code, run it once per environment as Umbraco migrations, and let Ferry move only content
(enforce on receiving sites with `Ferry:Full:ContentOnly`).

`SchemaBuilder` covers what a content-only transfer compares: data types, templates, media types, document types
(tabs, groups, folders, templates, variations, compositions), languages, and custom relation types between pages and
media. Existing sites can switch in one step: [Adopting an existing site](#adopting-an-existing-site).

## A migration

```csharp
using Ferry.Umbraco.Schema;
using Umbraco.Cms.Infrastructure.Migrations;

public sealed class AddLanding(IMigrationContext context, SchemaBuilder schema) : AsyncMigrationBase(context)
{
    protected override async Task MigrateAsync()
    {
        await schema.EnsureDataTypeAsync("Tagline", "Umbraco.TextBox", dataType => dataType
            .EditorUi("Umb.PropertyEditorUi.TextBox").Config("""{ "maxChars": 80 }"""));
        await schema.EnsureTemplateAsync("landing", template => template.Name("Landing"));
        await schema.EnsureDocumentTypeAsync("landing", type => type
            .Name("Landing").Icon("icon-home").AllowedAtRoot().Folder("Pages").Composition("seo")
            .AllowTemplates("landing").DefaultTemplate("landing")
            .Tab("Content", tab => tab
                .Property("tagline", "Tagline")
                .Group("Hero", group => group.Text("heroTitle", required: true).MediaPicker("heroImage")))
            .Tab("SEO", tab => tab.Text("metaKeywords", name: "Keywords")));
        await schema.EnsureAllowedChildrenAsync("landing", "article", "landing");
    }
}
```

From 0.6 Ferry can [generate these migrations](#generated-migrations) from backoffice changes. Hand-written ones go
in your own plan, run at startup like any Umbraco migration:

```csharp
var plan = new MigrationPlan("MySite.Schema")
    .From(string.Empty)
    .To<AddSeoComposition>("add-seo-composition")
    .To<AddLanding>("add-landing");
await new Upgrader(plan).ExecuteAsync(migrationPlanExecutor, coreScopeProvider, keyValueService);
```

`AddFerryUmbracoFull()` registers `SchemaBuilder`.

## What the `Ensure…` methods do

| Method | Creates or converges |
|---|---|
| `EnsureDocumentTypeAsync`, `EnsureMediaTypeAsync` | Name, icon, description, folder, root and element flags, list view, variations, history cleanup, compositions, allowed templates, groups, tabs, properties |
| `EnsureAllowedChildrenAsync`, `EnsureAllowedMediaChildrenAsync` | Allowed child types, for types that allow each other |
| `EnsureDataTypeAsync` | Name, editor and editor UI, folder, storage, configuration |
| `EnsureTemplateAsync` | The template row for a view the site ships |
| `EnsureLanguageAsync` | Name, default and mandatory flags, fallback |
| `EnsureRelationTypeAsync` | Relation type between pages and/or media: name and direction. What it relates and its dependency flag are fixed once created |

- **Creates** missing items and **converges** existing ones. **Never removes**: unlisted groups, tabs and properties
  are kept, so a release can restate a type with only its additions; omitted settings keep their value. Name, icon,
  description and root/element flags are always stated (defaults: alias, `icon-document` or `icon-picture` for media
  types, empty, off).
- **Refuses (throws)** changing an existing property's data type, a data type's editor or storage, or the variations
  of an existing type or property. Write each as its own explicit migration.
- **Stable keys.** Without `.Key(...)`, keys are RFC 4122 v5 UUIDs (`SchemaBuilder.StableKey`) from
  `document-type:{alias}`, `media-type:{alias}`, `data-type:{name}`, `template:{alias}`, `relation-type:{alias}`,
  `{type}/group:{group alias}`, `{type}/property:{alias}`, so every environment has the same identities and
  content-only transfers see the schema as unchanged. `.Key(existingKey)` adopts a hand-made item; on groups, tabs and
  properties it also re-keys an existing one (e.g. built-in media types on upgraded sites).
- **Unused namesakes are adopted.** If no data type has the stated key but an unused one with the same name exists
  (e.g. a fresh install's *Content Picker*), it is re-keyed and converged. A namesake used by a property is refused.
- **Data type configuration** is portable JSON, written through Ferry's transfer serializers. If omitted, the existing
  configuration is kept.
- **Folders.** `.Folder("Pages/Landing")` moves an existing item there, creating folders as needed; `.Folder("")`
  moves it to the root; no `.Folder(...)` leaves it in place.
- **Templates** read `Views/{alias}.cshtml` and never change it (missing view: Umbraco's default view). The master
  comes from the view's `Layout`, so create layouts first. A `Layout` naming a plain view, not a template (e.g.
  `"HistoryTimelineLayout.cshtml"`), gives no master and logs a warning. Ferry briefly writes a placeholder into the
  view so Umbraco can read the master, then restores the original bytes; only a migration step's scope discards it on
  failure, so **call the template methods only from migrations**.
- **Groups and tabs.** `Group(...)` on a type is outside any tab; `Tab(...)` holds properties and groups; a group in a
  tab has alias `tab/group`. Use `.Alias(...)` when the stored alias isn't the one Umbraco derives from the name, and
  `.SortOrder(...)` when order isn't declaration order.
- **Properties outside any group** (common on upgraded sites): call `Property(...)` or a shortcut on the type itself,
  e.g. `type.Text("internalRemarks").Tab("Content", …)`. `Ensure…` never moves an existing property between groups;
  use `MovePropertyAsync`.
- **Property settings:** `Property(alias, dataTypeKey, property => …)` takes `Label`, `Describe`, `Mandatory` (with
  message), `Validation` (with message), `Vary`, `LabelOnTop`, `Order`, `Key`.
- **Shortcuts** use Umbraco's default data types by name: `Text`, `TextArea`, `RichText`, `Number`, `Toggle`, `Date`,
  `ContentPicker`, `MediaPicker`. Otherwise use `Property(alias, "Data type name")`.

## Adopting an existing site

1. As an administrator, choose **Settings › Ferry › Advanced › Download schema as code**, or call:

   ```
   GET /umbraco/management/api/v1/ferry/schema/code?namespace=MySite.Schema&className=AdoptSchema
   ```

   This returns a zip of partial-class files: `AdoptSchema.cs` (the migration) plus `AdoptSchema.DataTypes.cs`,
   `AdoptSchema.DocumentTypes.cs` etc., one per schema kind. `format=cs` returns one file. In code,
   `ISyncSchemaCodeExport.GenerateFilesAsync` and `GenerateAsync` return the same.
2. Review, commit with the site's views, and run it as the first step of the plan. Later changes are new migrations.
3. It changes nothing on the source site and recreates the same schema, keys included, elsewhere.

The migration runs: languages, relation types, data types, templates (layouts first), media types, document types
(compositions first); then allowed children; then block editor configuration (block data types are created early
without configuration). Default-valued settings are omitted; ungrouped properties are stated on the type. Member types
are not included (Ferry transfers them only with people).

Schema `SchemaBuilder` cannot state (e.g. a group containing groups outside a tab) is refused:
[Create migration](#create-migration) returns 409 with the reason and writes nothing.

## Removing, renaming and moving

Each step is a no-op when already in the target state:

- `RemoveDocumentTypeAsync`, `RemoveMediaTypeAsync`, `RemoveDataTypeAsync`, `RemoveTemplateAsync`,
  `RemoveLanguageAsync`, `RemoveRelationTypeAsync`, `RemovePropertyAsync`, `RemoveGroupAsync`, `RemoveTabAsync`,
  `RemoveCompositionAsync`.
- `RenameDocumentTypeAsync`, `RenameMediaTypeAsync`, `RenameTemplateAsync`, `RenamePropertyAsync`,
  `RenameGroupAsync`, `RenameTabAsync`: no-op when only the new alias exists, refused when both do. `RenameTabAsync`
  renames the tab's groups too (`old/x` → `new/x`); a `RenameGroupAsync` in the same migration naming the old tab
  alias follows it.
- `MovePropertyAsync(type, property, groupAlias)`: empty `groupAlias` moves it out of every group and tab.

`typeAlias` resolves a document type first, then a media type. Groups and tabs are removed only when empty (a tab: no
properties or groups).

A step that would lose stored values throws, failing the migration (rolled back and reported). The check runs on the
deploying environment:

- property and composition removals use Umbraco's property usage check on the owning type (for a composition, the
  composition or nested composition holding the property, which covers every type composed of it);
- a data type used by any property is never removed;
- a type with content is not removed;
- a language is removed freely only when no type varies by culture;
- element types (block values are not tracked) and a missing usage service count as "may hold values".

`allowDataLoss: true` overrides this; write it by hand, Ferry never generates it.

## Generated migrations

Edit schema in your development site's backoffice. Ferry keeps a **draft migration**; **Create migration** turns it
into a named C# migration you commit. Other environments run missing migrations at startup. Only compiled C# carries
schema; content still moves with Send and Get. Covers data types, document, media and relation types, templates and
languages. **Member types are not covered.**

### Settings

Under `Ferry:Schema:Migrations`:

| Setting | Default | Meaning |
|---|---|---|
| `Enabled` | `false` | Run generated migrations at startup and track their schema. Turn on everywhere. |
| `HistoryName` | `{SiteAssembly}.Schema` | History name, so one database can hold several sites. `{SiteAssembly}` is the entry assembly name. |
| `Namespace` | `{SiteAssembly}.Schema` | Namespace of generated classes (assembly name, not `RootNamespace`). |
| `WriteDrafts` | `false` | Allow writing `.cs` files. Development only. |
| `ProjectPath` | none | Absolute path of the web project folder (with the `.csproj`). Required for writing. |
| `Folder` | `Migrations/Schema` | Folder under `ProjectPath` for generated files. |

Put `WriteDrafts` and `ProjectPath` in `appsettings.Development.json` or user secrets:

```json
{ "Ferry": { "Schema": { "Migrations": { "Enabled": true, "WriteDrafts": true, "ProjectPath": "/src/MySite.Web" } } } }
```

Files are written only when `WriteDrafts` is true, the environment is `Development`, the Umbraco runtime mode is not
`Production`, and `ProjectPath` contains a `.csproj`. Paths never leave `ProjectPath`. Otherwise **Create migration**
is hidden.

If you change `Folder`, set MSBuild `FerrySchemaFolder` to match so the draft stays out of compilation:

```xml
<PropertyGroup><FerrySchemaFolder>Schema/Generated</FerrySchemaFolder></PropertyGroup>
```

### The draft

Every backoffice schema save, folder move or rename rewrites `{Folder}/_PendingSchemaChanges.cs` a few seconds later
with the differences from the last migration (deleted when there are none). It is **not compiled and not watched** by
`dotnet watch`, so it can't ship.

**Create your migration before you pull.** If teammates' migrations run on your database while you have a draft,
Ferry keeps it as `_PendingSchemaChanges.before-{time}.cs` (not compiled), logs a warning, and regenerates the draft
from your database afterwards. Where a teammate restated an item you edited, the draft shows your database's current
state; check it.

### Create migration

As an administrator, enter a name such as `AddLandingPage` on **Settings › Ferry › Advanced** and choose **Create
migration** (class name: capital first letter, letters and digits only), or:

```
POST /umbraco/management/api/v1/ferry/schema/migrations
{ "name": "AddLandingPage" }
```

`GET …/ferry/schema/migrations/status` returns history, draft and drift.

- Writes `{Folder}/{yyyyMMddHHmm}_{Name}.cs`, adds it to the plan, deletes the draft, and marks it applied on your
  database.
- **The first migration adopts the whole schema** (as in [Adopting an existing site](#adopting-an-existing-site));
  later ones hold only changes since the previous one.
- Step id: `{yyyyMMddHHmm}-{kebab-name}`. A new step always sorts last; Ferry bumps the minute on a same-minute clash
  or when the plan is ahead of your clock.
- `{Folder}/FerrySchemaPlan.g.cs` lists every step. **Never edit it by hand**; on a merge conflict keep both lines.
- **Refused while the plan has migrations your database hasn't run** (just pulled, or failed here). Restart first, or
  your migration would undo theirs.
- **Parallel branches** both run, in step id order. If both restate the **same item**, the later one wins and the
  other change is lost. After merging, restart, check the item, and add a fix-up migration if needed.

### What happens at startup

Ferry keeps its own per-environment history (not Umbraco's single "last step").

- Every unrun migration runs in step id order, each in its own scope, whatever the merge or deploy order.
- Afterwards Ferry refreshes content type and data type caches and rebuilds the published cache once the site has
  started ("Ferry refreshed the content type caches…"). Each run logs "Ferry schema migrations finished in … ms".
- **A failing migration does not stop the site.** Its database writes, template view files and Umbraco's in-memory
  caches are rolled back, so steps must derive from `AsyncMigrationBase` (`UnscopedAsyncMigrationBase` is refused).
  The failure is logged, shown on the Advanced tab and in the **Ferry schema migrations** health check, and **blocks
  later migrations**. It retries on next start; fix the migration and redeploy.
- **Load balancing:** only the scheduling publisher runs migrations. Register an `IServerRoleAccessor` returning
  `SchedulingPublisher` on one server and `Subscriber` on the rest (`builder.SetServerRegistrar<T>()`). With
  Umbraco's default election roles are *Unknown* at boot, so every server runs them, possibly the same step at once.

### What a generated migration contains

`MigrateAsync` runs, in order: renames; property removals; `Ensure…` for each new or changed item (whole definition,
keys included); property moves; group, tab and composition removals; whole-item deletions. Your hand-written code runs
before the renames, so target a renamed item's **old** alias (and create any group it moved into that is new in this
migration).

Anything Ferry cannot write safely becomes `#error Review: …` at the top of `MigrateAsync`, so **the build fails**
until you handle it and delete the line. The item is then **not** restated; write its whole change yourself. This
applies to:

- an existing property's data type or variation;
- a data type's editor or storage;
- an existing type's variations;
- a template's layout (master template);
- a relation type's alias, what it relates, or its dependency flag;
- aliases swapped or rotated between items, properties, groups or tabs;
- a key changed under the same alias, or a container switched between group and tab.

A language's ISO code identifies it, so a code change is written as remove plus add; the removal refuses where a type
varies by culture, so write it by hand there. Removals follow the
[stored-value rules](#removing-renaming-and-moving) and can fail on one environment but not another.

### Drift

Schema that differs from what the migrations produced (e.g. an edit on live) is **drift**, listed on the Advanced tab
and by the health check across deploys until resolved. A migration that changes a drifted item does not clear it
unless the result matches exactly. Resolve by either:

- making the change on a development machine and choosing **Create migration**; or
- choosing **Accept current schema** (administrator, any environment). The API can accept specific items; no or empty
  `keys` accepts everything. It returns the new status.

  ```
  POST /umbraco/management/api/v1/ferry/schema/migrations/accept
  { "keys": ["<item key>", "..."] }
  ```

Development sites that write drafts show no drift (differences are the draft). Schema arriving by Ferry transfer is
drift everywhere else, hence `Ferry:Full:ContentOnly` on receiving environments.

### Moving from a hand-written 0.5 plan

0.6 leaves your old `MigrationPlan` alone. To switch:

1. Enable the settings on your development site and **Create migration**; with no history or plan file it is an
   adoption migration, marked applied locally.
2. In the **same commit**, remove your old plan's registration.
3. Deploy. Each environment runs the adoption migration once; matching schema is unchanged.

Ferry never reads or rewrites another plan's state.

## Guardrails

- **ImageSharp advisory (GHSA-v76p-62qx-wwq2):** Umbraco 17 depends on SixLabors.ImageSharp 3.1.x (heap
  out-of-bounds write, fixed in 3.2.0). Ferry doesn't reference it. 3.2.0 refuses Release builds without a Six Labors
  license key, so reference 3.2.0 if licensed, or record the advisory as accepted.
- Environments on different migrations have different schema; content-only transfers between them are rejected with
  the items to deploy first.
