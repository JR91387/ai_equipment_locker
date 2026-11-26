# View from another machine

The page is served only to `127.0.0.1`, and it answers only requests addressed to `127.0.0.1` or `localhost`.
That stops other machines and other websites from reading or changing your catalogue. A request addressed to
any other name gets `403` and a message naming the host it saw.

## SSH tunnel (no changes needed)
From the machine you want to look from:

```bash
ssh -L 8765:127.0.0.1:8765 alice@host-a
```

Then open `http://127.0.0.1:8765` there. The request still arrives as `127.0.0.1`, so nothing else is needed.

## A proxy or tunnel with its own name
Tools such as Tailscale Serve, Caddy or nginx forward requests under their own host name
(`host-a.example.ts.net`, say). Tell the server to accept that name:

```bash
equipment-locker serve --allow-host host-a.example.ts.net
```

`--allow-host` can be repeated. It adds the name to the accepted list for viewing and for the page's own
changes (notes, tags, pictures, Refresh). The server still listens only on `127.0.0.1`, so the proxy must run on
the same machine.

**Before you do this:** anyone who can reach the proxy can read your catalogue and change your notes and tags.
Put it only behind something that already limits who can connect (a private network or a login).
