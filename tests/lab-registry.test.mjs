import test from 'node:test';
import assert from 'node:assert/strict';
import { validateRegistry, renderLibrary } from '../scripts/lab-registry.mjs';

const core = {id:'first-lab',kind:'core',group:'Network',title:'A first lab',summary:'Review a saved record.',start_with:'Read the worked example.',extends:[],mode:'offline',status:'Independent practice not yet assessed'};
const extension = {...core,id:'next-task',kind:'extension',title:'Another evidence source',extends:['first-lab']};
const registry = () => ({schema_version:1,labs:[structuredClone(core),structuredClone(extension)]});

test('an extension adds a package without inflating the core lab total',()=>{
  const result=validateRegistry(registry());
  assert.deepEqual([result.coreCount,result.extensionCount,result.totalCount],[1,1,2]);
  const html=renderLibrary(result);
  assert.match(html,/Extension \/ offline practice/);
  assert.match(html,/Builds on:/);
  assert.match(html,/href="\/lab-files\/first-lab\/"/);
});

test('invalid references, paths and unsupported learner claims fail closed',()=>{
  const changes=[r=>r.labs[1].id=r.labs[0].id,r=>r.labs[1].id='../private',r=>r.labs[1].extends=['missing-lab'],r=>r.labs[1].extends=['next-task'],r=>r.labs[0].extends=['next-task'],r=>r.labs[1].extends=[],r=>r.labs[1].status='Completed independently',r=>r.labs[1].mode='real-world-verified',r=>r.labs[1].internalNote='unreviewed'];
  for(const change of changes){const value=registry();change(value);assert.throws(()=>validateRegistry(value));}
});

test('library copy remains escaped, including group and parent names',()=>{
  const value=registry();
  value.labs[0].title='<script>untrusted</script>';
  value.labs[0].group='<img src=x onerror=alert(1)>';
  value.labs[1].summary='"<button>" & details';
  const html=renderLibrary(validateRegistry(value));
  assert.ok(!html.includes('<script>')&&!html.includes('<img ')&&!html.includes('<button>'));
  assert.match(html,/&lt;script&gt;/);
  assert.match(html,/&quot;&lt;button&gt;&quot; &amp;/);
});
