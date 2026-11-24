// Deterministic local Three.js vendor bundle, consumed by the historical HTML.
// Only the build pipeline accesses npm. Browsers always use local assets.
import {build} from 'esbuild';
import {mkdir,copyFile,stat,readFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
const root=resolve(import.meta.dirname,'..');
const dir=join(root,'runtime_dist','vendor');
await mkdir(dir,{recursive:true});
const output=join(dir,'three-runtime.iife.js');
await build({entryPoints:[join(root,'tools','three_bridge.mjs')],bundle:true,
  outfile:output,format:'iife',platform:'browser',target:['es2020'],
  minify:true,legalComments:'eof',sourcemap:false,logLevel:'warning'});
const info=await stat(output);
if(info.size<200_000)throw Error('Bundled Three.js unexpectedly small: '+info.size);
const pkg=JSON.parse(await readFile(join(root,'node_modules','three','package.json'),'utf8'));
if(pkg.version!=='0.161.0')throw Error('Three.js mismatch: '+pkg.version);
await copyFile(join(root,'node_modules','three','LICENSE'),join(dir,'THREE-LICENSE.txt'));
console.log('LOCAL_THREE_BUNDLE',pkg.version,info.size,output);
