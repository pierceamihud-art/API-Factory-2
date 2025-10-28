# Premium Catalog — quick README

Files added by this change:

- `docs/premium_catalog.md` — Human-readable catalog listing each Premium API, tier, short description, compliance alignment, and recommended controls.
- `compliance/premium_matrix.csv` — Machine-friendly CSV (API,Tier,Feature,ComplianceAreas,PrimaryControls,Notes) suitable for spreadsheets or GRC import.
- `openapi/premium-apis.yaml` — Vendor-extension style OpenAPI companion file; contains `x-premium-apis` entries mapping APIs to compliance areas and recommended controls.

How to use

- Read the catalog for a product/legal-friendly summary.
- Open the CSV in Excel/Sheets for filtering and integration into a GRC spreadsheet.
- Use the `openapi/premium-apis.yaml` as a vendor-extensions file to incorporate compliance notes into API specs (e.g., copy `x-premium-apis` entries into service OpenAPI files or programmatically read them).

Quick validations performed

- Files were added to `docs/`, `compliance/`, and `openapi/` directories.
- Project test suite was executed to ensure no immediate breakage (see test output in workspace terminal).

Next steps (optional)

- Add owner, contact, estimated dev effort, and status columns to the CSV.
- Expand `openapi/premium-apis.yaml` to include `paths` for each API or attach `x-compliance` per path in your production specs.
- Integrate with a GRC tool (Archer, OneTrust) by exporting CSV or using the YAML as structured input.

If you'd like, I can now:
- create filter views (e.g., only HIPAA-related APIs),
- add owners and SLOs, or
- convert the YAML into an OpenAPI vendor extension in `app/` endpoints as examples.
