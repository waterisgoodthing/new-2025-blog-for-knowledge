# Reserved API Contract

Batch 6 defines no live API implementation. The following are reserved shapes for a later approved batch and must not be added now.

## Future AI Status

`GET /api/admin/ai/status` (reserved, not implemented)

```json
{
  "enabled": false,
  "provider": null,
  "model": null,
  "message": "AI is not enabled in the MVP"
}
```

## Future OCR Status

`GET /api/admin/attachments/{id}/ocr-status` (reserved, not implemented)

```json
{
  "attachment_id": "uuid",
  "available": false,
  "status": "not_available",
  "message": "OCR is not enabled in the MVP"
}
```

These examples are documentation only. No request must be made by Batch 6 UI, and no status may be persisted.

## Security

Any future endpoint must use backend `get_current_admin`; `AuthGate` is not sufficient. Public pages must never call these reserved endpoints.
