# Template Scanner — Sample Images

Place scanned church document images here for the `@template-scanner` agent to analyze.

## Supported Formats
- PNG, JPG, JPEG, PDF (single page)

## How It Works
1. Place a scanned document image in this directory
2. The `@template-scanner` agent analyzes the visual layout
3. It generates a YAML template definition in `templates/`
4. The template is then used by `@document-generator` for future documents

## Sample Use Cases
- Scanned 기부금영수증 (donation receipt) from another church
- Scanned 이명증서 (transfer certificate) format
- Scanned 교단 보고서 양식 (denomination report form)
- Scanned 공문 (official letter) format with church letterhead

## Current Templates (generated from analysis)
- `templates/bulletin-template.yaml` — Weekly bulletin layout
- `templates/worship-template.yaml` — Worship order layout
- `templates/receipt-template.yaml` — Donation receipt layout
- `templates/denomination-report-template.yaml` — Denomination report format
