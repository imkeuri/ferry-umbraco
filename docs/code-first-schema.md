# Code-first schema with SchemaBuilder

You can ship schema as reviewed code, run it once per environment as Umbraco migrations, and let Ferry move only
content. A site that receives transfers can enforce that with `Ferry:Full:ContentOnly`.

`SchemaBuilder` covers what a content-only transfer compares:

- data types;
- templates;
- media types;
- document types, with tabs, groups, folders, templates, variations and compositions;
- languages;
- custom relation types between pages and media.

An existing site can adopt code-first in one step: Ferry writes its current schema as a migration that keeps every key
(see [Adopting an existing site](#adopting-an-existing-site)).

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

From 0.6, Ferry can write these migrations for you from the changes you make in the backoffice, and run them on
every environment: see [Generated migrations](#generated-migrations). You can also write them by hand and register
the steps in a plan of your own that runs at startup, as for any Umbraco migration. A working example is
`SampleSchemaMigrationComponent` in `tests/e2e/FixtureSupport/FixtureSupport.cs`.

```csharp
var plan = new MigrationPlan("MySite.Schema")
    .From(string.Empty)
    .To<AddSeoComposition>("add-seo-composition")
    .To<AddLanding>("add-landing");
await new Upgrader(plan).ExecuteAsync(migrationPlanExecutor, coreScopeProvider, keyValueService);
```

`SchemaBuilder` is registered by `AddFerryUmbracoFull()`.

## What the `Ensure…` methods do

| Method | Creates or converges |
|---|---|
| `EnsureDocumentTypeAsync`, `EnsureMediaTypeAsync` | Name, icon, description, folder, root and element flags, list view, variations, history cleanup, compositions, allowed templates, groups, tabs and properties |
| `EnsureAllowedChildrenAsync`, `EnsureAllowedMediaChildrenAsync` | The allowed child types, for types that allow each other |
| `EnsureDataTypeAsync` | Name, editor and editor UI, folder, storage, and configuration |
| `EnsureTemplateAsync` | The template row for a view the site ships |
| `EnsureLanguageAsync` | Name, default and mandatory flags, and fallback |
| `EnsureRelationTypeAsync` | A custom relation type between pages and/or media: name and direction. What it relates and its dependency flag are fixed once created |

- It **creates** the item when it is missing. When the item exists, it **converges** it to the definition.
- It **never removes anything.** Groups, tabs and properties that a definition doesn't list are kept, so a later
  release restates a type with its additions only. Settings a definition leaves out keep their current value. Name,
  icon, description and the root and element flags are always stated; they default to the alias, `icon-document`
  (`icon-picture` for media types), empty and off.
- It **refuses destructive changes.** These throw, because stored values could be lost: changing an existing
  property's data type, changing a data type's editor or storage, and changing the variations of an existing type or
  property. Write each of those as its own explicit migration.
- **Keys are stable.** Without `.Key(...)`, keys are RFC 4122 version 5 UUIDs derived from aliases
  (`SchemaBuilder.StableKey`): `document-type:{alias}`, `media-type:{alias}`, `data-type:{name}`, `template:{alias}`,
  `relation-type:{alias}`, `{type}/group:{group alias}` and `{type}/property:{alias}`. Every environment that runs
  the migration therefore has the same identities, which is what Ferry matches on, so a content-only transfer plans
  the schema as unchanged.
  `.Key(existingKey)` adopts an item that was created by hand. On groups, tabs and properties it also re-keys an
  existing one, so built-in media types on an upgraded site can be matched.
- **A data type with a stated key adopts an unused namesake.** When no data type has the stated key but one with the
  same name exists and no property uses it (typically a fresh install's built-in, such as *Content Picker*, whose key
  differs from an upgraded site's), `EnsureDataTypeAsync` re-keys that data type to the stated key and converges it,
  as transfers do. A namesake that a property uses is refused, because its key cannot change under stored values.
- **Data type configuration** is the data type's portable JSON configuration. Data types are written through the same
  serializers that Ferry transfers use. When the configuration is left out, an existing
  data type keeps its configuration.
- **Templates use the site's view file.** A new template reads `Views/{alias}.cshtml` and never changes it. Umbraco
  takes its layout (master template) from the view's `Layout`, so create layouts first. A `Layout` that names a plain
  view rather than a template (for example `Layout = "HistoryTimelineLayout.cshtml"` with no such template) gives a
  template without a master, as Umbraco keeps one whose view was edited later, and logs a warning; renaming it or
  changing its name works the same way. If the view is missing, the template
  gets Umbraco's default view. Umbraco reads a new template's master from the view file itself, so for such a
  template Ferry briefly writes a placeholder into the view and then puts the original bytes back. Inside a schema
  migration step that write is part of the step's scope and is discarded if the step fails. Called outside a migration
  step (for example from your own code at runtime), there is no such scope: a crash at that moment can leave the
  placeholder in the view, so call the template methods from migrations.
- **Groups and tabs.** `Group(...)` on a type is a group outside any tab. `Tab(...)` holds properties and groups. A
  group inside a tab has the alias `tab/group`. Use `.Alias(...)` when the stored alias isn't the one Umbraco derives
  from the name, and `.SortOrder(...)` when the order isn't the declaration order.
- **Properties outside any group.** Sites upgraded from older Umbraco versions often have properties in no group or
  tab. `Property(...)` and the shortcuts on the type itself state such a property:
  `type.Text("internalRemarks").Tab("Content", …)`. A new one is created outside every group. An existing property
  stays where it is, as for any property: `Ensure…` never moves one into or out of a group. Use `MovePropertyAsync`
  for that.
- **Property settings.** `Property(alias, dataTypeKey, property => …)` accepts every setting:
  - `Label`, `Describe`, `Mandatory` (with a message), `Validation` (with a message), `Vary`, `LabelOnTop`, `Order`, `Key`.
- **Shortcuts use Umbraco's default data types by name:**
  - `Text`, `TextArea`, `RichText`, `Number`, `Toggle`, `Date`, `ContentPicker` and `MediaPicker`.
  - For any other data type, use `Property(alias, "Data type name")`.

## Adopting an existing site

A site whose schema was made in the backoffice can move to code-first without changing any key:

1. As an administrator, open **Settings › Ferry › Advanced** and choose **Download schema as code**, or call:

   ```
   GET /umbraco/management/api/v1/community-sync/schema/code?namespace=MySite.Schema&className=AdoptSchema
   ```

   - The download is a zip with one partial-class file per schema kind: `AdoptSchema.cs` holds the migration, and
     `AdoptSchema.DataTypes.cs`, `AdoptSchema.DocumentTypes.cs` and the other files hold one kind each. Large sites
     stay reviewable, and later diffs show which kind changed.
   - `format=cs` returns a single file instead.
   - Inside the application, `ISyncSchemaCodeExport.GenerateFilesAsync` and `GenerateAsync` return the same code.
2. Review the file and commit it with the site's views. Run it as the first step of the site's migration plan. Later
   schema changes are new migrations after it.
3. On the site it came from, it changes nothing. On a new environment it creates the same schema, so a content-only
   transfer from the original site plans every schema item as unchanged.

The generated migration runs in this order:

1. Languages, relation types, data types, templates (layouts first), media types and document types (compositions
   first).
2. Allowed children.
3. Block editor configuration. Block editors name element types, so these data types are created early without their
   configuration and configured once the element types exist.

Settings that equal Umbraco's defaults are left out. Properties outside any group are stated on the type itself.
Member types are not included; Ferry transfers them only with people.

A schema that `SchemaBuilder` cannot state (for example a group that contains groups, which Umbraco only allows in
tabs) is refused: [Create migration](#create-migration) answers with a conflict (409) that gives the reason, and
writes nothing. Change the schema in the backoffice, then try again.

This was validated on a real client site (165 document types, 463 data types, 28 templates and 9 media types):

- A fresh content-only install ran the generated migration and pulled 6,117 items, with every schema item unchanged.
- Running the migration again changed nothing.

## Removing, renaming and moving

`Ensure…` only adds and converges. These steps state the other changes; each is a no-op when the environment is
already in the target state, so a migration is safe to run anywhere:

- `RemoveDocumentTypeAsync`, `RemoveMediaTypeAsync`, `RemoveDataTypeAsync`, `RemoveTemplateAsync`,
  `RemoveLanguageAsync`, `RemoveRelationTypeAsync`, `RemovePropertyAsync`, `RemoveGroupAsync`, `RemoveTabAsync`,
  `RemoveCompositionAsync`.
- `RenameDocumentTypeAsync`, `RenameMediaTypeAsync`, `RenameTemplateAsync`, `RenamePropertyAsync`,
  `RenameGroupAsync`, `RenameTabAsync`: a no-op when the new alias exists and the old one does not, a refusal when
  both exist. `RenameTabAsync` also renames the groups inside the tab (`old/x` becomes `new/x`).
- `MovePropertyAsync(type, property, groupAlias)`: an empty `groupAlias` moves the property out of every group and
  tab.

A step that would lose stored values throws, which fails the migration (Umbraco rolls the step back and Ferry reports
it). The check runs on the environment that deploys, because only it knows whether content holds the values: property
and composition removals use Umbraco's property usage check, asked of the type that owns each property (for a composition: the composition or nested composition that holds it, which covers every type composed of it), a data type is
never removed while a property uses it, a type is not removed while content of it exists, and a language is only
removed freely when no type varies by culture. Element types and a missing usage service count as "may hold values".
The `allowDataLoss: true` parameter is for you to write by hand; Ferry never generates it.

A group or tab is only removed when it is empty (a tab: no properties and no groups). Move or remove its properties
first. `typeAlias` resolves a document type first, then a media type.

## Generated migrations

You change schema in the backoffice of your development site as usual. Ferry keeps a **draft migration** with what
changed, and **Create migration** turns it into a named C# migration in your project. You commit it with the code.
Staging and live run every migration they have not run yet when the site starts. Nothing but the compiled C# carries
schema between environments; content keeps moving with Send and Get.

Covered: data types, document types, media types, templates, languages and relation types. **Member types are not
covered**; Ferry transfers them only with people.

### Settings

Under `Ferry:Schema:Migrations`:

| Setting | Default | Meaning |
|---|---|---|
| `Enabled` | `false` | Run the site's generated migrations at startup and keep track of the schema they produce. Turn it on everywhere. |
| `HistoryName` | `{SiteAssembly}.Schema` | Name the history is kept under, so one database can hold more than one site's history. `{SiteAssembly}` is the site's entry assembly name. |
| `Namespace` | `{SiteAssembly}.Schema` | Namespace of the generated classes (from the assembly name, not the project's `RootNamespace`). |
| `WriteDrafts` | `false` | Allow Ferry to write `.cs` files. Development only. |
| `ProjectPath` | none | Absolute path of the web project folder (the one with the `.csproj`). Required for writing. |
| `Folder` | `Migrations/Schema` | Folder under `ProjectPath` for the generated files. |

On a development machine, put `WriteDrafts` and `ProjectPath` in `appsettings.Development.json` or user secrets:

```json
{ "Ferry": { "Schema": { "Migrations": { "Enabled": true, "WriteDrafts": true, "ProjectPath": "/src/MySite.Web" } } } }
```

Ferry writes files only when **all** of these hold: `WriteDrafts` is true, the environment is `Development`,
Umbraco's runtime mode is not `Production`, and `ProjectPath` exists and contains a `.csproj`. Every path stays
inside `ProjectPath`. Otherwise nothing is written and **Create migration** is hidden. Staging and live never write
code; they only run it.

If you change `Folder`, set the MSBuild property `FerrySchemaFolder` in your `.csproj` to the same value. Ferry's
build files use it to keep the draft out of compilation:

```xml
<PropertyGroup><FerrySchemaFolder>Schema/Generated</FerrySchemaFolder></PropertyGroup>
```

### The draft

While writing is allowed, every schema save in the backoffice (and every folder move or rename) rewrites
`{Folder}/_PendingSchemaChanges.cs`, a few seconds later, with only what differs from the last migration. When
nothing differs, the file is deleted.

- The draft is **not compiled and not watched**: `dotnet watch` does not restart for it, and an unfinished draft
  can never ship. Open it in your IDE to see what the next migration will contain.
- **Create your migration before you pull.** When migrations from teammates run on your database at startup and you
  have a draft, Ferry first sets it aside as `_PendingSchemaChanges.before-{time}.cs` (also not compiled, kept as a
  backup) and logs a warning. Your edits are still in your database and still differ from the last migration, so
  after the teammates' migrations run Ferry writes the draft again with your edits in it. Where a teammate's migration
  restated an item you had also edited, the draft states what your database holds now; check it before you create
  your migration.

### Create migration

As an administrator, open **Settings › Ferry › Advanced**, enter a name such as `AddLandingPage`, and choose
**Create migration**. The name becomes the class name: it starts with a capital letter and has only letters and
digits. Or call:

```
POST /umbraco/management/api/v1/community-sync/schema/migrations
{ "name": "AddLandingPage" }
```

`GET …/community-sync/schema/migrations/status` returns the history, the draft and the drift shown on that tab.

- Ferry writes `{Folder}/{yyyyMMddHHmm}_{Name}.cs`, adds it to the plan file, deletes the draft, and records the
  step as already applied on your database (it holds those changes already, so your next restart does not run it).
- **The first migration is the adoption migration**: the whole current schema, every key kept (the same code as
  [Adopting an existing site](#adopting-an-existing-site)). Every later migration contains only the changes since the
  one before it.
- The step id is `{yyyyMMddHHmm}-{kebab-name}`. A new step always sorts after every step already in the plan: when
  another migration was created in the same minute, or the plan holds a later time than your clock, Ferry moves the
  timestamp on a minute at a time, so migrations run everywhere in the order they were created.
- `{Folder}/FerrySchemaPlan.g.cs` lists every migration with its step id. It is
  generated: **never edit it by hand.** When two branches each add a migration, git shows a conflict in it; keep both
  lines.
- **Create migration refuses while the plan lists migrations your database has not run** (for example a teammate's
  migration you just pulled, or one that failed here): restart the site so it runs them, then create yours. Otherwise
  your migration would be a diff against a database without their changes, and would undo them wherever it runs after
  them.
- **Parallel branches.** Two branches can each create a migration from the same starting point. Both run everywhere,
  in step id order. When both restate the **same item** (each `Ensure…` states the item's whole definition), the one
  that runs later wins and the other branch's change to that item is lost. After merging such branches, restart your
  development site so it runs both, check the item in the backoffice, and create one more migration if it needs
  fixing.

### What happens at startup

Ferry keeps its own history of the migrations each environment has run (not Umbraco's single "last step" state).

- At startup, every listed migration the environment has not run yet runs, in step id order, each as an ordinary
  Umbraco migration in its own scope. Two branches that each added a migration both run wherever they are missing,
  whatever order they were merged or deployed in.
- After a migration applies, Ferry refreshes the content type and data type caches and rebuilds the published cache
  once the site has started (logged as "Ferry refreshed the content type caches…").
- **A failing migration does not stop the site.** The whole migration is taken back: Umbraco rolls back its database
  writes, the view files Umbraco wrote for its templates are discarded, and Ferry clears Umbraco's in-memory caches so
  nothing it created before failing is still served (a step must therefore derive from `AsyncMigrationBase`; the plan
  refuses an `UnscopedAsyncMigrationBase`, which Umbraco runs outside that scope). Ferry records the failure with its message, and **no later
  migration runs** until it is fixed, so they never apply out of order. The failure is
  logged, shown on the Advanced tab and reported by the **Ferry schema migrations** health check. The next start
  retries it. The fix is a code change: edit the failing migration and deploy again.
- **Load-balanced sites:** servers in the subscriber role skip the migrations; they run on the scheduling publisher.
  Give every server an explicit role: register an `IServerRoleAccessor` that returns `SchedulingPublisher` on one
  server and `Subscriber` on the others (`builder.SetServerRegistrar<T>()`, as in Umbraco's load-balancing docs). With
  Umbraco's default election, every server's role is still *Unknown* when the migrations run at boot, so every server
  runs them, and two servers starting together can run the same step at once.
- Each run logs how long it took ("Ferry schema migrations finished in … ms").

### What a generated migration contains

Inside `MigrateAsync`, the steps run in this order:

1. Renames (types, templates, properties, tabs, groups).
2. Property removals.
3. `Ensure…` for every new or changed item, restating its whole current definition, keys included.
4. Property moves.
5. Group, tab and composition removals.
6. Deletions of whole items.

Ferry checks that the steps cover every difference. Anything it cannot write safely becomes an `#error Review: …`
line at the top of `MigrateAsync`, so **the project does not build** until you handle it and delete the line.

**Changes you write by hand.** These are `#error` lines, and Ferry does **not** restate the item at all; write that
item's whole change yourself:

- an existing property's data type or variation;
- a data type's editor or storage;
- the variations of an existing type;
- a template's layout (master template);
- a relation type's alias, what it relates, or its dependency flag;
- aliases swapped or rotated between items, properties, groups or tabs;
- a key changed while the alias stayed the same, or a container changed between group and tab.

A language's ISO code identifies it, so changing the code is written as removing the old language and adding the new
one. That removal refuses wherever a type varies by culture; write the change by hand there.

Your code runs before the renames, so for a renamed item target its **old** alias. If the item also moved into a
group that is new in this migration, create that group in your code too.

**Removals and stored values.** A removal refuses (and the migration fails on that environment) when stored values
exist there:

- removing a property, or a composition whose properties hold values;
- deleting a type that has content, or a data type that any property uses (always refused);
- element types and their properties always refuse, because block values are not tracked.

Pass `allowDataLoss: true` by hand when you mean it; Ferry never generates it. `RemoveGroupAsync` and
`RemoveTabAsync` refuse while the group or tab still holds properties or groups, which is why removals of contents
come first.

**Folders.** `.Folder("Pages/Landing")` in an `Ensure…` call moves an existing item into that folder (creating the
folders as needed), also in the adoption migration and in migrations you write. `.Folder("")` moves it to the root.
Without `.Folder(...)`, the item stays where it is.

**Tabs and groups.** `RenameTabAsync` also renames the groups inside the tab. A `RenameGroupAsync` in the same
migration that names the tab's old alias follows it.

### Drift

Ferry remembers the schema its migrations produced on each environment. Anything different, such as an edit made
directly on live, is **drift**: it is listed on the Advanced tab and by the **Ferry schema migrations** health check,
and it stays listed through later deploys until it is resolved. A deploy never hides it: when a migration changes an
item that had already drifted, Ferry does not take the result as the migrations' schema, so the item stays listed
(unless the migration happens to put it back exactly as the migrations had it).

To resolve drift, either:

- make the same change on a development machine and **Create migration**, so every environment gets it; or
- keep the schema as it is on this environment: as an administrator, choose **Accept current schema** on the Advanced
  tab. Ferry then treats the current schema as the migrations' schema here and the list clears. It works on any
  environment, including staging and live where no migration can be written. The API also accepts only some items:

  ```
  POST /umbraco/management/api/v1/community-sync/schema/migrations/accept
  { "keys": ["<item key>", "..."] }
  ```

  Without `keys` (or with an empty list) the whole current schema is accepted. It returns the status afterwards.

On a development machine that writes drafts, nothing is listed as drift: what differs from the last migration is your
draft.

Schema that arrives through a Ferry transfer is part of the migrations' schema only on a development site that writes
drafts (it then shows in your draft). Anywhere else it shows as drift. Use `Ferry:Full:ContentOnly` on environments
that receive transfers.

### Moving from a hand-written 0.5 plan

Sites that followed the 0.5 docs have their own `MigrationPlan` with an adoption migration. 0.6 leaves that plan as
it is. To switch:

1. On your development site, enable the settings above and choose **Create migration**. With no history and no plan
   file, the first migration is an adoption migration of the current schema, recorded as applied on your database.
2. In the **same commit**, remove the registration of your old plan (the component or code that runs it).
3. Deploy. Each environment runs the adoption migration once; it converges what is already there and changes nothing
   on a site whose schema already matches.

Ferry never reads or rewrites another plan's state.

## Guardrails

- **ImageSharp advisory (GHSA-v76p-62qx-wwq2).** Umbraco 17 depends on SixLabors.ImageSharp 3.1.x, which a security
  audit of your site reports (a heap out-of-bounds write, fixed in 3.2.0). Ferry itself does not reference ImageSharp.
  ImageSharp 3.2.0 refuses Release builds without a Six Labors license key, so updating it is your decision as the site
  owner: reference 3.2.0 directly when you have a license, or record the advisory as accepted until Umbraco moves on.

- Set `Ferry:Full:ContentOnly` on every environment that receives transfers, so schema arrives only through
  migrations.
- If one environment runs a newer migration than another, their schema differs, and a content-only transfer is
  rejected with the items to deploy first.
- The `schema-migrations` E2E suite runs the sample migration on two real sites and checks the generated code:
  `python3 scripts/e2e/run.py --mode Full --suite schema-migrations`.
- The `schema-files` E2E suite creates migrations on a development site, builds a release with them, runs it on a
  second site, and checks content-only transfers, restarts, a folder move, a property with values moved out of its
  group, drift and Accept current schema, and a failing removal:
  `python3 scripts/e2e/run.py --mode Full --suite schema-files`.
