#!/usr/bin/env node
/**
 * check-docs.mjs
 * Ensures core docs exist and are non-empty.
 */
import fs from 'node:fs';

const requiredFiles = [
  'README.md',
  'ARCHITECTURE.md',
  'MONETIZATION.md',
  'OPENAPI.yaml',
  'ROADMAP.md',
  'RISK_REGISTER.md'
];

let missing = [];
let empty = [];

for (const f of requiredFiles) {
  if (!fs.existsSync(f)) {
    missing.push(f);
  } else {
    const sz = fs.statSync(f).size;
    if (sz < 50) empty.push(f);
  }
}

if (missing.length) {
  console.error('[check-docs] FAIL: Missing files:', missing.join(', '));
  process.exit(1);
}
if (empty.length) {
  console.error('[check-docs] FAIL: Files too small:', empty.join(', '));
  process.exit(1);
}

console.log('[check-docs] PASS: All core docs present with reasonable size.');
