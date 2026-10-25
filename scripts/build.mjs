// Contract: refresh the generated guide mirror, then build src into this project's dist; no deployment.
import { mkdir, readFile, writeFile, cp, rm, readdir, realpath, lstat } from 'node:fs/promises';
import { resolve, dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { renderLabCatalog, renderPracticeGuide, renderHandsOnCatalog } from './lab-catalog.mjs';
import { buildSourceDownloads } from './source-downloads.mjs';
import { readRegistry, renderLibrary } from './lab-registry.mjs';
const root=await realpath(resolve(dirname(fileURLToPath(import.meta.url)),'..'));
const dist=resolve(root,'dist');
const project=JSON.parse(await readFile(join(root,'package.json'),'utf8'));
if(dirname(dist)!==root || project.name!=='jeremy-bryant-pages') throw Error('Unexpected build directory');
// Accept any checkout folder name, but never clean an output link to another location.
const previousDist=await lstat(dist).catch(error=>{if(error.code==='ENOENT')return null;throw error;});
if(previousDist && (!previousDist.isDirectory() || previousDist.isSymbolicLink())) throw Error('Unsafe build output directory');
const config=JSON.parse(await readFile(join(root,'site.config.json'),'utf8'));
const registry=await readRegistry(root);
if(config.base!=='/' || config.origin!=='https://jeremy-bryant.pages.dev' || config.source!=='/source/') throw Error('Unexpected public scope');
if(!/^https:\/\//.test(config.linkedin)) throw Error('Invalid public link');
const catalog = renderLabCatalog(JSON.parse(await readFile(join(root,'labs','foundation-catalog.json'),'utf8')),config.labSource);
const handsOn = renderHandsOnCatalog(JSON.parse(await readFile(join(root,'labs','hands-on-catalog.json'),'utf8')),config.labSource);
const originalSix=new Set(['dns-triage','login-triage','access-review','http-triage','file-integrity','firewall-review']);
for (const id of registry.ids) for (const name of originalSix.has(id)?['README.md','lab.py','test_lab.py']:['README.md','WORKED-EXAMPLE.md','DRILLS.md','lab.py','test_lab.py']) await readFile(join(root,'labs',id,name));
await writeFile(join(root,'src','security-labs','practice-guide.txt'),renderPracticeGuide(await readFile(join(root,'labs','PRACTICE-GUIDE.md'),'utf8')));
await rm(dist,{recursive:true,force:true});
await mkdir(dist,{recursive:true});
await cp(join(root,'src'),dist,{recursive:true});
async function files(dir){const out=[];for(const e of await readdir(dir,{withFileTypes:true})){const p=join(dir,e.name);out.push(...(e.isDirectory()?await files(p):[p]));}return out;}
const heroDiagram=await readFile(join(root,'src','assets','lab-system.svg'),'utf8');
for(const file of await files(dist)){if(!/\.(html|txt)$/.test(file))continue;let text=await readFile(file,'utf8');for(const [token,value] of Object.entries({__LINKEDIN_URL__:config.linkedin,__SOURCE_URL__:config.source,__UPDATED__:config.updated,__HERO_DIAGRAM__:heroDiagram,__LAB_CATALOG__:catalog.html,__HANDS_ON_CATALOG__:handsOn.html,__LAB_COUNT__:String(registry.coreCount),__EXTENSION_COUNT__:String(registry.extensionCount),__LAB_LIBRARY__:renderLibrary(registry)}))text=text.replaceAll(token,value);await writeFile(file,text);}
await writeFile(join(dist,'_headers'),`/*
  Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'; object-src 'none'; upgrade-insecure-requests
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: no-referrer
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()
  Cross-Origin-Opener-Policy: same-origin
  Strict-Transport-Security: max-age=31536000
  X-Robots-Tag: noindex, nofollow, noarchive
  Cache-Control: public, max-age=0, must-revalidate, no-transform
`);
const source = await buildSourceDownloads({root,dist,config});
const inventory=(await files(dist)).map(p=>relative(dist,p).replaceAll('\\','/'));
console.log(JSON.stringify({status:'built',files:inventory.length,base:config.base,runtimeDependencies:0,source}));
