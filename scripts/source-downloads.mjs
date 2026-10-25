// Contract: build 30 escaped lab source pages and one deterministic, allowlisted source ZIP.
// Called after src is copied into root/dist. No dependencies, network, source edits or deployment.
import { createHash } from 'node:crypto';
import { lstat, mkdir, readFile, readdir, realpath, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';

const ORIGIN = 'https://jeremy-bryant.pages.dev';
const PREFIX = 'jeremy-bryant-pages/';
const DOWNLOAD = 'downloads/jeremy-bryant-portfolio.zip';
const LAB_COUNT = 30;
const HANDS_ON = new Set(['traffic-capture', 'burp-access-control', 'snort-rule-testing', 'windows-event-investigation']);
const DIRECTORIES = ['docs', 'labs', 'scripts', 'src', 'tests', 'tools'];
const TOP_FILES = ['README.md', 'package.json', 'site.config.json', 'wrangler.jsonc', '.gitignore', '.gitattributes'];
const DOCUMENTS = ['README.md', 'WORKED-EXAMPLE.md', 'DRILLS.md', 'PRACTICE.md'];
const OMIT_COMPONENTS = new Set(['run', 'runs', 'dist', 'node_modules', '.git', '.wrangler', 'private', 'receipts', '__pycache__', 'pycache', 'env', 'logs', 'log', '.venv', 'venv']);
const escape = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');
const compare = (a, b) => a < b ? -1 : a > b ? 1 : 0;
const digest = value => createHash('sha256').update(value).digest('hex');

function safeComponent(name) {
  if (!name || name === '.' || name === '..' || /[\\/:\u0000-\u001f\u007f]/u.test(name) || /[. ]$/u.test(name)) {
    throw Error('Unsafe source path component');
  }
}

function omitted(name, directory = false) {
  const lower = name.toLowerCase();
  return OMIT_COMPONENTS.has(lower) || (directory && /^(?:run|runs)[-_]/u.test(lower)) || lower.startsWith('.env') ||
    /\.(?:pyc|pyo|log|logs|env)$/u.test(lower) ||
    /(?:^|[._-])receipts?(?:[._-]|$)/u.test(lower) ||
    lower === '.ds_store' || lower === 'thumbs.db';
}

async function statOrNull(path) {
  try { return await lstat(path); } catch (error) { if (error.code === 'ENOENT') return null; throw error; }
}

async function collectSource(root) {
  const entries = [];
  const labIds = [];
  let excludedSymlinks = 0;
  async function walk(parts) {
    const path = join(root, ...parts);
    const info = await lstat(path);
    if (info.isSymbolicLink()) { excludedSymlinks++; return; }
    if (info.isDirectory()) {
      const children = (await readdir(path, { withFileTypes: true })).sort((a, b) => compare(a.name, b.name));
      for (const child of children) {
        const name = child.name;
        safeComponent(name);
        if (omitted(name, child.isDirectory())) continue;
        const next = [...parts, name];
        if (parts.length === 1 && parts[0] === 'labs') {
          if (child.isDirectory() && !child.isSymbolicLink()) {
            if (!/^[a-z][a-z0-9-]{1,60}$/u.test(name)) throw Error('Unsafe lab identifier');
            labIds.push(name);
          }
        }
        await walk(next);
      }
    } else if (info.isFile()) {
      entries.push({ path: parts.join('/'), data: await readFile(path) });
    } else {
      throw Error('Unsupported source file type');
    }
  }
  for (const name of DIRECTORIES) {
    const info = await statOrNull(join(root, name));
    if (!info || !info.isDirectory() || info.isSymbolicLink()) throw Error('Missing or unsafe source directory: ' + name);
    await walk([name]);
  }
  for (const name of TOP_FILES) {
    const info = await statOrNull(join(root, name));
    if (!info || !info.isFile() || info.isSymbolicLink()) throw Error('Missing or unsafe source file: ' + name);
    await walk([name]);
  }
  if (labIds.length !== LAB_COUNT) throw Error(`Expected exactly ${LAB_COUNT} lab directories`);
  entries.sort((a, b) => compare(a.path, b.path));
  const folded = new Set();
  for (const { path } of entries) {
    const key = path.toLowerCase();
    if (folded.has(key)) throw Error('Source filenames collide on case-insensitive extraction');
    folded.add(key);
  }
  return { entries, labIds: labIds.sort(compare), excludedSymlinks };
}

const CRC_TABLE = Array.from({ length: 256 }, (_, index) => {
  let value = index;
  for (let bit = 0; bit < 8; bit++) value = (value & 1) ? 0xedb88320 ^ (value >>> 1) : value >>> 1;
  return value >>> 0;
});

function crc32(data) {
  let value = 0xffffffff;
  for (const byte of data) value = CRC_TABLE[(value ^ byte) & 0xff] ^ (value >>> 8);
  return (value ^ 0xffffffff) >>> 0;
}

function sourceZip(entries) {
  // Stored entries avoid compressor-version differences. All timestamps are 1980-01-01 00:00.
  if (entries.length > 65535) throw Error('Source archive exceeds classic ZIP limits');
  const localParts = [], centralParts = [];
  let offset = 0;
  for (const { path, data } of entries) {
    const name = Buffer.from(PREFIX + path, 'utf8');
    if (name.length > 65535 || data.length > 0xffffffff || offset > 0xffffffff) throw Error('Source archive exceeds classic ZIP limits');
    const crc = crc32(data);
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0);
    local.writeUInt16LE(20, 4);
    local.writeUInt16LE(0x0800, 6); // UTF-8 filenames, no encryption or data descriptor.
    local.writeUInt16LE(0x0021, 12); // DOS date: 1980-01-01.
    local.writeUInt32LE(crc, 14);
    local.writeUInt32LE(data.length, 18);
    local.writeUInt32LE(data.length, 22);
    local.writeUInt16LE(name.length, 26);
    localParts.push(local, name, data);
    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50, 0);
    central.writeUInt16LE(0x0314, 4); // Unix, ZIP 2.0; fixed regular-file mode below.
    central.writeUInt16LE(20, 6);
    central.writeUInt16LE(0x0800, 8);
    central.writeUInt16LE(0x0021, 14);
    central.writeUInt32LE(crc, 16);
    central.writeUInt32LE(data.length, 20);
    central.writeUInt32LE(data.length, 24);
    central.writeUInt16LE(name.length, 28);
    central.writeUInt32LE((0o100644 * 65536) >>> 0, 38);
    central.writeUInt32LE(offset, 42);
    centralParts.push(central, name);
    offset += local.length + name.length + data.length;
  }
  const directory = Buffer.concat(centralParts);
  if (offset > 0xffffffff || directory.length > 0xffffffff || offset + directory.length > 0xffffffff) throw Error('Source archive exceeds classic ZIP limits');
  const end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50, 0);
  end.writeUInt16LE(entries.length, 8);
  end.writeUInt16LE(entries.length, 10);
  end.writeUInt32LE(directory.length, 12);
  end.writeUInt32LE(offset, 16);
  return Buffer.concat([...localParts, directory, end]);
}

function page({ title, path, description, body }) {
  return `<!doctype html>
<html lang="en-AU">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="robots" content="noindex, nofollow, noarchive">
  <meta name="description" content="${escape(description)}">
  <title>${escape(title)} — Jeremy Bryant</title>
  <link rel="canonical" href="${ORIGIN}${path}">
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
  <link rel="stylesheet" href="/styles.css">
  <link rel="stylesheet" href="/source-downloads.css">
</head>
<body class="source-page">
<a class="skip-link" href="#main">Skip to content</a>
<header class="source-masthead container">
  <a class="brand" href="/"><span class="brand-mark" aria-hidden="true">JB<span>·</span></span><span class="brand-name">Jeremy Bryant<span>Cybersecurity portfolio</span></span></a>
  <nav class="source-navigation" aria-label="Main navigation"><a href="/">Portfolio</a><a href="/security-labs/">Security labs</a><a href="/source/"${path === '/source/' ? ' aria-current="page"' : ''}>Source &amp; downloads</a></nav>
</header>
<main class="container source-main" id="main">${body}</main>
<footer class="container source-footer"><p>Guided practice materials. Independent completion has not yet been assessed.</p><p><a href="/">Return to the portfolio</a> · <a href="/source/">Source &amp; downloads</a></p></footer>
</body>
</html>
`;
}

function titleFrom(markdown, id) {
  return markdown.match(/^#\s+(.+)$/mu)?.[1].trim() || id.replaceAll('-', ' ');
}

function labPage(id, documents) {
  const title = titleFrom(documents[0].text, id);
  const handsOn = HANDS_ON.has(id);
  const labels = { 'README.md': 'Lab instructions', 'WORKED-EXAMPLE.md': 'Worked example', 'DRILLS.md': 'Practice drills', 'PRACTICE.md': 'Practice notes' };
  const anchor = name => name.toLowerCase().replace('.md', '');
  const body = `
  <section class="source-intro">
    <p class="eyebrow">${handsOn ? 'Hands-on security exercise' : 'Offline security exercise'} / source reading</p>
    <h1>${escape(title)}</h1>
    <p>Read the supplied instructions here, then download the complete project to use the Python utilities and training materials. ${handsOn ? 'The tool workflow requires the separate software and controlled environment described below. ' : ''}These are guided practice materials; reference checks do not assess independent understanding.</p>
    <p><a class="button button-primary" href="/${DOWNLOAD}" download>Download complete source ZIP</a></p>
    <p class="source-location">Archive folder: <code>${PREFIX}labs/${id}/</code></p>
  </section>
  <nav class="source-document-nav" aria-label="Documents in this lab">${documents.map(({ name }) => `<a href="#${anchor(name)}">${labels[name]}</a>`).join('')}</nav>
  ${documents.map(({ name, text }) => `<section class="source-document" id="${anchor(name)}"><div class="source-document-heading"><h2>${labels[name]}</h2><p><code>labs/${id}/${name}</code></p></div><pre class="source-document-text">${escape(text.replaceAll('\r\n', '\n'))}</pre></section>`).join('\n')}
  <p class="source-back"><a href="/source/">Browse all ${LAB_COUNT} lab source pages</a></p>`;
  return { title, html: page({ title, path: `/lab-files/${id}/`, description: 'Readable instructions for an original guided security exercise.', body }) };
}

function indexPage(labs, receipt) {
  const body = `
  <section class="source-intro">
    <p class="eyebrow">Inspectable work / local downloads</p>
    <h1>Source &amp; downloads</h1>
    <p>The complete portfolio source includes the static website, documentation, project utilities and all ${LAB_COUNT} guided security exercises: 26 offline foundations and four hands-on workflows. Supplied records and packet fixtures are fictional; personal tool evidence must be collected separately. Independent completion of unfamiliar variants has not yet been assessed.</p>
    <p><a class="button button-primary" href="/${DOWNLOAD}" download>Download complete source ZIP</a></p>
    <p class="source-location">${receipt.files} files · ${receipt.bytes.toLocaleString('en-AU')} bytes · Standard-library Python utilities</p>
    <details class="source-integrity"><summary>Archive integrity and contents</summary><p>The ZIP contains <code>docs/</code>, <code>labs/</code>, <code>scripts/</code>, <code>src/</code>, <code>tests/</code>, <code>tools/</code> and the project README and configuration. Generated runs, local credentials, private notes, receipts and version history are excluded. Upstream attribution remains in the source.</p><p>SHA-256 checks file identity; it does not assess the exercises or the learner.</p><pre>${receipt.sha256}</pre></details>
  </section>
  <section class="source-start" aria-labelledby="source-start-title">
    <h2 id="source-start-title">Run it locally</h2>
    <p>Extract the whole archive so the labs retain their shared modules. The exercises require Python 3.10 or later. The website build requires a current Node.js release. The hands-on labs also need the separate security tools and local environment described in each README. Read the root <code>README.md</code> and the chosen lab's README before running commands.</p>
    <pre><code>python -m zipfile -e jeremy-bryant-portfolio.zip .
cd jeremy-bryant-pages
node scripts/build.mjs</code></pre>
    <p>The website build writes a local <code>dist/</code> folder. It does not publish a site or connect to a lab target.</p>
  </section>
  <section class="source-labs" aria-labelledby="source-labs-title">
    <div class="source-section-heading"><h2 id="source-labs-title">Read a lab before downloading</h2><p>${LAB_COUNT} exercises · Instructions and practice documents</p></div>
    <ol class="source-lab-list">${labs.map(({ id, title }, index) => `<li><a href="/lab-files/${id}/"><span class="source-lab-number" aria-hidden="true">${String(index + 1).padStart(2, '0')}</span><span>${escape(title)}</span><span aria-hidden="true">↗</span></a></li>`).join('\n')}</ol>
  </section>`;
  return page({ title: 'Source & downloads', path: '/source/', description: `Download the portfolio source and read all ${LAB_COUNT} guided lab instructions locally.`, body });
}

async function safeWrite(dist, path, content) {
  const parts = path.split('/');
  for (const name of parts) safeComponent(name);
  let directory = dist;
  for (const name of parts.slice(0, -1)) {
    directory = join(directory, name);
    const info = await statOrNull(directory);
    if (info && (info.isSymbolicLink() || !info.isDirectory())) throw Error('Unsafe generated output directory');
    if (!info) await mkdir(directory);
  }
  const output = join(directory, parts.at(-1));
  const info = await statOrNull(output);
  if (info && (info.isSymbolicLink() || !info.isFile() || info.nlink > 1)) throw Error('Unsafe generated output file');
  await writeFile(output, content);
}

export async function buildSourceDownloads({ root, dist, config }) {
  if (typeof root !== 'string' || typeof dist !== 'string' || !config || config.origin !== ORIGIN || config.base !== '/') throw Error('Unexpected source-download build configuration');
  root = resolve(root);
  dist = resolve(dist);
  if (dist !== join(root, 'dist')) throw Error('Source downloads must be written to root/dist');
  const sourceInfo = await lstat(root);
  if (!sourceInfo.isDirectory() || sourceInfo.isSymbolicLink()) throw Error('Unsafe source root');
  const outputInfo = await statOrNull(dist);
  if (outputInfo && (!outputInfo.isDirectory() || outputInfo.isSymbolicLink())) throw Error('Unsafe dist directory');
  const { entries, labIds, excludedSymlinks } = await collectSource(await realpath(root));
  const source = new Map(entries.map(entry => [entry.path, entry.data]));
  const pages = labIds.map(id => {
    const documents = DOCUMENTS.filter(name => source.has(`labs/${id}/${name}`)).map(name => ({ name, text: source.get(`labs/${id}/${name}`).toString('utf8') }));
    if (documents[0]?.name !== 'README.md') throw Error('Missing regular lab README: ' + id);
    return { id, ...labPage(id, documents) };
  });
  const archive = sourceZip(entries);
  const receipt = { files: entries.length, sha256: digest(archive), bytes: archive.length, labCount: pages.length, labIds, downloadPath: '/' + DOWNLOAD, generatedPages: pages.length + 1, excludedSymlinks };
  if (!outputInfo) await mkdir(dist);
  await safeWrite(dist, DOWNLOAD, archive);
  for (const { id, html } of pages) await safeWrite(dist, `lab-files/${id}/index.html`, html);
  await safeWrite(dist, 'source/index.html', indexPage(pages, receipt));
  return receipt;
}
