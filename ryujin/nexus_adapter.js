// Expose only the bridge's existing panel record to Nexus's built-in panel editor.
// Does not replace layouts, alter other devices, or suppress native warnings.
(() => {
  if (location.pathname.startsWith('/panel')) return;
  const panelId = '__PANEL_ID__';
  const originalFetch = window.fetch.bind(window);
  window.fetch = async function(input, options) {
    const response = await originalFetch(input, options);
    const url = new URL(typeof input === 'string' ? input : input.url, location.href);
    const method = options?.method || (input instanceof Request ? input.method : 'GET');
    if (url.origin !== location.origin || url.pathname !== '/panel/devices' || method.toUpperCase() !== 'GET' || !response.ok) return response;
    try {
      const data = await response.clone().json();
      const record = data.devices?.find(d => d.id === panelId);
      if (!record) return response;
      record.streamed = true;
      const headers = new Headers(response.headers);
      headers.delete('Content-Length'); headers.delete('Content-Encoding'); headers.delete('ETag');
      return new Response(JSON.stringify(data), {status:response.status,statusText:response.statusText,headers});
    } catch { return response; }
  };
})();
