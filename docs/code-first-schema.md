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

Register the steps in a plan and run it at startup, as for any Umbraco migration. A working example is
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
- **Data type configuration** is uSync's portable JSON, the `Config` of a uSync `DataType` file. Data types are
  written through the same uSync serializers that Ferry transfers use. When the configuration is left out, an existing
  data type keeps its configuration.
- **Templates use the site's view file.** A new template reads `Views/{alias}.cshtml` and never changes it. Umbraco
  takes its layout (master template) from the view's `Layout`, so create layouts first. If the view is missing, the
  template gets Umbraco's default view.
- **Groups and tabs.** `Group(...)` on a type is a group outside any tab. `Tab(...)` holds properties and groups. A
  group inside a tab has the alias `tab/group`. Use `.Alias(...)` when the stored alias isn't the one Umbraco derives
  from the name, and `.SortOrder(...)` when the order isn't the declaration order.
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

Settings that equal Umbraco's defaults are left out. Member types are not included; Ferry transfers them only with
people.

This was validated on a real client site (165 document types, 463 data types, 28 templates and 9 media types):

- A fresh content-only install ran the generated migration and pulled 6,117 items, with every schema item unchanged.
- Running the migration again changed nothing.

## Guardrails

- Set `Ferry:Full:ContentOnly` on every environment that receives transfers, so schema arrives only through
  migrations.
- If one environment runs a newer migration than another, their schema differs, and a content-only transfer is
  rejected with the items to deploy first.
- The `schema-migrations` E2E suite runs the sample migration on two real sites and checks the generated code:
  `python3 scripts/e2e/run.py --mode Full --suite schema-migrations`.
