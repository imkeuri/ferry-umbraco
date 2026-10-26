# Extending Ferry

Ferry refuses what it does not understand. A property editor it has no contract for, or data a package keeps in its own
tables, blocks the transfer with a message instead of being copied half-right. This guide shows the three ways to teach
Ferry about a package:

| What the package adds | What to do | Section |
|---|---|---|
| A property editor whose value has no ids, paths or references | Declare it a **scalar** editor | [Scalar editors](#scalar-editors) |
| A property editor whose value points at pages, media or other items | Write a uSync **mapper** and declare it a **mapped** editor | [Mapped editors](#mapped-editors) |
| Data stored outside content (redirects, forms, settings rows, …) | Write a Ferry **package provider** | [Package providers](#package-providers) |
| Media files of a type Ferry does not allow | List the extension | [Media file types](#media-file-types) |

Whatever you add, register it the same way on **every** site that sends or receives it.

## Scalar editors

A scalar value is copied exactly as stored. Use this only when the value contains no site-local ids, file paths or
entity references: plain text, numbers, colours, a JSON object of settings.

```csharp
builder.AddFerryUmbracoFull(options =>
{
    options.ScalarEditors.Add("Our.ColorPicker");
});
```

or in configuration:

```json
"Ferry": { "Editors": { "ScalarEditors": [ "Our.ColorPicker" ] } }
```

If the value holds a page or media key, a scalar contract copies it without the dependency, so the page may not exist
on the destination. Use a mapped editor instead.

## Mapped editors

A mapped editor needs a uSync `ISyncMapper` that

- returns the value to export (`GetExportValueAsync`) and to import (`GetImportValueAsync`);
- reports every page and media item the value points at (`GetDependenciesAsync`), so they travel with the page and the
  review shows them.

Keys are the same on both sites after a Ferry transfer, so a value that stores keys or `umb://` UDIs can usually be
copied unchanged; the mapper's job is to report the references. Ferry checks the round trip and the declared references
before saving content.

```csharp
[HideFromTypeFinder]
public sealed class LinkCardMapper : ISyncMapper
{
    public string Name => "Link card";
    public string[] Editors => ["Our.LinkCard"];
    public bool IsMapper(PropertyType propertyType) => propertyType.PropertyEditorAlias == "Our.LinkCard";

    public Task<string?> GetExportValueAsync(object value, string editorAlias) => Task.FromResult(value?.ToString());
    public Task<string?> GetImportValueAsync(string value, string editorAlias) => Task.FromResult<string?>(value);
    public Task<string?> GetImportValueAsync(string value, string editorAlias, SyncSerializerOptions options) =>
        Task.FromResult<string?>(value);

    public Task<IEnumerable<uSyncDependency>> GetDependenciesAsync(object value, string editorAlias, DependencyFlags flags) =>
        Task.FromResult<IEnumerable<uSyncDependency>>(PageKeys(value?.ToString())
            .Select(key => new GuidUdi(Constants.UdiEntityType.Document, key))
            .Select(udi => new uSyncDependency
            {
                Name = udi.ToString(), Udi = udi, Flags = flags,
                Order = DependencyOrders.OrderFromEntityType(udi.EntityType), Level = 0
            }).ToArray());

    private static IEnumerable<Guid> PageKeys(string? value) => /* read the keys out of your stored JSON */ [];
}
```

Register the mapper and declare the editor:

```csharp
builder.WithCollectionBuilder<SyncValueMapperCollectionBuilder>().Add<LinkCardMapper>();
builder.AddFerryUmbracoFull(options => options.MappedEditors.Add("Our.LinkCard"));
```

Declaring an alias does not create a mapper: without one, content using the editor is still refused. Ferry's own
`ContentmentReferenceMapper` and `MetaMomentumMapper` are working examples.

Test the editor on two disposable sites whose local ids differ: create content on one, Send it, and check that a second
review plans it as unchanged.

## Package providers

Some packages keep data outside content, in their own tables: redirects, form definitions, banners, settings. A package
provider lets that data travel in the same transfer as the pages and media it points at.

Ferry ships two:

| Package | Provider | What travels |
|---|---|---|
| [Skybrud.Umbraco.Redirects](https://github.com/skybrud/Skybrud.Umbraco.Redirects) | `Ferry.Skybrud.Redirects`, `builder.AddFerrySkybrudRedirects()` | Redirects with their root page and destination page or media. Destination URLs must be site paths or http(s) URLs. |
| Umbraco Forms | `Ferry.Umbraco.Forms`, `builder.AddFerryUmbracoForms()` | Form definitions with their workflows, and the page a form goes to after submit. The form and theme pickers are accepted as plain values. Records, folders, prevalue sources and data sources are not transferred; a form that uses a prevalue or data source needs it on the destination first. |

```csharp
builder.AddFerryUmbracoFull();
builder.AddFerrySkybrudRedirects();
builder.AddFerryUmbracoForms();
```

Forms workflows act on the server, so every workflow and field setting is checked: a view path must stay inside the
site's views, and an address must be an http or https URL to a public host. Ferry checks the address as written; it
cannot see what a host name resolves to when Umbraco Forms later calls it.

### Turning it on

Package data is off by default, because a provider writes to tables Ferry does not otherwise touch. Turn it on on
**both** sites:

```json
"Ferry": { "Full": { "AllowPackageItemTransfer": true } }
```

Each site advertises its providers. A site that receives items for a provider it does not have refuses the transfer
before anything is written, with a message that names the provider.

### What a transfer does

- A **whole-site** transfer carries every item of every provider.
- A **selected** transfer carries the items whose pages and media are all in the selection. An item that points at
  nothing, such as a form with no page after submit, travels only in a whole-site transfer.
- Each item keeps its key on every site, shows in the review as "*ItemName*: *name*" with its changed fields, and is
  written after the pages and media it points at, inside the same apply.
- An item that points at a page or media item that is missing or in the recycle bin is left out of the export and
  logged: it is already broken on the source.
- Items are created or updated, never deleted.

### Writing a provider

Implement `IFerryPackageProvider` (namespace `Ferry.Umbraco.Packages`):

| Member | What it does |
|---|---|
| `Alias` | Stable id, lowercase letters, digits and dashes, for example `our-banners`. Never change it. |
| `ItemName` | What one item is called in the review, for example `Banner`. |
| `ExportAllAsync` | Every item on this site. |
| `ExportAsync(key)` | One item, or null. Ferry compares it with the incoming item. |
| `ValidateAsync(item)` | Checks an incoming item before anything is written; throw `InvalidOperationException` or `NotSupportedException` with a message for the reviewer. |
| `ApplyAsync(item)` | Creates or updates the item, keeping its key. |

Each item is a `FerryPackageItem(Key, Name, Data, References)`:

- `Data` is a JSON object with the item's portable settings. Leave out local integer ids, dates and anything derived,
  so an unchanged item compares equal on both sites. Ferry sorts object properties, so field order does not matter.
- `References` lists the pages (`FerryReferenceKind.Document`) and media (`FerryReferenceKind.Media`) the item needs,
  by key. Ferry checks they exist on the destination or come in the same transfer.

```csharp
public sealed class BannerProvider(IBannerService banners) : IFerryPackageProvider
{
    public string Alias => "our-banners";
    public string ItemName => "Banner";

    public Task<IReadOnlyList<FerryPackageItem>> ExportAllAsync(CancellationToken token) =>
        Task.FromResult<IReadOnlyList<FerryPackageItem>>(banners.GetAll().Select(ToItem).ToArray());

    public Task<FerryPackageItem?> ExportAsync(Guid key, CancellationToken token) =>
        Task.FromResult(banners.Get(key) is { } banner ? ToItem(banner) : null);

    public Task ValidateAsync(FerryPackageItem item, CancellationToken token) => Task.CompletedTask;

    public Task ApplyAsync(FerryPackageItem item, CancellationToken token)
    {
        var banner = banners.Get(item.Key) ?? new Banner { Key = item.Key };
        banner.Text = (string?)item.Data["text"] ?? "";
        banner.ImageKey = (string?)item.Data["image"] is { } image ? Guid.Parse(image) : null;
        banners.Save(banner);
        return Task.CompletedTask;
    }

    private static FerryPackageItem ToItem(Banner banner) => new(
        banner.Key, banner.Text,
        new JsonObject { ["text"] = banner.Text, ["image"] = banner.ImageKey?.ToString("D") },
        banner.ImageKey is { } image ? [new(FerryReferenceKind.Media, image)] : []);
}
```

Register it on both sites:

```csharp
builder.AddFerryPackageProvider<BannerProvider>();
```

Guidelines:

- **Treat incoming data as untrusted.** It came from another site. Validate every field in `ValidateAsync` and again in
  `ApplyAsync`: lengths, enums, and above all URLs (the Skybrud provider accepts only site paths and http(s) URLs).
- **Keep the key.** If the package's API gives new items a random key, set the source's key after creating it (the
  Skybrud provider updates its row in the apply's scope).
- **Map local ids.** If the package stores a page's integer id, store the key in `Data` and look up the local id when
  applying.
- **Clash with a different local item** (same URL, same alias, other key): refuse it in `ValidateAsync` with a message
  that names both.
- Payloads are limited to 256 KiB per item and 32 providers per site.

`SkybrudRedirectsProvider` in `src/Ferry.Skybrud.Redirects` is the reference implementation.

## Media file types

Ferry allows common image, document, audio, video and font types. To carry another static type, list it on both sites:

```json
"Ferry": { "Full": { "AdditionalMediaExtensions": [ ".pdn" ] } }
```

Types a browser or the server can run (`.html`, `.js`, `.svgz`, `.cshtml`, `.exe` and similar) are refused at startup.

## SQLite and large transfers

On SQLite, Umbraco's relation tracking reads and then writes after each save without taking a write lock. A commit
from another connection in between, such as one of Umbraco's background jobs, which run every few seconds, fails it
with "database is locked" after minutes of retries. Ferry keeps its own background writes out of that gap. For a large
first transfer into a SQLite site, set `Umbraco:CMS:DistributedJobs:Delay` to a few hours on the receiving site for the
transfer, or use SQL Server.
