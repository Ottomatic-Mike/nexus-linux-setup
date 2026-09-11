const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const vm=require('node:vm');
const script=fs.readFileSync(__dirname+'/../nexus_adapter.js','utf8').replace('__PANEL_ID__','fixture');
function setup(path='/system/devices/available') {
 const data={devices:[{id:'fixture',layout:{keep:true}},{id:'y70',layout:{keep:true}}]};
 const window={fetch:async()=>new Response(JSON.stringify(data),{headers:{'content-type':'application/json','content-length':'12'}})};
 vm.runInNewContext(script,{window,location:{pathname:path,origin:'http://localhost:9400',href:'http://localhost:9400'+path},URL,Request,Response,Headers});return window;
}
test('exposes only configured record without changing either layout',async()=>{
 const r=await setup().fetch('/panel/devices');const d=await r.json();assert.equal(d.devices[0].streamed,true);assert.equal(d.devices[1].streamed,undefined);assert.deepEqual(d.devices.map(x=>x.layout),[{keep:true},{keep:true}]);assert.equal(r.headers.get('content-length'),null);
});
test('does not alter mutations, other origins or endpoints',async()=>{
 for(const [url,options] of [['/panel/devices',{method:'POST'}],['https://example.invalid/panel/devices'],['/preferences']]){const d=await (await setup().fetch(url,options)).json();assert.equal(d.devices[0].streamed,undefined);}
});
test('does not wrap physical panel or simulator fetches',async()=>{
 for(const path of ['/panel/fixture','/panel']) {const d=await (await setup(path).fetch('/panel/devices')).json();assert.equal(d.devices[0].streamed,undefined);}
});
