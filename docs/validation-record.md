# Local validation record

Recorded local results for the experimental v5 Umbraco 17.6.2 / .NET 10 baseline:

- .NET: 433/433 ordinary tests (Core 45, Transport 147, Backoffice 116, Umbraco 125).
- Fresh exact-NuGet fixture-consumer package install passed with an isolated Docker
  SDK 10.0 after the host sandbox denied restore access to
  `~/.dotnet/sdk/10.0.201/trustedroots/codesignctl.pem`:
  `artifacts/package-install/native-published-docker-20260925/result.json`.
  This is current local package evidence; it does not establish hosted CI.
- `dotnet pack src/Ferry.Umbraco/Ferry.Umbraco.csproj --no-restore -c Release`
  succeeded and created the local package
  `artifacts/package-install/native-pack-no-restore-20260925/Ferry.Umbraco.0.1.0-alpha.1.nupkg`.
- Exact-package Full transfer/publication: 22/22
  (`artifacts/e2e/run-b5b2c4780302/results.json`), including the new greenfield
  template-rejection case. Executable template transfer remains unsupported.
- Exact-package two-site source-version Content UploadField: 6/6
  (`artifacts/e2e/run-8fdee911be35/results.json`). It verifies immutable
  publish-time snapshot export when Umbraco's deterministic same-name UploadField
  path is later overwritten with draft B, so Published transfers A while Draft
  transfers B; it also verifies repeat `Unchanged` and missing-snapshot preview
  failure before a target write. It also verifies native new-content `SaveAndPublish`:
  pre-version immutable bytes bind to the assigned `PublishedVersionId`, transfer
  exactly, and replay unchanged. Preexisting publications without a snapshot fail
  closed on Published export. The same run also
  verifies an en-US-only partial republish carries an untouched immutable fr-FR
  snapshot forward after the mutable fr-FR file path is overwritten. Arbitrary
  culture-varying UploadField configurations remain untested.
- Astra review of this production change found no P1 or P2 issues.
- Exact-package SQL Server source-version E2E: 4/4
  (`artifacts/e2e/run-148ef4ea5e5e/results.json`). The source database contains one
  `cmsCommunitySyncPublishedContentAsset` row and
  `PK_cmsCommunitySyncPublishedContentAsset`, proving the bounded saved-source
  snapshot write/schema path.
- Exact-package SQL Server target culture-Media Push/Pull: 2/2
  (`artifacts/e2e/run-923dbb295bb3/results.json`). The target database created the
  snapshot table and primary key, with zero rows as expected because this scenario
  has no Published-source UploadField capture. Culture-varying UploadField,
  multi-node hosting, hosted CI, and production topology are untested.
- Clean exact-NuGet fixture host with culture-varying Media: Push and administrator
  Pull 2/2 (`artifacts/e2e/run-d96fcf3e9db4/results.json`), after a clean fixture
  consumer package installation at
  `artifacts/package-install/e2e-fixture-consumer-clean-20260925/result.json`.
  Push verifies distinct en-US/fr-FR PNG bytes, captions, durable culture names,
  unchanged replay, and a target process restart. Pull verifies the same transfer
  values and bytes but does not restart the target.
- Package-installed SQL Server-target culture-Media restart suite: 2/2
  (`artifacts/e2e/run-7cc1d7cd178d/results.json`).
- Packaged native Backoffice browser flow: three suites passed 19/19 against two
  disposable Umbraco sites in a Playwright MCP image container using a browse peer
  policy (`artifacts/e2e/browser-snapshot-final/results.json`). This earlier-package
  exact-package result predates the current production commit. The earlier macOS Chrome abort and a pull-only 17/19 fixture
  run were harness outcomes, not the final browser result. This is local Chromium-container evidence, not hosted CI,
  cross-browser, accessibility, or production-topology validation.
- Native Umbraco 17.6.2 reads culture-varying Media names as `null` after a fresh
  Media read (`artifacts/e2e/run-de0c9af7479d/results.json`). Ferry's
  migration-owned store preserves those names for transfer; native API/Backoffice
  display is not claimed.

The evidence files are under ignored `artifacts/` and are not committed or available
to CI. No remote CI run is claimed here.

From the repository root, the tracked test commands are:

```sh
dotnet test Ferry.slnx -m:1
node --test src/Ferry.Backoffice/Client/*.test.mjs
```

The installed-package E2E launcher requires Python `cryptography`, .NET 10, Node,
and the E2E npm dependencies. With the retained ignored package outputs, rerun the
v5 scenarios with:

```sh
python3 scripts/e2e/run.py --skip-build --published-output artifacts/package-install/run-full-v5-culture-store-20260925/published --mode Full --publication --suite transfer
python3 scripts/e2e/run.py --skip-build --published-output artifacts/package-install/e2e-fixture-consumer-clean-20260925/e2e-fixture-published --mode Full --suite push-media-culture-v5
```

These commands reuse local published consumers and create fresh disposable sites;
they do not reproduce a clean package build. `artifacts/` is ignored, may be absent
on another machine, and can contain disposable fixture data. The culture fixture
host is intentionally test-only; production consumers exclude fixture support.
