(async () => {
  const {toBlob} = await import('__CAPTURE_MODULE__');
  await document.fonts.ready;
  await new Promise(r => setTimeout(r, 2500));
  for (;;) {
    try {
      const png = await toBlob(document.body, {width:320,height:240,canvasWidth:320,canvasHeight:240,pixelRatio:1,includeQueryParams:true,cacheBust:false});
      if (!png) throw new Error('Empty frame');
      const r = await fetch('/_bridge/frame', {method:'POST',body:png});
      if (!r.ok) throw new Error('USB frame rejected');
    } catch(e) { console.warn('Ryujin bridge:',e.message); }
    await new Promise(r => setTimeout(r,1000));
  }
})();
