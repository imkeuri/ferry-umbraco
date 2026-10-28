# Umbraco package integration decisions

Based on Umbraco documentation reviewed on 2026-09-17; some older `/extending` and `/reference` links now redirect.

## Package layout and registration

Ferry uses Umbraco's recommended layout (NuGet distribution; library, tests and example website in one repository)
with a .NET 10 / Umbraco 17.6.2 adapter project, under the Ferry Freeware License (free to use, closed source).

Referencing a package changes nothing by itself:

- `AddFerryUmbraco()` registers the constrained text store (scoped, through `IUmbracoBuilder.Services`). No endpoints,
  no credential.
- `AddFerryUmbracoFull()` selects the staged schema/language/content/media adapter.
- The example website maps endpoints only when `Ferry:Enabled` is true.
- `Ferry:Backoffice:Enabled` turns on the backoffice workspace, actions, queue and Management API. Destinations are
  configured on the server; credentials and payloads never reach the browser. The client uses Umbraco 17.6's
  authentication context.

Sources: [Creating a Package](https://docs.umbraco.com/umbraco-cms/extend-your-project/packages/creating-a-package),
[Example Package Repository](https://docs.umbraco.com/umbraco-cms/extending/packages/example-package-repository),
[Dependency Injection](https://docs.umbraco.com/umbraco-cms/develop-with-umbraco/application-code/backend-and-custom-logic/using-ioc),
[Composing](https://docs.umbraco.com/umbraco-cms/model-your-content/content-types-and-structure/composing).

## Draft persistence

The adapter saves with `IContentService.Save` and checks the result. It never publishes, unpublishes or schedules,
and payloads carry no schedules. Target items that already have schedules are blocked, since a scheduled operation
could publish the changed draft. Sort order and schema/media changes can still affect the live site.

API research used [Umbraco 17.3.2 ContentService](https://github.com/umbraco/Umbraco-CMS/blob/release-17.3.2/src/Umbraco.Core/Services/ContentService.cs);
the build targets 17.6.2. This is not a compatibility claim for all 17.x versions.

## Current capability boundary

- Constrained adapter: invariant text properties on existing matching document/data types.
- Full adapter: staged schema and language transfer, variant draft content, mapper-based references and media.
- Template code, arbitrary custom editors and unsupported tree operations must never be dropped silently.

Preview and apply run a whole-manifest preflight before writing, repeated at write boundaries. Backoffice export holds
the operation gate for snapshot and asset staging, then releases it before remote requests. This is process-local,
not a distributed transaction: external editors or another node can still race an operation. Database integration and
locking must be established before a production release.

See the example website for a two-site sample.
