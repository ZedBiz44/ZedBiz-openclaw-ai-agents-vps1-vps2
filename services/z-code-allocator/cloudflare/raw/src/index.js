export default {
  async fetch(request, env) {
    const incoming = new URL(request.url);
    const target = new URL(env.ORIGIN_BASE);
    target.pathname = target.pathname + incoming.pathname.replace(/^\//, "");
    target.search = incoming.search;
    const response = await fetch(new Request(target, request));
    const headers = new Headers(response.headers);
    headers.set("X-Content-Type-Options", "nosniff");
    headers.set("Referrer-Policy", "no-referrer");
    headers.set("Cache-Control", "no-store");
    return new Response(response.body, {status: response.status, statusText: response.statusText, headers});
  }
};
