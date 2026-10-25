import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {renderLabCatalog,renderPracticeGuide,renderHandsOnCatalog} from '../scripts/lab-catalog.mjs';
const source = JSON.parse(await readFile(new URL('../labs/foundation-catalog.json',import.meta.url),'utf8'));
const repo = '/lab-files/';
const handsOn = JSON.parse(await readFile(new URL('../labs/hands-on-catalog.json',import.meta.url),'utf8'));
test('hands-on catalog rejects unreviewed IDs, destinations and mastery claims',()=>{
  for (const mutate of [c=>c.labs[0].id='../private',c=>c.labs[1].id=c.labs[0].id,c=>c.labs[0].status='Mastered',c=>c.labs.pop()]) {
    const c=structuredClone(handsOn);mutate(c);assert.throws(()=>renderHandsOnCatalog(c,repo));
  }
  assert.throws(()=>renderHandsOnCatalog(handsOn,'https://example.test/'));
});
test('hands-on catalog escapes supplied prose and preserves pending practice',()=>{
  const c=structuredClone(handsOn);c.labs[0].title='<img src=x onerror=alert(1)>';
  const result=renderHandsOnCatalog(c,repo);
  assert.equal(result.totalCount,30);assert.equal(result.newCount,4);
  assert.ok(result.html.includes('&lt;img'));assert.ok(!result.html.includes('<img'));
  assert.equal((result.html.match(/Independent practice not yet assessed/g)||[]).length,4);
});
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
