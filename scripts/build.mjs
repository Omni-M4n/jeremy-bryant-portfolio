// Contract: build only this project's src into its own dist; no deployment.
import { mkdir, readFile, writeFile, cp, rm, readdir } from 'node:fs/promises';
import { resolve, dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const dist=resolve(root,'dist');
if(dirname(dist)!==root || !root.endsWith('jeremy-bryant-portfolio')) throw Error('Unexpected build directory');
const config=JSON.parse(await readFile(join(root,'site.config.json'),'utf8'));
if(config.base!=='/portfolio/') throw Error('Unexpected public scope');
for(const key of ['linkedin','github']) if(!/^https:\/\//.test(config[key])) throw Error('Invalid public link');
await rm(dist,{recursive:true,force:true});
await mkdir(join(dist,'portfolio'),{recursive:true});
await cp(join(root,'src'),join(dist,'portfolio'),{recursive:true});
async function files(dir){const out=[];for(const e of await readdir(dir,{withFileTypes:true})){const p=join(dir,e.name);out.push(...(e.isDirectory()?await files(p):[p]));}return out;}
const heroDiagram=await readFile(join(root,'src','assets','lab-system.svg'),'utf8');
for(const file of await files(join(dist,'portfolio'))){if(!/\.(html|txt)$/.test(file))continue;let text=await readFile(file,'utf8');for(const [token,value] of Object.entries({__LINKEDIN_URL__:config.linkedin,__GITHUB_URL__:config.github,__UPDATED__:config.updated,__HERO_DIAGRAM__:heroDiagram}))text=text.replaceAll(token,value);await writeFile(file,text);}
await cp(join(dist,'portfolio','404.html'),join(dist,'404.html'));
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
const inventory=(await files(dist)).map(p=>relative(dist,p).replaceAll('\\','/'));
console.log(JSON.stringify({status:'built',files:inventory.length,base:config.base,runtimeDependencies:0}));
