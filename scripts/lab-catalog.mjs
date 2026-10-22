// Contract: validate and render the supplied lab catalog; no IO or deployment.
const escape = text => text.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
const slug = value => typeof value === 'string' && /^[a-z][a-z0-9-]{1,60}$/.test(value);
const prose = value => typeof value === 'string' && value.trim().length > 0 && value.length <= 1000;
export function renderPracticeGuide(markdown) {
  return markdown.replaceAll('\r\n','\n').replace(/^#{1,3} (.+)$/gm,(_,title)=>title.toUpperCase()).replace(/^```[^\n]*\n?/gm,'').replaceAll('`','');
}
export function renderLabCatalog(catalog, github) {
  if (catalog.schema_version !== 1 || catalog.existing_labs !== 6 || !Array.isArray(catalog.tracks) || !Array.isArray(catalog.labs) || catalog.labs.length !== 20) throw Error('Expected the reviewed 20-lab expansion catalog');
  if (github !== 'https://github.com/Omni-M4n/jeremy-bryant-portfolio') throw Error('Unexpected repository destination');
  const tracks = new Set(), ids = new Set();
  for (const track of catalog.tracks) {
    if (!slug(track.id) || tracks.has(track.id) || !prose(track.title) || !prose(track.description)) throw Error('Invalid or duplicate track');
    tracks.add(track.id);
  }
  for (const lab of catalog.labs) {
    if (!slug(lab.id) || ids.has(lab.id) || !tracks.has(lab.track)) throw Error('Invalid, duplicate or ungrouped lab');
    for (const key of ['title','purpose','evidence','deliverable','prerequisites','minutes','status']) if (!prose(lab[key])) throw Error('Missing lab text: '+key);
    if (lab.status !== 'Independent practice not yet assessed') throw Error('Completion status needs an evidence review');
    ids.add(lab.id);
  }
  if ([...tracks].some(id => !catalog.labs.some(lab => lab.track === id))) throw Error('Empty track');
  const html = catalog.tracks.map(track => `<section class="case-section" id="${track.id}"><p class="eyebrow">Practice track</p><h2 class="case-section-title">${escape(track.title)}</h2><p>${escape(track.description)}</p><div class="lab-catalog">${catalog.labs.filter(lab => lab.track === track.id).map(lab => {
    const number = String(catalog.existing_labs + catalog.labs.indexOf(lab) + 1).padStart(2,'0');
    return `<details class="lab-card" id="${lab.id}"><summary><span class="eyebrow">Lab ${number} / Foundation</span><span class="lab-summary-title">${escape(lab.title)}</span></summary><p>${escape(lab.purpose)}</p><dl><dt>Start with</dt><dd>${escape(lab.prerequisites)}</dd><dt>Evidence</dt><dd>${escape(lab.evidence)}</dd><dt>Your deliverable</dt><dd>${escape(lab.deliverable)}</dd><dt>First session</dt><dd>${escape(lab.minutes)}; split it into shorter sessions as needed.</dd></dl><p class="small">Three scenarios, a worked example, a worksheet and repeatable reference checks. ${escape(lab.status)}.</p><p><a class="text-link" href="${github}/tree/main/labs/${lab.id}" target="_blank" rel="noopener noreferrer">Open the complete ${escape(lab.title.toLowerCase())} lab ↗</a></p></details>`;
  }).join('\n')}</div></section>`).join('\n');
  return {html, newCount: catalog.labs.length, totalCount: catalog.existing_labs + catalog.labs.length, ids:[...ids]};
}
