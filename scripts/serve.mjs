import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const portIndex = process.argv.indexOf('--port');
const dirIndex = process.argv.indexOf('--dir');
const port = Number(portIndex >= 0 ? process.argv[portIndex + 1] : process.env.PORT || 4173);
const publicDir = path.resolve(dirIndex >= 0 ? process.argv[dirIndex + 1] : path.join(root, 'site', 'public'));
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8', '.csv': 'text/csv; charset=utf-8', '.txt': 'text/plain; charset=utf-8', '.svg': 'image/svg+xml' };

const server = http.createServer((request, response) => {
  if (!['GET', 'HEAD'].includes(request.method)) {
    response.writeHead(405, { Allow: 'GET, HEAD' });
    response.end('Method not allowed');
    return;
  }
  let pathname;
  try { pathname = decodeURIComponent(new URL(request.url, 'http://preview.local').pathname); } catch { response.writeHead(400); response.end('Bad request'); return; }
  if (pathname.endsWith('/')) pathname += 'index.html';
  const file = path.resolve(publicDir, `.${pathname}`);
  if (!file.startsWith(publicDir + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
    const fallback = path.join(publicDir, '404.html');
    response.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
    if (request.method === 'HEAD' || !fs.existsSync(fallback)) response.end(); else fs.createReadStream(fallback).pipe(response);
    return;
  }
  response.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-cache', 'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer' });
  if (request.method === 'HEAD') response.end(); else fs.createReadStream(file).pipe(response);
});
server.listen(port, '0.0.0.0', () => console.log(`Research dashboard serving ${publicDir} at http://0.0.0.0:${port}`));
for (const signal of ['SIGTERM', 'SIGINT']) process.on(signal, () => server.close(() => process.exit(0)));
