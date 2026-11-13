import test from 'node:test';import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';
test('contact identity and standalone public scope are fixed',async()=>{const c=JSON.parse(await readFile(new URL('../site.config.json',import.meta.url)));assert.equal(c.base,'/');assert.equal(c.origin,'https://jeremy-bryant.pages.dev');assert.equal(c.source,'/source/');assert.equal(c.github,undefined);assert.match(c.linkedin,/linkedin\.com\/in\/jeremy-bryant-61347a445\//);});
test('case study retains incomplete extension and attribution',async()=>{const html=await readFile(new URL('../dist/lg-webos-lab/index.html',import.meta.url),'utf8');assert.match(html,/Bluetooth controller behaviour had not been verified/);assert.match(html,/work of their upstream developers/);assert.match(html,/not an original exploit discovery/);});
test('production is an independent static Pages target with no existing domain routes',async()=>{const config=JSON.parse(await readFile(new URL('../wrangler.jsonc',import.meta.url)));assert.deepEqual(Object.keys(config).sort(),['compatibility_date','name','pages_build_output_dir']);assert.equal(config.name,'jeremy-bryant');assert.equal(config.pages_build_output_dir,'./dist');});
test('GRC route reaches the complete pack and does not claim an assessed result',async()=>{
  const home=await readFile(new URL('../dist/index.html',import.meta.url),'utf8');
  const grc=await readFile(new URL('../dist/security-labs/grc/index.html',import.meta.url),'utf8');
  const study=await readFile(new URL('../dist/security-labs/grc/loan-cupboard/index.html',import.meta.url),'utf8');
  const lab=await readFile(new URL('../dist/lab-files/risk-register/index.html',import.meta.url),'utf8');
  assert.match(home,/href="\/security-labs\/grc\/"/);
  assert.match(grc,/href="\/lab-files\/risk-register\/#grc-pack"/);
  assert.match(grc,/href="\/security-labs\/grc\/loan-cupboard\/"/);
  assert.match(study,/Fictional, paper-only/);
  assert.match(study,/acceptance: false/);
  assert.match(study,/Exposure is not confirmed/);
  assert.match(lab,/id="grc-pack"/);
  assert.match(lab,/Independent completion: \*\*not claimed\*\*/);
});
