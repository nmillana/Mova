
import http from 'node:http';import fs from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../dist/',import.meta.url)),port=5178;
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.woff2':'font/woff2','.woff':'font/woff','.svg':'image/svg+xml','.png':'image/png','.json':'application/json'};
const server=http.createServer(async(req,res)=>{
 try{let pathname=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);if(pathname==='/health'){res.writeHead(200,{'Content-Type':'application/json'});res.end('{"app":"mova","ok":true}');return}
 const file=path.resolve(root,'.'+(pathname==='/'?'/index.html':pathname));
 if(!file.startsWith(path.resolve(root)+path.sep)){res.writeHead(403);res.end();return}
 const data=await fs.readFile(file);res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream','Cache-Control':'no-cache','Referrer-Policy':'strict-origin-when-cross-origin','X-Content-Type-Options':'nosniff'});res.end(data);
 }catch{res.writeHead(404);res.end('No encontrado')}
});
server.on('error',err=>{console.error(err.code==='EADDRINUSE'?'El puerto 5178 ya está en uso.':err.message);process.exitCode=1});
server.listen(port,'127.0.0.1',()=>console.log('Mova disponible en http://127.0.0.1:'+port));
