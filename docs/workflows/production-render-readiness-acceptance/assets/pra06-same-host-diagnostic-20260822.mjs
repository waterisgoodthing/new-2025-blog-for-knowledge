#!/usr/bin/env node

import path from 'node:path'
import { fileURLToPath } from 'node:url'

const assetDir = path.dirname(fileURLToPath(import.meta.url))
process.env.PRA_RUN_ID ||= 'pra06-same-host-diagnostic-20260822'
process.env.PRA_ASSET_DIR ||= assetDir
process.env.PRA_SEED_FILE ||= path.join(assetDir, 'pra06-cookie-diagnostic-20260822-seed.py')
await import('./pra06-cookie-diagnostic-20260822.mjs')
