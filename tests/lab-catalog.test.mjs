import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {renderLabCatalog,renderPracticeGuide} from '../scripts/lab-catalog.mjs';
const source = JSON.parse(await readFile(new URL('../labs/foundation-catalog.json',import.meta.url),'utf8'));
const repo = 'https://github.com/Omni-M4n/jeremy-bryant-portfolio';
test('catalog escapes supplied prose rather than rendering markup',()=>{
  const value=structuredClone(source);value.labs[0].title='<script>test</script> "title"';
  const {html}=renderLabCatalog(value,repo);assert.ok(!html.includes('<script>'));assert.ok(html.includes('&lt;script&gt;'));
});
test('catalog rejects duplicate IDs, path traversal and unknown tracks',()=>{
  for(const mutation of [c=>c.labs[1].id=c.labs[0].id,c=>c.labs[0].id='../private',c=>c.labs[0].track='unknown']){
    const value=structuredClone(source);mutation(value);assert.throws(()=>renderLabCatalog(value,repo));
  }
});
test('catalog does not silently publish unsupported completion claims or destinations',()=>{
  const value=structuredClone(source);value.labs[0].status='independently mastered';
  assert.throws(()=>renderLabCatalog(value,repo));assert.throws(()=>renderLabCatalog(source,'https://example.test/elsewhere'));
});
test('reviewed catalog has 20 additional and 26 total distinct exercises',()=>{
  const result=renderLabCatalog(source,repo);assert.equal(result.newCount,20);assert.equal(result.totalCount,26);assert.equal(new Set(result.ids).size,20);
});
test('plain guide retains commands without exposing Markdown fence labels',()=>{
  const value='# Practice\r\n\r\n```console\r\npython lab.py cases\r\n```\r\nUse `notes.txt`.\r\n';
  assert.equal(renderPracticeGuide(value),'PRACTICE\n\npython lab.py cases\nUse notes.txt.\n');
});
