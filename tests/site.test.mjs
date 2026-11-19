import test from 'node:test';import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';
test('contact identity and standalone public scope are fixed',async()=>{const c=JSON.parse(await readFile(new URL('../site.config.json',import.meta.url)));assert.equal(c.base,'/');assert.equal(c.origin,'https://jeremy-bryant.pages.dev');assert.equal(c.source,'/source/');assert.equal(c.github,undefined);assert.match(c.linkedin,/linkedin\.com\/in\/jeremy-bryant-61347a445\//);});
test('case study retains incomplete extension and attribution',async()=>{const html=await readFile(new URL('../dist/lg-webos-lab/index.html',import.meta.url),'utf8');assert.match(html,/Bluetooth controller behaviour had not been verified/);assert.match(html,/work of their upstream developers/);assert.match(html,/not an original exploit discovery/);});
test('production is an independent static Pages target with no existing domain routes',async()=>{const config=JSON.parse(await readFile(new URL('../wrangler.jsonc',import.meta.url)));assert.deepEqual(Object.keys(config).sort(),['compatibility_date','name','pages_build_output_dir']);assert.equal(config.name,'jeremy-bryant');assert.equal(config.pages_build_output_dir,'./dist');});
test('GRC route reaches the complete pack and does not claim an assessed result',async()=>{
  const home=await readFile(new URL('../dist/index.html',import.meta.url),'utf8');
  const grc=await readFile(new URL('../dist/security-labs/grc/index.html',import.meta.url),'utf8');
  const study=await readFile(new URL('../dist/security-labs/grc/loan-cupboard/index.html',import.meta.url),'utf8');
  const review=await readFile(new URL('../dist/security-labs/grc/public-control-review/index.html',import.meta.url),'utf8');
  const lab=await readFile(new URL('../dist/lab-files/risk-register/index.html',import.meta.url),'utf8');
  assert.match(home,/href="\/security-labs\/grc\/"/);
  assert.match(grc,/href="\/lab-files\/risk-register\/#grc-pack"/);
  assert.match(grc,/href="\/security-labs\/grc\/loan-cupboard\/"/);
  assert.match(grc,/href="\/security-labs\/grc\/public-control-review\/"/);
  assert.match(study,/Fictional, paper-only/);
  assert.match(study,/acceptance: false/);
  assert.match(study,/Exposure is not confirmed/);
  assert.match(review,/115 requests passed with zero errors/);
  assert.match(review,/account authentication, recovery and browser-level policy behaviour were outside this review/);
  assert.match(lab,/id="grc-pack"/);
  assert.match(lab,/Independent completion: \*\*not claimed\*\*/);
});
test('goal route publishes indexable metadata and first-person claim boundaries',async()=>{
  const goal=await readFile(new URL('../dist/goal/index.html',import.meta.url),'utf8');
  assert.match(goal,/<link rel="canonical" href="https:\/\/jeremy-bryant\.pages\.dev\/goal\/">/);
  assert.match(goal,/<meta name="robots" content="index, follow">/);
  assert.match(goal,/I plan to work through 30 existing labs in dependency order/);
  assert.match(goal,/13 beginner · 11 intermediate · 6 advanced/);
  assert.match(goal,/Stage 1 · 13 labs · all planned/);
  assert.match(goal,/Stage 2 · 11 labs · all planned/);
  assert.match(goal,/I will retain a synthetic packet worksheet that cites exact frames and matches each DNS question to any visible reply by endpoints, ports, DNS ID, name and type\./);
  assert.match(goal,/I will distinguish an A answer, NXDOMAIN and no visible reply\./);
  assert.match(goal,/I will use only the supplied synthetic evidence, not a live capture, and will not treat the exercise as proof of packet loss, application success, answer truth, professional use, completion or mastery\./);
  assert.match(goal,/I will retain a TCP flow table with exact frame references and sequence\/acknowledgement calculations\./);
  assert.match(goal,/distinguish an observed handshake, reset, no visible response, missing final ACK, missing initial SYN and acknowledgement mismatch\./);
  assert.match(goal,/the excerpt cannot establish full connection state or root cause/);
  assert.match(goal,/missing packets do not prove packet loss, firewall failure or server fault/);
  assert.match(goal,/an observed handshake does not prove application success/);
  assert.match(goal,/matching helper results do not prove professional use, completion or mastery/);
  assert.match(goal,/They do not describe my current ability\./);
  assert.match(goal,/I am publishing a learning intention and a route through existing practice materials\./);
  assert.match(goal,/I am not claiming that I have completed these labs, mastered their topics or used these methods in a professional role\./);
  assert.match(goal,/A tool reporting a match does not move the status by itself\./);
  assert.match(goal,/If a reviewer is unavailable, I will mark the work as awaiting review and will not call it independently demonstrated\./);
  assert.match(goal,/Helper checks can compare formats and expected decisions, but they cannot judge the quality of my reasoning or prove independent skill\./);
  assert.match(goal,/The route is a plan, not a credential, job history or completion record\./);
});
test('goal manifest is a 30-lab planned route with valid ordered dependencies',async()=>{
  const manifest=JSON.parse(await readFile(new URL('../dist/goal/manifest.json',import.meta.url),'utf8'));
  const registry=JSON.parse(await readFile(new URL('../labs/release-catalog.json',import.meta.url),'utf8'));
  const studyPlan=JSON.parse(await readFile(new URL('../labs/SUMMER-STUDY-PLAN.json',import.meta.url),'utf8'));
  assert.equal(manifest.schema_version,1);
  assert.equal(manifest.route_id,'cyber-cloud-goal');
  assert.equal(manifest.route_url,'/goal/');
  assert.equal(manifest.source_plan,'/security-labs/summer-study-plan.json');
  assert.equal(manifest.initial_status,'planned');
  assert.equal(manifest.lab_count,30);
  assert.equal(manifest.claim_boundary.statement,'I am publishing a learning intention and an evidence route. I am not claiming completion, mastery, a credential or professional experience.');
  assert.equal(manifest.claim_boundary.safe_scope,'I will use the fictional or dummy evidence and the safe boundaries stated in each lab.');
  assert.equal(manifest.claim_boundary.tool_limit,'A matching helper result can check an expected decision or format; it cannot judge my reasoning or prove independent skill.');
  const statusKeys=['planned','guided','solo','reviewed','recall'];
  assert.deepEqual(Object.keys(manifest.status_model),statusKeys);
  for(const status of statusKeys) assert.ok(typeof manifest.status_model[status]==='string'&&manifest.status_model[status].trim().length>0);
  assert.ok(typeof manifest.review_gate.statement==='string'&&manifest.review_gate.statement.trim().length>0);
  assert.ok(Array.isArray(manifest.review_gate.required_evidence));
  assert.equal(manifest.review_gate.required_evidence.length,8);
  assert.ok(manifest.review_gate.required_evidence.every(item=>typeof item==='string'&&item.trim().length>0));
  assert.ok(typeof manifest.review_gate.unavailable_reviewer==='string'&&manifest.review_gate.unavailable_reviewer.trim().length>0);
  assert.ok(Array.isArray(manifest.stages));
  assert.deepEqual(manifest.stages.map(stage=>stage.id),['beginner','intermediate','advanced']);
  assert.deepEqual(manifest.stages.map(stage=>stage.labs.length),[13,11,6]);
  const labs=manifest.stages.flatMap(stage=>{
    assert.match(stage.id,/^[a-z][a-z0-9-]*$/);
    for(const field of ['title','complexity','mastery_note']) assert.ok(typeof stage[field]==='string'&&stage[field].trim().length>0);
    assert.equal(stage.status,manifest.initial_status);
    assert.ok(Array.isArray(stage.labs));
    return stage.labs;
  });
  assert.equal(labs.length,manifest.lab_count);
  const ids=labs.map(lab=>lab.id);
  assert.deepEqual(ids,[
    'rules-of-engagement','dns-triage','access-review','login-triage','timeline-analysis','network-address-path','tcp-handshake','firewall-review','http-triage','file-integrity','backup-verification','cloud-storage-review','identity-lifecycle','mfa-review',
    'cloud-audit-triage','shared-responsibility','iam-explicit-deny','temporary-credentials','cloud-network-path','log-ingestion','logging-health','restore-drill','evidence-custody','secret-handling',
    'endpoint-triage','alert-correlation','soc-query-workbook','incident-case','containment-tabletop','incident-communications'
  ]);
  assert.deepEqual(labs.find(lab=>lab.id==='evidence-custody')?.dependencies,['file-integrity']);
  assert.deepEqual(labs.find(lab=>lab.id==='secret-handling')?.dependencies,['file-integrity']);
  const dnsTriage=labs.find(lab=>lab.id==='dns-triage');
  assert.deepEqual(dnsTriage?.dependencies,[]);
  assert.equal(dnsTriage?.status,'planned');
  assert.match(dnsTriage?.evidence.artifact,/synthetic packet worksheet/);
  assert.match(dnsTriage?.evidence.decision,/match each DNS question to any visible reply by endpoints, ports, DNS ID, name and type/);
  assert.match(dnsTriage?.evidence.decision,/use only the supplied synthetic evidence rather than claim a live capture/);
  assert.match(dnsTriage?.evidence.decision,/not treat the exercise as proof of packet loss, application success, answer truth, professional use, completion or mastery/);
  const tcpHandshake=labs.find(lab=>lab.id==='tcp-handshake');
  assert.deepEqual(tcpHandshake?.dependencies,['dns-triage']);
  assert.equal(tcpHandshake?.status,'planned');
  assert.equal(tcpHandshake?.evidence.artifact,'TCP flow table with exact frame references and sequence/acknowledgement calculations');
  assert.match(tcpHandshake?.evidence.decision,/distinguish an observed handshake, reset, no visible response, missing final ACK, missing initial SYN and acknowledgement mismatch/);
  assert.match(tcpHandshake?.evidence.decision,/cannot establish full connection state or root cause/);
  assert.match(tcpHandshake?.evidence.decision,/missing packets do not prove packet loss, firewall failure or server fault/);
  assert.match(tcpHandshake?.evidence.decision,/observed handshake does not prove application success/);
  assert.match(tcpHandshake?.evidence.decision,/matching helper results do not prove professional use, completion or mastery/);
  const mfaReview=labs.find(lab=>lab.id==='mfa-review');
  assert.deepEqual(mfaReview?.dependencies,['identity-lifecycle']);
  assert.equal(mfaReview?.status,'planned');
  assert.match(mfaReview?.evidence.artifact,/synthetic account-control worksheet/);
  assert.match(mfaReview?.evidence.decision,/does not test a real sign-in or prove control effectiveness/);
  assert.equal(new Set(ids).size,ids.length);
  const registryIds=new Set(registry.labs.map(lab=>lab.id));
  const studyIds=new Set(studyPlan.packages.map(item=>item.id));
  const positions=new Map(ids.map((id,index)=>[id,index]));
  for(const [index,lab] of labs.entries()){
    assert.ok(statusKeys.includes(lab.status));
    assert.equal(lab.status,manifest.initial_status);
    assert.ok(typeof lab.title==='string'&&lab.title.trim().length>0);
    assert.equal(lab.url,`/lab-files/${lab.id}/`);
    assert.ok(registryIds.has(lab.id),`${lab.id} is missing from the accepted lab registry`);
    assert.ok(studyIds.has(lab.id),`${lab.id} is missing from the summer study plan`);
    assert.ok(Array.isArray(lab.dependencies));
    assert.ok(typeof lab.evidence?.artifact==='string'&&lab.evidence.artifact.trim().length>0);
    assert.ok(typeof lab.evidence?.decision==='string'&&lab.evidence.decision.trim().length>0);
    for(const dependency of lab.dependencies){
      assert.ok(positions.has(dependency),`${lab.id} depends on missing goal lab ${dependency}`);
      assert.ok(positions.get(dependency)<index,`${lab.id} must follow ${dependency}`);
    }
  }
});
test('goal route and surrounding pages provide the expected wayfinding',async()=>{
  const [goal,home,labs,library,readme,wiki,goalDoc,wikiGoal]=await Promise.all([
    readFile(new URL('../dist/goal/index.html',import.meta.url),'utf8'),
    readFile(new URL('../dist/index.html',import.meta.url),'utf8'),
    readFile(new URL('../dist/security-labs/index.html',import.meta.url),'utf8'),
    readFile(new URL('../dist/security-labs/library/index.html',import.meta.url),'utf8'),
    readFile(new URL('../README.md',import.meta.url),'utf8'),
    readFile(new URL('../docs/wiki-home.md',import.meta.url),'utf8'),
    readFile(new URL('../docs/cyber-cloud-learning-goal.md',import.meta.url),'utf8'),
    readFile(new URL('../docs/wiki-cybersecurity-and-cloud-goal.md',import.meta.url),'utf8')
  ]);
  for(const href of ['/goal/manifest.json','/security-labs/library/','/security-labs/study-plan/','/source/']) assert.match(goal,new RegExp(`href="${href.replaceAll('/','\\/')}"`));
  const manifest=JSON.parse(await readFile(new URL('../dist/goal/manifest.json',import.meta.url),'utf8'));
  for(const lab of manifest.stages.flatMap(stage=>stage.labs)) assert.match(goal,new RegExp(`href="\\/lab-files\\/${lab.id}\\/"`));
  for(const page of [home,labs,library]) assert.match(page,/href="\/goal\/"/);
  assert.match(home,/I will work through 30 mapped labs/);
  assert.match(readme,/https:\/\/jeremy-bryant\.pages\.dev\/goal\//);
  assert.match(readme,/docs\/cyber-cloud-learning-goal\.md/);
  assert.match(readme,/docs\/wiki-cybersecurity-and-cloud-goal\.md/);
  assert.match(wiki,/https:\/\/jeremy-bryant\.pages\.dev\/goal\//);
  assert.match(wiki,/docs\/cyber-cloud-learning-goal\.md/);
  assert.match(readme,/I will use the prepared \[goal source note\]/);
  assert.doesNotMatch(readme,/\[public goal page\]/);
  assert.match(wiki,/prepared \[learning goal and planned 30-lab route\]/);
  assert.match(wikiGoal,/prepared, \*\*planned\*\* route through 30 existing labs/);
  for(const page of [readme,wiki,goalDoc,wikiGoal]){
    assert.match(page,/On 19 November 2026, I verified that/);
    assert.match(page,/5e51611690f21859b27c2b8bbfc624770fb5198b/);
    assert.match(page,/This confirms site\s+availability at that check only; I am keeping every lab \*\*Planned\*\*, and I am\s+not claiming completion or mastery\./);
    assert.doesNotMatch(page,/pending until I separately verify|after I separately verify|I intend to publish/);
  }
});
