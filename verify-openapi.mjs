#!/usr/bin/env node
/**
 * verify-openapi.mjs
 * Audit Mode: fails CI if OPENAPI.yaml drifts from required runtime routes.
 * 
 * Strategy (static, no server boot):
 * - Parse OPENAPI.yaml (minimal YAML parser via regex since no deps).
 * - Ensure required paths + methods are present.
 * - Required endpoints (v1 baseline): 
 *   - GET /_api/healthz
 *   - GET /api/v1/hello/ping
 *   - POST /api/v1/hello/echo
 */
import fs from 'node:fs';

const SPEC_PATH = 'OPENAPI.yaml';
const required = {
  '/_api/healthz': ['get'],
  '/api/v1/hello/ping': ['get'],
  '/api/v1/hello/echo': ['post'],
};

function parsePaths(yamlText) {
  // Extremely lightweight YAML "paths" extractor (no external deps)
  // Looks for lines under "paths:" then indented path keys and method keys.
  const lines = yamlText.split(/\r?\n/);
  const paths = {};
  let inPaths = false;
  let currentPath = null;
  let indentPaths = 0;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!inPaths) {
      if (/^\s*paths:\s*$/.test(line)) {
        inPaths = true;
        indentPaths = line.match(/^\s*/)[0].length;
      }
      continue;
    }
    // Stop if we reach top-level section again
    if (inPaths && line.trim() && line.match(/^\S/) && line.match(/^\w/)) {
      // A new top-level key found -> exit
      break;
    }
    // Path line e.g.: "  /_api/healthz:"
    const pathMatch = line.match(/^\s{2,}([^\s][^:]+):\s*$/);
    if (pathMatch && line.trim().startsWith('/')) {
      currentPath = pathMatch[1].trim();
      paths[currentPath] = paths[currentPath] || [];
      continue;
    }
    // Method line under a path e.g.: "    get:"
    if (currentPath) {
      const methodMatch = line.match(/^\s{4,}(get|post|put|patch|delete|options|head):\s*$/i);
      if (methodMatch) {
        paths[currentPath].push(methodMatch[1].toLowerCase());
      }
    }
  }
  return paths;
}

function fail(msg) {
  console.error(`\n[verify-openapi] FAIL: ${msg}`);
  process.exit(1);
}

if (!fs.existsSync(SPEC_PATH)) {
  fail(`Spec not found at ${SPEC_PATH}`);
}

const yamlText = fs.readFileSync(SPEC_PATH, 'utf8');
const paths = parsePaths(yamlText);

// Validate required routes exist
for (const [p, methods] of Object.entries(required)) {
  if (!paths[p]) {
    fail(`Missing path in OPENAPI.yaml: ${p}`);
  }
  for (const m of methods) {
    if (!paths[p].includes(m)) {
      fail(`Missing method for ${p}: ${m.toUpperCase()}`);
    }
  }
}

console.log('[verify-openapi] PASS: Required endpoints present in OPENAPI.yaml');
