// News Image — Friday 20 November 2026 (news-image-20261120).
// Node 22, standard library only: the image is the entry.png beside this
// file, and the program copies it to /output/entry.png. The image itself is
// drawn by generate.py (Python + PIL) from the verified research for this
// day's news; this file only copies the finished bytes, so both grader runs
// write identical output.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync } from 'node:fs';
import { join } from 'node:path';

copyFileSync(new URL('./entry.png', import.meta.url), join(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png'));
