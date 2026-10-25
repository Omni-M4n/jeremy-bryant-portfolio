// Contract: node scripts/verify-live.mjs NEW_RECEIPT. Read-only HTTPS checks against this site's configured origin.
import {readFile,writeFile,readdir,access} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,resolve,join,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..'),dist=join(root,'dist');
const receipt=process.argv[2];
if(!receipt)throw Error('Supply a new receipt path outside dist');
const output=resolve(receipt);
if(output.startsWith(dist))throw Error('Receipt must not be published');
try{await access(output);throw Error('Receipt already exists');}catch(e){if(e.code!=='ENOENT')throw e;}
const config=JSON.parse(await readFile(join(root,'site.config.json'),'utf8'));
if(config.origin!=='https://jeremy-bryant.pages.dev')throw Error('Unexpected origin');
async function walk(dir){let out=[];for(const e of await readdir(dir,{withFileTypes:true})){const p=join(dir,e.name);if(e.isSymbolicLink())throw Error('Unexpected symlink');out.push(...(e.isDirectory()?await walk(p):[p]));}return out;}
const sha=data=>createHash('sha256').update(data).digest('hex');
const checks=[];
for(const file of await walk(dist)){
  const name=relative(dist,file).replaceAll('\\','/');
  if(name.startsWith('_') || name==='404.html')continue;
  const path=name==='index.html'?'/':'/'+name.replace(/\/index\.html$/,'/');
  checks.push({path,status:200,sha256:sha(await readFile(file))});
}
for(const path of ['/absent-page-for-release-check/','/.git/config','/.env','/private/','/wrangler.jsonc','/labs/foundation_runtime.py'])checks.push({path,status:404});
const results=[],errors=[];
const required=['content-security-policy','x-content-type-options','x-frame-options','referrer-policy','permissions-policy','strict-transport-security','x-robots-tag'];
let next=0;
async function worker(){while(next<checks.length){const item=checks[next++],url=config.origin+item.path;try{
  const response=await fetch(url,{headers:{'Cache-Control':'no-cache'},signal:AbortSignal.timeout(40000)});
  const data=Buffer.from(await response.arrayBuffer());
  const actual=sha(data),headers=Object.fromEntries(response.headers.entries());
  const failure=[];
  if(response.status!==item.status)failure.push('status');
  if(item.sha256 && actual!==item.sha256)failure.push('content hash');
  if(new URL(response.url).origin!==config.origin)failure.push('redirect origin');
  for(const header of required)if(!headers[header])failure.push('missing '+header);
  if(!headers['x-robots-tag']?.includes('noindex'))failure.push('indexing policy');
  if(item.path.endsWith('.zip')&&!headers['content-type']?.includes('application/zip'))failure.push('download MIME');
  if(failure.length)errors.push({path:item.path,failures:failure});
  results.push({path:item.path,status:response.status,sha256:actual,matchesLocal:item.sha256?actual===item.sha256:null,bytes:data.length,headers,failures:failure});
}catch(e){errors.push({path:item.path,error:e.message});}}}
await Promise.all(Array.from({length:4},worker));
results.sort((a,b)=>a.path.localeCompare(b.path));
await writeFile(output,JSON.stringify({origin:config.origin,checkedAt:new Date().toISOString(),status:errors.length?'failed':'passed',checks:checks.length,errors,results},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({status:errors.length?'failed':'passed',checks:checks.length,exactMatches:results.filter(r=>r.matchesLocal).length,errors}));
if(errors.length)process.exitCode=1;
