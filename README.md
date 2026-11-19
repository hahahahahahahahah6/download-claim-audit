# Documentation claim auditor

This offline static checker compares documentation statements about retrieving remote bytes into local files with recognizable Python call sites. It scans the root README and Markdown below a docs directory, excluding fenced blocks; inline code counts. It parses source without executing it and excludes examples, fixtures, documentation, and symbolic links. Test evidence is reported separately. Exact phrases and listed denials determine matching; review findings in context.

```sh
download-claim-audit audit . --json
download-claim-audit audit . --fail-on medium --ignore vendor/
python3 -m download_claim_audit --version
```

Findings use these identifiers:

```text
documented-file-download-claim-false
documented-no-file-download-claim-false
```

A missing production operation is high severity, or medium when found only in tests. A denial contradicted by production code is high severity. The default threshold is high; exit status 0 means the threshold was not met, 2 means it was met, and 1 indicates a usage or I/O error. JSON includes a verdict, findings, and messages. Verbose mode adds details. Ignore prefixes may be repeated.

## Differentiation

API request auditing recognizes a GET alone; this checker additionally requires a binary write. A GET paired with a binary write can satisfy both audits. Their claim wording differs. Uploading sends bytes in the opposite direction and its calls and claims do not satisfy this audit. Web scraping fetches and parses pages; fetching alone is insufficient here. Database auditing checks connect and execute operations, and its claims differ. Storage and generation statements use different wording. Cache operations are not evidence. Importable API surface auditing checks names and arguments instead. Offline, privacy, timeout and server-sent event checks use transport calls for different questions. Extraction claims for documents and identity records also use different wording.

## Limitations

A link or button, deployment instructions, a metadata listing, or a server receiving uploads can trigger a statement without establishing the checked operation. Review the source. A GET and binary write in one module may be unrelated. Provider construction alone and unpaired provider methods do not count. A GET alone or a write alone is insufficient. In-memory responses, uploads, presigned URLs, local copies and subprocess commands are excluded. The aiohttp path is not traced. A bare urllib fetch is insufficient.

S3, Google Cloud Storage and Azure Blob Storage have paired routes. Document extraction services including Mindee, Document Intelligence, Veryfi, Document AI, Eden AI, Textract, LlamaParse, Nanonets, Docsumo, ABBYY Vantage, Rossum, Klippa, Parseur and Extend have no evidence routes here. Feed parsing and websockets are also excluded. Static pattern matching is not semantic judgment: dead code counts, unresolved aliases and invalid Python are missed, exact wording and the denial list limit matching, and each route must occur in one module.
