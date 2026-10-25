// Contract: validate the accepted lab list and render its library. No writes or deployment.
import { readFile, lstat } from 'node:fs/promises';
import { join } from 'node:path';

const slug = value => typeof value === 'string' && /^[a-z][a-z0-9-]{1,60}$/.test(value);
const text = value => typeof value === 'string' && value.trim().length > 0 && value.length <= 1200;
const escape = value => value.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
const fields = ['id','kind','group','title','summary','start_with','extends','mode','status'];

export function validateRegistry(value) {
  if (!value || value.schema_version !== 1 || !Array.isArray(value.labs) || value.labs.length < 1 || value.labs.length > 200) throw Error('Invalid accepted lab registry');
  const ids = new Set();
  for (const lab of value.labs) {
    if (!lab || Object.keys(lab).sort().join() !== [...fields].sort().join()) throw Error('Unsupported lab fields');
    if (!slug(lab.id) || ids.has(lab.id)) throw Error('Invalid or duplicate lab ID');
    if (!['core','extension'].includes(lab.kind) || !['offline','hands-on','mixed'].includes(lab.mode)) throw Error('Invalid lab kind or mode');
    for (const key of ['group','title','summary','start_with']) if (!text(lab[key])) throw Error('Missing lab text: ' + key);
    if (lab.status !== 'Independent practice not yet assessed') throw Error('Learner status needs an evidence review');
    if (!Array.isArray(lab.extends) || lab.extends.some(id => !slug(id)) || new Set(lab.extends).size !== lab.extends.length) throw Error('Invalid extension parents');
    if (lab.kind === 'core' && lab.extends.length || lab.kind === 'extension' && !lab.extends.length) throw Error('Core and extension counts must stay separate');
    ids.add(lab.id);
  }
  const byId = new Map(value.labs.map(lab => [lab.id,lab]));
  for (const lab of value.labs) for (const parent of lab.extends) {
    if (!byId.has(parent) || byId.get(parent).kind !== 'core' || parent === lab.id) throw Error('Extension needs an accepted core parent');
  }
  return {labs:value.labs, ids:[...ids], coreCount:value.labs.filter(lab=>lab.kind==='core').length,
    extensionCount:value.labs.filter(lab=>lab.kind==='extension').length, totalCount:value.labs.length};
}

export async function readRegistry(root) {
  const path = join(root,'labs','release-catalog.json');
  const info = await lstat(path);
  if (!info.isFile() || info.isSymbolicLink() || info.nlink > 1) throw Error('Unsafe accepted lab registry');
  return validateRegistry(JSON.parse(await readFile(path,'utf8')));
}

export function renderLibrary(registry) {
  const checked = validateRegistry({schema_version:1,labs:registry.labs});
  const groups = [...new Set(checked.labs.map(lab=>lab.group))];
  return groups.map(group=>`<section class="case-section"><h2 class="case-section-title">${escape(group)}</h2><div class="lab-catalog">${checked.labs.filter(lab=>lab.group===group).map(lab=>`<details class="lab-card" id="${lab.id}"><summary><span class="eyebrow">${lab.kind==='extension'?'Extension':'Core lab'} / ${escape(lab.mode)} practice</span><span class="lab-summary-title">${escape(lab.title)}</span></summary><p>${escape(lab.summary)}</p><p><strong>Start with:</strong> ${escape(lab.start_with)}</p>${lab.extends.length?`<p><strong>Builds on:</strong> ${lab.extends.map(id=>`<a href="/lab-files/${id}/">${escape(checked.labs.find(parent=>parent.id===id).title)}</a>`).join(', ')}.</p>`:''}<p class="small">${escape(lab.status)}. Read the instructions for tools, limits and evidence to save.</p><p><a class="text-link" href="/lab-files/${lab.id}/">Read the lab and practice tasks ↗</a></p></details>`).join('\n')}</div></section>`).join('\n');
}
