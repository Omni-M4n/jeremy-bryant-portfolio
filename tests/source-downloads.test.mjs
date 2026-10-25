import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { lstat, mkdir, mkdtemp, readFile, rename, rm, symlink, utimes, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { basename, dirname, join, resolve } from 'node:path';
import { buildSourceDownloads } from '../scripts/source-downloads.mjs';

const config = { origin: 'https://jeremy-bryant.pages.dev', base: '/' };
const prefix = 'jeremy-bryant-pages/';
const archivePath = root => join(root, 'dist', 'downloads', 'jeremy-bryant-portfolio.zip');

async function fixture(t) {
  const parent = resolve(tmpdir(), 'jeremy-source-downloads-tests');
  await mkdir(parent, { recursive: true });
  const root = await mkdtemp(join(parent, 'fixture-'));
  t.after(async () => {
    // Only remove the exact test-owned child produced by mkdtemp.
    if (dirname(resolve(root)) !== parent || !basename(root).startsWith('fixture-') || (await lstat(root)).isSymbolicLink()) throw Error('Unsafe test cleanup path');
    await rm(root, { recursive: true, force: true });
  });
  for (const directory of ['docs', 'labs', 'scripts', 'src', 'tests', 'tools']) await mkdir(join(root, directory));
  for (const name of ['README.md', 'package.json', 'site.config.json', 'wrangler.jsonc', '.gitignore', '.gitattributes']) await writeFile(join(root, name), name === 'site.config.json' ? JSON.stringify(config) : 'Public source: ' + name + '\n');
  const labs = [];
  for (let index = 0; index < 30; index++) {
    const id = 'lab-' + String(index + 1).padStart(2, '0');
    labs.push({id,kind:'core',group:'Test practice',title:'Exercise '+(index+1),summary:'Test source page.',start_with:'Read the example.',extends:[],mode:'offline',status:'Independent practice not yet assessed'});
    await mkdir(join(root, 'labs', id));
    await writeFile(join(root, 'labs', id, 'README.md'), `# Guided exercise ${index + 1}\n\nSynthetic practice, not assessed.\n`);
    await writeFile(join(root, 'labs', id, 'lab.py'), 'print("synthetic fixture")\n');
  }
  await writeFile(join(root,'labs','release-catalog.json'),JSON.stringify({schema_version:1,labs}));
  await writeFile(join(root, 'docs', 'credits.md'), 'Upstream credit: https://www.webosbrew.org/\n');
  return { root, dist: join(root, 'dist'), config };
}

function parseZip(archive) {
  const end = archive.length - 22;
  assert.equal(archive.readUInt32LE(end), 0x06054b50);
  assert.equal(archive.readUInt16LE(end + 4), 0);
  assert.equal(archive.readUInt16LE(end + 6), 0);
  const count = archive.readUInt16LE(end + 10);
  assert.equal(archive.readUInt16LE(end + 8), count);
  assert.equal(archive.readUInt16LE(end + 20), 0);
  const start = archive.readUInt32LE(end + 16);
  assert.equal(start + archive.readUInt32LE(end + 12), end);
  const entries = new Map();
  let cursor = start;
  for (let index = 0; index < count; index++) {
    assert.equal(archive.readUInt32LE(cursor), 0x02014b50);
    assert.equal(archive.readUInt16LE(cursor + 8), 0x0800);
    assert.equal(archive.readUInt16LE(cursor + 10), 0); // Stored entries.
    assert.equal(archive.readUInt16LE(cursor + 12), 0); // Neutral time.
    assert.equal(archive.readUInt16LE(cursor + 14), 0x0021); // 1980-01-01.
    assert.equal(archive.readUInt32LE(cursor + 38), (0o100644 * 65536) >>> 0);
    const size = archive.readUInt32LE(cursor + 24);
    assert.equal(archive.readUInt32LE(cursor + 20), size);
    const nameLength = archive.readUInt16LE(cursor + 28);
    assert.equal(archive.readUInt16LE(cursor + 30), 0);
    assert.equal(archive.readUInt16LE(cursor + 32), 0);
    const name = archive.subarray(cursor + 46, cursor + 46 + nameLength).toString('utf8');
    assert.ok(name.startsWith(prefix));
    assert.ok(!name.includes('\\'));
    assert.ok(!name.split('/').some(part => part === '..' || part === '.' || part.includes(':')));
    assert.ok(!entries.has(name));
    const local = archive.readUInt32LE(cursor + 42);
    assert.equal(archive.readUInt32LE(local), 0x04034b50);
    assert.equal(archive.readUInt32LE(local + 22), size);
    assert.equal(archive.readUInt16LE(local + 26), nameLength);
    assert.equal(archive.subarray(local + 30, local + 30 + nameLength).toString('utf8'), name);
    const data = archive.subarray(local + 30 + nameLength, local + 30 + nameLength + size);
    // Independent bit-by-bit CRC implementation verifies the written payload and header.
    let crc = 0xffffffff;
    for (const byte of data) {
      crc ^= byte;
      for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
    }
    assert.equal(archive.readUInt32LE(cursor + 16), (crc ^ 0xffffffff) >>> 0);
    assert.equal(archive.readUInt32LE(local + 14), (crc ^ 0xffffffff) >>> 0);
    entries.set(name, data);
    cursor += 46 + nameLength;
  }
  assert.equal(cursor, end);
  assert.deepEqual([...entries.keys()], [...entries.keys()].sort());
  return entries;
}

test('draft packages are omitted while accepted extensions retain separate counts', async t=>{
  const context=await fixture(t);
  await mkdir(join(context.root,'labs','draft-secret'));
  await writeFile(join(context.root,'labs','draft-secret','README.md'),'UNREVIEWED_CONTENT_MUST_NOT_SHIP');
  await mkdir(join(context.root,'labs','extra-task'));
  await writeFile(join(context.root,'labs','extra-task','README.md'),'# Reviewed extra task\n');
  const path=join(context.root,'labs','release-catalog.json');
  const registry=JSON.parse(await readFile(path,'utf8'));
  registry.labs.push({...registry.labs[0],id:'extra-task',kind:'extension',extends:['lab-01']});
  await writeFile(path,JSON.stringify(registry));
  const receipt=await buildSourceDownloads(context);
  assert.deepEqual([receipt.coreCount,receipt.extensionCount,receipt.labCount],[30,1,31]);
  const entries=parseZip(await readFile(archivePath(context.root)));
  assert.ok(![...entries.keys()].some(path=>path.includes('draft-secret')));
  assert.ok(entries.has(prefix+'labs/extra-task/README.md'));
  const index=await readFile(join(context.dist,'source','index.html'),'utf8');
  assert.match(index,/30 core labs and 1 extensions/);
  assert.ok(!index.includes('draft-secret'));
});

test('a registry entry cannot silently point to a missing package',async t=>{
  const context=await fixture(t);
  const path=join(context.root,'labs','release-catalog.json');
  const registry=JSON.parse(await readFile(path,'utf8'));
  registry.labs.push({...registry.labs[0],id:'missing-lab'});
  await writeFile(path,JSON.stringify(registry));
  await assert.rejects(buildSourceDownloads(context),/Accepted lab directory missing/);
});

test('renders all 30 local lab pages and literal documents without executable markup', async t => {
  const context = await fixture(t);
  const attack = '<script>alert("test")</script> & <img src=x onerror="alert(1)">';
  await writeFile(join(context.root, 'labs', 'lab-01', 'README.md'), '# ' + attack + '\n\n[Link](javascript:alert(1))\n');
  for (const name of ['WORKED-EXAMPLE.md', 'DRILLS.md', 'PRACTICE.md']) await writeFile(join(context.root, 'labs', 'lab-01', name), '# ' + name + '\n' + attack);
  const receipt = await buildSourceDownloads(context);
  assert.equal(receipt.labCount, 30);
  assert.equal(receipt.generatedPages, 31);
  const index = await readFile(join(context.dist, 'source', 'index.html'), 'utf8');
  assert.equal((index.match(/href="\/lab-files\/lab-\d\d\/"/gu) || []).length, 30);
  assert.ok(index.includes(receipt.sha256));
  assert.ok(index.includes('Independent completion of fresh cases has not yet been assessed.'));
  for (const id of receipt.labIds) {
    const html = await readFile(join(context.dist, 'lab-files', id, 'index.html'), 'utf8');
    assert.ok(html.includes('<meta name="robots" content="noindex, nofollow, noarchive">'));
    assert.ok(html.includes(`href="https://jeremy-bryant.pages.dev/lab-files/${id}/"`));
    assert.ok(html.includes('href="/styles.css"'));
    assert.ok(html.includes('href="/source-downloads.css"'));
    assert.ok(!html.includes('<script'));
    assert.ok(!html.includes('<img'));
    assert.ok(!html.includes('style="'));
  }
  const html = await readFile(join(context.dist, 'lab-files', 'lab-01', 'index.html'), 'utf8');
  assert.ok(html.includes('&lt;script&gt;alert(&quot;test&quot;)&lt;/script&gt; &amp;'));
  assert.ok(!html.includes('href="javascript:'));
  for (const name of ['README.md', 'WORKED-EXAMPLE.md', 'DRILLS.md', 'PRACTICE.md']) assert.ok(html.includes('labs/lab-01/' + name));
});

test('hands-on instructions explain separate tooling rather than claiming offline completion', async t => {
  const context = await fixture(t);
  await rename(join(context.root,'labs','lab-01'),join(context.root,'labs','traffic-capture'));
  const path=join(context.root,'labs','release-catalog.json');
  const registry=JSON.parse(await readFile(path,'utf8'));
  registry.labs[0].id='traffic-capture';registry.labs[0].mode='hands-on';
  await writeFile(path,JSON.stringify(registry));
  await buildSourceDownloads(context);
  const html = await readFile(join(context.dist,'lab-files','traffic-capture','index.html'),'utf8');
  assert.ok(html.includes('Core lab / hands-on practice'));
  assert.ok(html.includes('requires the separate software and controlled environment'));
  assert.ok(!html.includes('Core lab / offline practice'));
});

test('archive excludes private, generated, environment, history and receipt paths', async t => {
  const context = await fixture(t);
  const excluded = ['run', 'runs', 'dist', 'node_modules', '.git', '.wrangler', 'private', 'receipts', '__pycache__', 'pycache', 'env', 'logs', '.venv'];
  for (const name of excluded) {
    await mkdir(join(context.root, 'docs', name));
    await writeFile(join(context.root, 'docs', name, 'marker.txt'), 'excluded-marker');
  }
  for (const name of ['.env', '.env.local', 'debug.log', 'secret.env', 'module.pyc', 'module.pyo', 'build-receipt.json', 'release-receipts.txt']) await writeFile(join(context.root, 'docs', name), 'excluded-marker');
  await writeFile(join(context.root, 'unlisted-root-file.txt'), 'excluded-marker');
  await mkdir(join(context.root, 'unlisted-folder'));
  await writeFile(join(context.root, 'unlisted-folder', 'marker.txt'), 'excluded-marker');
  await writeFile(join(context.root, 'labs', 'lab-01', 'fixture.bin'), Buffer.from([0, 255, 13, 10, 128]));
  const receipt = await buildSourceDownloads(context);
  const archive = await readFile(archivePath(context.root));
  const entries = parseZip(archive);
  assert.equal(entries.size, receipt.files);
  assert.equal(archive.length, receipt.bytes);
  assert.equal(createHash('sha256').update(archive).digest('hex'), receipt.sha256);
  for (const value of entries.values()) assert.ok(!value.includes(Buffer.from('excluded-marker')));
  assert.equal(entries.get(prefix + 'docs/credits.md').toString(), 'Upstream credit: https://www.webosbrew.org/\n');
  assert.deepEqual(entries.get(prefix + 'labs/lab-01/fixture.bin'), Buffer.from([0, 255, 13, 10, 128]));
  for (const required of ['README.md', 'package.json', 'site.config.json', 'wrangler.jsonc', '.gitignore', '.gitattributes']) assert.ok(entries.has(prefix + required));
});

test('excludes generated run-prefixed directories while retaining similarly named source files', async t => {
  const context = await fixture(t);
  for (const name of ['run-unfamiliar', 'runs-verification', 'run_changed', 'runs_trial', 'RUN-extra', 'RUNS_extra']) {
    const directory = join(context.root, 'labs', 'lab-01', name);
    await mkdir(directory);
    await writeFile(join(directory, 'attempt.txt'), 'excluded-practice-attempt');
  }
  for (const name of ['run-helper.py', 'runs-summary.md', 'run_contract.py', 'runs_reference.json']) await writeFile(join(context.root, 'docs', name), 'maintained source');
  for (const name of ['runtime', 'runner', 'runspec']) {
    await mkdir(join(context.root, 'docs', name));
    await writeFile(join(context.root, 'docs', name, 'README.md'), 'maintained source');
  }
  await buildSourceDownloads(context);
  const entries = parseZip(await readFile(archivePath(context.root)));
  for (const value of entries.values()) assert.ok(!value.includes(Buffer.from('excluded-practice-attempt')));
  for (const name of ['run-helper.py', 'runs-summary.md', 'run_contract.py', 'runs_reference.json']) assert.ok(entries.has(prefix + 'docs/' + name));
  for (const name of ['runtime', 'runner', 'runspec']) assert.ok(entries.has(prefix + 'docs/' + name + '/README.md'));
});

test('rebuilding identical source is byte-for-byte deterministic despite file times and existing dist', async t => {
  const context = await fixture(t);
  const first = await buildSourceDownloads(context);
  const archive = await readFile(archivePath(context.root));
  const firstPage = await readFile(join(context.dist, 'source', 'index.html'));
  await utimes(join(context.root, 'README.md'), new Date('2030-05-06T12:34:56Z'), new Date('2031-04-03T23:59:59Z'));
  await mkdir(join(context.dist, 'private'));
  await writeFile(join(context.dist, 'private', 'marker.txt'), 'excluded build output');
  const second = await buildSourceDownloads(context);
  assert.deepEqual(second, first);
  assert.deepEqual(await readFile(archivePath(context.root)), archive);
  assert.deepEqual(await readFile(join(context.dist, 'source', 'index.html')), firstPage);
  parseZip(archive);
});

test('rejects traversal destinations, malformed lab identifiers and missing required READMEs', async t => {
  const context = await fixture(t);
  await assert.rejects(buildSourceDownloads({ ...context, dist: join(context.root, '..', 'outside') }), /root\/dist/u);
  await assert.rejects(buildSourceDownloads({ ...context, dist: context.root }), /root\/dist/u);
  await assert.rejects(buildSourceDownloads({ ...context, config: { ...config, origin: 'https://example.invalid' } }), /configuration/u);
  await assert.rejects(buildSourceDownloads({ ...context, config: { ...config, base: '/elsewhere/' } }), /configuration/u);
  await rename(join(context.root, 'labs', 'lab-01'), join(context.root, 'labs', 'invalid_lab'));
  await assert.rejects(buildSourceDownloads(context), /Accepted lab directory missing/u);
  await rename(join(context.root, 'labs', 'invalid_lab'), join(context.root, 'labs', 'lab-01'));
  await rename(join(context.root, 'labs', 'lab-01', 'README.md'), join(context.root, 'labs', 'lab-01', 'NOTES.md'));
  await assert.rejects(buildSourceDownloads(context), /Missing regular lab README/u);
});

test('excludes linked source and refuses linked output directories', async t => {
  const context = await fixture(t);
  const outside = join(context.root, 'outside-allowlist');
  await mkdir(outside);
  await writeFile(join(outside, 'secret.txt'), 'private linked content');
  // Windows junctions require no administrator privilege; Unix uses directory symlinks.
  const kind = process.platform === 'win32' ? 'junction' : 'dir';
  await symlink(outside, join(context.root, 'docs', 'linked-directory'), kind);
  const receipt = await buildSourceDownloads(context);
  assert.equal(receipt.excludedSymlinks, 1);
  const entries = parseZip(await readFile(archivePath(context.root)));
  assert.ok(![...entries.keys()].some(name => name.includes('linked-directory') || name.includes('secret.txt')));
  await rename(join(context.dist, 'downloads'), join(context.dist, 'saved-downloads'));
  await symlink(outside, join(context.dist, 'downloads'), kind);
  await assert.rejects(buildSourceDownloads(context), /Unsafe generated output directory/u);
  assert.deepEqual(await readFile(join(outside, 'secret.txt'), 'utf8'), 'private linked content');
});
