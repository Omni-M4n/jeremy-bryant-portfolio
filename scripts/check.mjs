// Validate public output, local links, required controls and accidental disclosures.
import { readFile,readdir,stat } from 'node:fs/promises';
import { dirname,resolve,join,extname,sep } from 'node:path';
import { fileURLToPath } from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..'),dist=join(root,'dist');
async function walk(dir){let out=[];for(const e of await readdir(dir,{withFileTypes:true})){const p=join(dir,e.name);out.push(...(e.isDirectory()?await walk(p):[p]));}return out;}
const paths=await walk(dist),errors=[];
let bytes=0,links=0;
for(const path of paths){bytes+=(await stat(path)).size;if(!/\.(html|css|js|svg|txt)$/.test(path)&&!path.endsWith('_headers'))continue;const text=await readFile(path,'utf8');
for(const [name,re] of Object.entries({placeholder:/__(?:LINKEDIN_URL|SOURCE_URL|GITHUB_URL|UPDATED|HERO_DIAGRAM|LAB_CATALOG|HANDS_ON_CATALOG|LAB_COUNT|EXTENSION_COUNT|LAB_LIBRARY)__/,privatePath:/[A-Z]:\\Users\\|remote-attachments|root-audit\\private/,credential:/-----BEGIN (?:OPENSSH|RSA|EC|PRIVATE)|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}/,contactDetails:/mailto:|tel:|[\w.+-]+@(?:gmail|protonmail|outlook|hotmail)\./i}))if(re.test(text))errors.push(name+': '+path);
if(extname(path)==='.html'){
 if(!text.includes('name="robots"')||!text.includes('noindex'))errors.push('Missing noindex: '+path);
 if(/<script(?![^>]*src=)[^>]*>|\son[a-z]+\s*=|style\s*=/i.test(text))errors.push('Inline execution or style: '+path);
 for(const m of text.matchAll(/(?:href|src)="(\/[^"?#]*)(?:[?#][^"]*)?"/g)){const url=m[1];let target=resolve(dist,'.'+decodeURIComponent(url));if(url.startsWith('//') || (target!==dist&&!target.startsWith(dist+sep))){errors.push('Out-of-scope asset/link: '+url);continue;}if(url.endsWith('/'))target=join(target,'index.html');try{const item=await stat(target);if(!item.isFile())throw Error('Not a file');links++;}catch{errors.push('Missing link: '+url);}}
}}
const headers=await readFile(join(dist,'_headers'),'utf8');for(const h of ['Content-Security-Policy','X-Content-Type-Options','X-Frame-Options','Referrer-Policy','Permissions-Policy','Strict-Transport-Security','X-Robots-Tag'])if(!headers.includes(h))errors.push('Missing header '+h);
const pkg=JSON.parse(await readFile(join(root,'package.json'),'utf8'));if(pkg.dependencies||pkg.devDependencies)errors.push('Dependency posture changed; review required');
if(errors.length){console.error(JSON.stringify({status:'failed',errors},null,2));process.exitCode=1;}else console.log(JSON.stringify({status:'passed',files:paths.length,localLinks:links,totalBytes:bytes,dependencyCount:0}));
