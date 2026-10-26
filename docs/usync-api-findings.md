# Public uSync API findings

Research date: 2026-09-17. Public base uSync sources and package metadata only.
These are integration findings, not proof of a functioning Umbraco adapter.

## Version baseline

Public `uSync.BackOffice` / `uSync.Core` 17.4.2 target .NET 10; their minimum
Umbraco dependency is 17.3.0. If the adapter uses this pair, its documented minimum
must be **Umbraco 17.3.0**, not every Umbraco 17 patch. Pin the chosen packages when
the adapter is added. Current Core/Transport projects do not reference these packages.

Sources: [NuGet metadata](https://api.nuget.org/v3-flatcontainer/usync.core/17.4.2/usync.core.nuspec),
[base uSync repository and MPL-2.0 license](https://github.com/KevinJump/uSync).

## Export, report and dependencies

`ISyncService.ExportAsync` accepts an export folder, configured handler pairs and
callbacks. Import has folder, force and handler options. Per-handler reports and
`ISyncHandler.GetDependenciesAsync(Guid, DependencyFlags)` expose relevant extension
points. Inspect these APIs against the pinned package during adapter implementation.

The service's import path resolves handler settings again through a named set;
changing a cloned settings object passed in handler pairs may not enforce policy.
Use a dedicated configured set or direct handler APIs and test the effective settings.

Sources at package commit `d762d529398d5a80a94572417deba0aca7d67026`:
[ISyncService](https://github.com/KevinJump/uSync/blob/d762d529398d5a80a94572417deba0aca7d67026/uSync.BackOffice/Services/ISyncService.cs),
[ISyncHandler](https://github.com/KevinJump/uSync/blob/d762d529398d5a80a94572417deba0aca7d67026/uSync.BackOffice/SyncHandlers/Interfaces/ISyncHandler.cs),
[SyncService](https://github.com/KevinJump/uSync/blob/d762d529398d5a80a94572417deba0aca7d67026/uSync.BackOffice/Services/SyncService.cs).

## Draft-only behavior is not the default

Default content import can reproduce publication state, including publishing or
unpublishing destination content. Omitting `Info/Published` reaches a save-only
branch; setting its default false can unpublish destination content instead.
Schedules are handled independently in a second pass. Merely omitting publication
state does not prevent a future imported release schedule from publishing content.

Omitting both publication and schedule XML is still not a sufficient general policy:
the importer removes destination schedules absent from incoming XML. A tested adapter
must preserve destination scheduling deliberately, or block affected items with an
explicit explanation. Do not ship naive XML stripping as a complete draft solution.

Source: [ContentSerializer](https://github.com/KevinJump/uSync/blob/d762d529398d5a80a94572417deba0aca7d67026/uSync.Core/Serialization/Serializers/ContentSerializer.cs),
publication handling around lines 437–535 and schedule handling around 326–401.

## Media and scope

Serialized media metadata is not equivalent to transferring physical media files.
Implement a separate bounded media stream/store layer. Allowlist supported entity
handlers and reject delete/clean instructions. Do not accidentally include executable
templates, users, or unrelated server configuration in a content transfer.

Adapter acceptance requires two real Umbraco sites, not only the in-memory stores
used to prove the current protocol. Tests must cover variants, nested blocks,
circular references, schedules, and preservation of existing live content versions.
