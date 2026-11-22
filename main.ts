// news-image-20261121 — copies the rendered front page to the output directory.
// Written for this entry (not the kit starter). Prototype run: `node main.ts`.
import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output'; // /output stands in for the grader
mkdirSync(outDir, { recursive: true }); // create it if it is missing
copyFileSync(join(dirname(fileURLToPath(import.meta.url)), 'entry.png'), join(outDir, 'entry.png'));
