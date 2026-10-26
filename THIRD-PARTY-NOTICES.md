# Third-party notices

Ferry is proprietary freeware (see `LICENSE`). It uses the packages below as unmodified
NuGet dependencies; their licenses remain those of their respective authors and are not
affected by Ferry's license.

## uSync.Core 17.4.2

- Author: Kevin Jump / Jumoo; package copyright: Jumoo @ 2013–2026.
- License: [Mozilla Public License 2.0](https://licenses.nuget.org/MPL-2.0).
- [Upstream source](https://github.com/KevinJump/uSync8/tree/d762d529398d5a80a94572417deba0aca7d67026).
- Used as an unmodified NuGet dependency for its public schema serializers and
  property value mappers. Ferry's draft-content writer and site-to-site
  protocol are separate original implementations.

## uSync.BackOffice 17.4.2

- Author: Kevin Jump / Jumoo; package copyright: Jumoo @ 2013–2026.
- License: [Mozilla Public License 2.0](https://licenses.nuget.org/MPL-2.0).
- [Upstream source](https://github.com/KevinJump/uSync/tree/d762d529398d5a80a94572417deba0aca7d67026).
- Used as an unmodified NuGet dependency to register the public base-uSync
  services, handlers and normal save/export lifecycle in the Full integration.
  Ferry retains its guarded draft-write and explicit-publication paths;
  this does not include the commercial uSync.Complete package.
- License and source identity checked against the official NuGet 17.4.2 metadata.

## Umbraco CMS 17.6.2

- Author: Umbraco; package copyright: Copyright © Umbraco 2026.
- License: [MIT](https://licenses.nuget.org/MIT).
- [Upstream source](https://github.com/umbraco/Umbraco-CMS/tree/7415e8cd566ce8a2ecf7918117e7d11fd09d3778).

These versions and license identifiers were verified against restored package
metadata. NuGet retains each dependency's own metadata and notices; this document
does not replace the licenses of transitive dependencies.

Ferry is an independent product. It does not include the
commercial uSync.Complete package, its proprietary implementation, or its branding,
and is not an official Jumoo or Umbraco product.

## Hey API generated fetch client runtime

The Backoffice dashboard includes generated fetch client runtime code from
`@hey-api/openapi-ts` 0.99.0. [Upstream source](https://github.com/hey-api/openapi-ts).
Its MIT license notice follows and is also distributed alongside the dashboard as
`App_Plugins/Ferry/hey-api-LICENSE.txt`.

MIT License

Copyright (c) Hey API

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
