# Extending Ferry

Ferry refuses what it does not understand: a property editor without a contract, or data a package keeps in its own
tables, blocks the transfer with a message rather than being copied half-right. To teach Ferry about a package:

| What the package adds | What to do | Section |
|---|---|---|
| A property editor whose value has no ids, paths or references | Declare it a **scalar** editor | [Scalar editors](#scalar-editors) |
| A property editor whose value points at pages, media or other items | Register a value **mapper** (`IFerryValueMapper`) | [Mapped editors](#mapped-editors) |
| Data stored outside content (redirects, forms, settings rows, …) | Write a Ferry **package provider** | [Package providers](#package-providers) |
| Media files of a type Ferry does not allow | List the extension | [Media file types](#media-file-types) |

Register everything the same way on **every** site that sends or receives it.

## Scalar editors

Scalar values are copied exactly as stored. Use only for values with no site-local ids, file paths or entity
references (text, numbers, colours, a JSON settings object). A page or media key in a scalar value is copied without
its dependency; use a mapped editor instead.

```csharp
builder.AddFerryUmbracoFull(options => options.ScalarEditors.Add("Our.ColorPicker"));
```

or:

```json
"Ferry": { "Editors": { "ScalarEditors": [ "Our.ColorPicker" ] } }
```

## Mapped editors

A value mapper returns the value to send and the value to store, and reports every page and media item the value
points at, so they travel with the page and show in the review. Keys match on both sites after a transfer, so values
storing keys or `umb://` UDIs can usually be copied unchanged; the mapper's main job is reporting references. Ferry
checks the round trip and declared references before saving.

Built-in mappers cover Umbraco's pickers, Multi URL Picker, rich text, Block List, Block Grid, Single Block,
Contentment and MetaMomentum. For your own editor, implement `IFerryValueMapper` (`Ferry.Umbraco.Values`):

```csharp
public sealed class LinkCardMapper : IFerryValueMapper
{
    public IReadOnlyCollection<string> Editors { get; } = ["Our.LinkCard"];

    // Keys are the same on both sites, so the stored value travels unchanged.
    public Task<string?> ToPortableAsync(object value, FerryValueContext context) => Task.FromResult(value?.ToString());
    public Task<object?> FromPortableAsync(string portable, FerryValueContext context) => Task.FromResult<object?>(portable);

    // Every page and media item the value points at.
    public Task<IReadOnlyCollection<GuidUdi>> ReferencesAsync(object value, FerryValueContext context) =>
        Task.FromResult<IReadOnlyCollection<GuidUdi>>(PageKeys(value?.ToString())
            .Select(key => new GuidUdi(Constants.UdiEntityType.Document, key)).ToArray());

    private static IEnumerable<Guid> PageKeys(string? value) => /* read the keys out of your stored JSON */ [];
}
```

Registering it also opts the editor in:

```csharp
builder.AddFerryValueMapper<LinkCardMapper>();
```

- `FerryValueContext.Values` maps nested values, such as a block's properties.
- An alias in `MappedEditors` without a registered mapper is still refused.
- Test on two disposable sites with different local ids: create content, Send it, and check a second review plans it
  as unchanged.

## Package providers

A package provider carries data a package keeps in its own tables (redirects, forms, banners, settings) in the same
transfer as the pages and media it points at. Ferry ships two:

| Package | Provider | What travels |
|---|---|---|
| [Skybrud.Umbraco.Redirects](https://github.com/skybrud/Skybrud.Umbraco.Redirects) | `Ferry.Skybrud.Redirects`, `builder.AddFerrySkybrudRedirects()` | Redirects with their root page and destination page or media. Destination URLs must be site paths or http(s) URLs. |
| Umbraco Forms | `Ferry.Umbraco.Forms`, `builder.AddFerryUmbracoForms()` | Form definitions with workflows and the page shown after submit. Form and theme pickers travel as plain values. Records, folders, prevalue sources and data sources are not transferred; a form using a prevalue or data source needs it on the destination first. |

```csharp
builder.AddFerryUmbracoFull();
builder.AddFerrySkybrudRedirects();
builder.AddFerryUmbracoForms();
```

Forms workflows act on the server, so every workflow and field setting is checked: a view path must be a Razor view
in the Forms email template folder (`Forms/Emails/`), and an address must be an http or https URL to a public host. A
*Save as an XML file* workflow may only write `xml`, `txt` or `csv` files. Ferry checks the address as written; it
cannot see what a host name resolves to when Umbraco Forms later calls it.

### Turning it on

Off by default, because providers write to tables Ferry otherwise leaves alone. Enable on **both** sites:

```json
"Ferry": { "Full": { "AllowPackageItemTransfer": true } }
```

A site receiving items for a provider it lacks refuses the transfer before writing anything, naming the provider.

### What a transfer does

- **Whole-site** transfers carry every item of every provider.
- **Selected** transfers carry items whose pages and media are all selected. Items pointing at nothing (e.g. a form
  with no after-submit page) travel only in whole-site transfers.
- Items keep their key, show in the review as "*ItemName*: *name*" with changed fields, and are written after the pages
  and media they point at, in the same apply.
- Items pointing at missing or recycled pages or media are left out of the export and logged.
- Items are created or updated, never deleted.

### Writing a provider

Implement `IFerryPackageProvider` (`Ferry.Umbraco.Packages`):

| Member | What it does |
|---|---|
| `Alias` | Stable id: lowercase letters, digits, dashes, e.g. `our-banners`. Never change it. |
| `ItemName` | What one item is called in the review, e.g. `Banner`. |
| `ExportAllAsync` | Every item on this site. |
| `ExportAsync(key)` | One item or null; compared with the incoming item. |
| `ValidateAsync(item)` | Checks an incoming item before anything is written; throw `InvalidOperationException` or `NotSupportedException` with a message for the reviewer. |
| `ApplyAsync(item)` | Creates or updates the item, keeping its key. |

Each item is a `FerryPackageItem(Key, Name, Data, References)`:

- `Data`: JSON object of portable settings. Omit local integer ids, dates and derived values so unchanged items compare
  equal. Property order does not matter.
- `References`: pages (`FerryReferenceKind.Document`) and media (`FerryReferenceKind.Media`) the item needs, by key.
  They must exist on the destination or come in the same transfer.

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

Register on both sites:

```csharp
builder.AddFerryPackageProvider<BannerProvider>();
```

Guidelines:

- **Treat incoming data as untrusted.** Validate every field in `ValidateAsync` and again in `ApplyAsync`: lengths,
  enums, and especially URLs (the Skybrud provider accepts only site paths and http(s) URLs).
- **Keep the key.** If the package assigns random keys, set the source key after creating (the Skybrud provider
  updates its row in the apply's scope).
- **Map local ids.** Store page keys in `Data` and look up the local id when applying.
- **Refuse clashes** with a different local item (same URL or alias, other key) in `ValidateAsync`, naming both.
- Limits: 256 KiB per item, 32 providers per site.

Reference implementation: `SkybrudRedirectsProvider` in `src/Ferry.Skybrud.Redirects`.

## Media file types

Ferry allows common image, document, audio, video and font types. Add others on both sites:

```json
"Ferry": { "Full": { "AdditionalMediaExtensions": [ ".pdn" ] } }
```

Types a browser or server can run (`.html`, `.js`, `.svgz`, `.cshtml`, `.exe` and similar) are refused at startup.

## SQLite and large transfers

On SQLite, Umbraco's relation tracking reads then writes after each save without a write lock, so a commit from
another connection in between (e.g. Umbraco's background jobs, every few seconds) fails it with "database is locked"
after minutes of retries. Ferry keeps its own background writes out of that gap. For a large first transfer into a
SQLite site, set `Umbraco:CMS:DistributedJobs:Delay` to a few hours on the receiving site, or use SQL Server.
