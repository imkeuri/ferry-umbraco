# Local validation record

Local results for the experimental v5 baseline (Umbraco 17.6.2, .NET 10). Evidence lives in ignored `artifacts/`,
so it is not in the repository or CI; no remote CI run is claimed.

| Check | Result | Evidence (`artifacts/…`) |
| --- | --- | --- |
| .NET tests | 433/433 (Core 45, Transport 147, Backoffice 116, Umbraco 125) | |
| Exact-NuGet fixture-consumer install, isolated Docker SDK 10.0 | Passed | `package-install/native-published-docker-20260925/result.json` |
| `dotnet pack … --no-restore -c Release` | `Ferry.Umbraco.0.1.0-alpha.1.nupkg` | `package-install/native-pack-no-restore-20260925/` |
| Full transfer/publication | 22/22 | `e2e/run-b5b2c4780302/results.json` |
| Source-version Content UploadField | 6/6 | `e2e/run-8fdee911be35/results.json` |
| SQL Server source-version | 4/4 | `e2e/run-148ef4ea5e5e/results.json` |
| SQL Server target culture-Media | 2/2 | `e2e/run-923dbb295bb3/results.json` |
| Clean fixture host, culture-Media Push and Pull | 2/2 | `e2e/run-d96fcf3e9db4/results.json` |
| SQL Server target culture-Media restart | 2/2 | `e2e/run-7cc1d7cd178d/results.json` |
| Backoffice browser flows (Playwright container) | 19/19, earlier package | `e2e/browser-snapshot-final/results.json` |
| Native culture-Media name read | Umbraco reads `null`; Ferry keeps the names | `e2e/run-de0c9af7479d/results.json` |

- **UploadField:** Published sends the immutable publish-time snapshot while Draft sends the overwritten file;
  repeats are `Unchanged`; a missing snapshot fails before target writes; new-content `SaveAndPublish` binds to its
  `PublishedVersionId`; an en-US-only republish carries the fr-FR snapshot forward.
- **SQL Server:** source run writes one snapshot row; target run creates the table with zero rows, as expected.
- **Culture-Media:** distinct en-US/fr-FR bytes, captions and names, unchanged replay; Push also restarts the target.
- **Browser:** predates the current commit; local Chromium only, not CI, cross-browser or accessibility evidence.
- Independent code review found no P1 or P2 issues.
- Untested: arbitrary culture-varying UploadField setups, multi-node hosting, hosted CI, production topology.
  Executable template transfer is unsupported.

## Rerunning

```sh
dotnet test Ferry.slnx -m:1
node --test src/Ferry.Backoffice/Client/*.test.mjs
```

Package E2E needs Python `cryptography`, .NET 10, Node and the E2E npm dependencies:

```sh
python3 scripts/e2e/run.py --skip-build --published-output artifacts/package-install/run-full-v5-culture-store-20260925/published --mode Full --publication --suite transfer
python3 scripts/e2e/run.py --skip-build --published-output artifacts/package-install/e2e-fixture-consumer-clean-20260925/e2e-fixture-published --mode Full --suite push-media-culture-v5
```

These reuse local published outputs (absent on other machines) and do not rebuild the package. The culture fixture
host is test-only.
