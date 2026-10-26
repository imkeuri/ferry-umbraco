# Umbraco package integration decisions

Documentation reviewed on 2026-09-17. Some older `/extending` and `/reference`
documentation links now redirect or return a suggested replacement path.

## Package layout and registration

Umbraco recommends NuGet distribution and keeping a package library, tests and an
example website in the repository. Ferry follows that layout with an
explicit .NET 10 / Umbraco 17.6.2 adapter project, with public uSync.Core 17.4.2
for schema and portable value support. Shared package metadata marks the
code under the Ferry Freeware License (free to use, closed source).

The opt-in `AddFerryUmbraco()` extension registers the constrained text store through
`IUmbracoBuilder.Services`. It does not enable network endpoints or install a
credential. The example website registers the transport separately and maps its
endpoints only when `Ferry:Enabled` is true. This avoids changing installed
sites merely because they reference the library. Scoped store instances allow the
adapter to use request-scoped Umbraco dependencies without a singleton capturing them.

`AddFerryUmbracoFull()` opts into the staged schema/language/content/media
adapter and public uSync core services. Referencing the package alone does not select
this adapter. The backoffice package adds the Ferry workspace under Settings › Synchronisation
(Overview, Sites, Packages and Advanced tabs), Send/Get actions and a top-bar queue for editors, and a
Management API; enable it with `Ferry:Backoffice:Enabled` and configure named
HTTPS destinations on the server. Neither destination credentials nor transfer
payloads are sent to the browser. The workspace's generated client uses the Umbraco
17.6 authentication context and native refresh/interceptor configuration.

Sources: [Creating a Package](https://docs.umbraco.com/umbraco-cms/extend-your-project/packages/creating-a-package),
[Example Package Repository](https://docs.umbraco.com/umbraco-cms/extending/packages/example-package-repository),
[Dependency Injection](https://docs.umbraco.com/umbraco-cms/develop-with-umbraco/application-code/backend-and-custom-logic/using-ioc),
[Composing](https://docs.umbraco.com/umbraco-cms/model-your-content/content-types-and-structure/composing).

## Draft persistence

The initial adapter uses `IContentService.Save`, not base uSync deserialization.
It never calls publication, unpublication or schedule-writing methods. The native
save result is checked. Existing target items with schedules are blocked because
their changed draft could otherwise be published by a future scheduled operation.

The pinned service implementation has a separate save path and accepts a nullable
schedule argument. Keeping schedule changes out of the payload is intentional.
This does not promise zero live-site impact: sort order and later schema/media
changes may affect rendering independently of content publication.

Historical API research used [Umbraco 17.3.2 ContentService](https://github.com/umbraco/Umbraco-CMS/blob/release-17.3.2/src/Umbraco.Core/Services/ContentService.cs).
The build and tests now target 17.6.2; that historical source link is not a compatibility claim for all 17.x versions.

## Current capability boundary

The constrained adapter remains available for invariant text properties on existing
matching document/data types. The optional full adapter implements staged schema and
language transfer, variant draft content, mapper-based references and media support.
Those implementations are distinct from acceptance: real-site fixture results and
explicit editor coverage determine what can be claimed as working. Template code,
arbitrary custom editors and unsupported tree operations must not be silently
dropped. Check current adapter validation and the verification record before deployment.

Both preview and apply run the adapter's whole-manifest preflight before any writes.
Preflight checks are repeated at write boundaries. Backoffice source export shares
the transport operation gate for snapshot and local asset staging, then releases it
before remote requests. Process-local serialization
and these checks are not a distributed transaction: external editors or another
application node can still race the operation. Real database integration and locking
must be established before a production release.

See the example website for an explicitly scoped acceptance
fixture and verification for tests actually executed.
