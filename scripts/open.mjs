
import {spawn} from 'node:child_process';import {fileURLToPath} from 'node:url';
const url='http://127.0.0.1:5178/';
async function available(){try{const r=await fetch(url,{signal:AbortSignal.timeout(1000)});return r.ok&&(await r.text()).includes('Mova')}catch{return false}}
if(!await available()){const child=spawn(process.execPath,[fileURLToPath(new URL('./serve.mjs',import.meta.url))],{cwd:fileURLToPath(new URL('../',import.meta.url)),detached:true,windowsHide:true,stdio:'ignore'});child.unref()}
let ready=false;for(let i=0;i<30;i++){if(await available()){ready=true;break}await new Promise(r=>setTimeout(r,300))}
if(!ready){console.error('No se pudo abrir Mova. Revisa si otro programa ocupa el puerto 5178.');process.exitCode=1}
else if(!process.argv.includes('--no-browser')){spawn('explorer.exe',[url],{windowsHide:true,detached:true,stdio:'ignore'}).unref()}
else console.log(url);
