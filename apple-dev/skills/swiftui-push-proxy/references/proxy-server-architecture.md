# Relay proxy server architecture

The server half. You build and deploy this once; it is not part of the iOS app. The proxy is a stateless forwarder: Web Push in, APNS out, ciphertext never decoded.

## What the proxy does

1. Accepts Web Push HTTPS POSTs from upstream services on a per-device URL.
2. Looks up the device's APNS token (encoded into the URL path at registration time).
3. Repackages the encrypted Web Push payload into an APNS alert with `mutable-content: 1` so the device's NotificationService extension wakes.
4. Forwards to APNS via HTTP/2 with the right team auth key.

The proxy never holds the device's private key or auth secret, only the APNS token and the ciphertext in transit.

## Endpoint shape

A typical relay accepts URLs like:

```
POST https://push-relay.example.com/push/<apns-token-hex>/<account-id>?sandbox=true
Content-Encoding: aesgcm
Encryption: salt=<base64url>
Crypto-Key: dh=<base64url>; p256ecdsa=<base64url>
Body: <ciphertext bytes>
```

Headers come from the Web Push standard. The proxy parses `salt` and `dh` (server public key), base64url-encodes both, and stuffs them into the APNS payload alongside the ciphertext:

```json
{
  "aps": { "alert": { "title": " " }, "mutable-content": 1, "sound": "default" },
  "m": "<urlsafe-base64 ciphertext>",
  "s": "<urlsafe-base64 16-byte salt>",
  "k": "<urlsafe-base64 65-byte server pubkey>",
  "a": "<account-id>"
}
```

The `title` is a placeholder; the device overwrites it after decryption. APNS will not deliver an alert with empty content, so set a space.

## Device registration

When the device first calls the proxy to register, it sends its current APNS push token plus a per-account identifier. The proxy returns the per-device URL the upstream service should POST Web Push to. The device then calls the upstream's `POST /api/v1/push/subscription` with that URL as `endpoint`, plus its `p256dh` public key (URL-safe base64 x9.63) and `auth` secret.

The proxy stores essentially: `(deviceID, apnsToken, sandboxFlag, optionalPriorities)`. Nothing about messages, no decryption keys, no message bodies.

## Statelessness

The proxy must not log payload bodies, must not retain payloads past forwarding, and ideally pipes the request body straight from the inbound HTTPS stream into the outbound APNS frame. Treat the ciphertext as opaque bytes; if your language pulls it into memory as a string, you have a bug (UTF-8 will corrupt it).

## APNS specifics

- Use the HTTP/2 APNS Provider API with a token-based auth (`.p8` key from Apple Developer).
- The `apns-topic` header must be the bundle ID of the NotificationService extension's host app.
- The `apns-push-type: alert` and `apns-priority: 10` headers are typical.
- Sandbox environment for DEBUG builds (`api.sandbox.push.apple.com`), production for TestFlight and App Store (`api.push.apple.com`). The `?sandbox=true` query param at registration tells the proxy which.

## Considerations

- Rate limiting: APNS will start rejecting if you spam invalid tokens. Cache `BadDeviceToken` responses and drop the device record so the upstream stops getting subscribed.
- Retry policy: APNS returns `429` or `503`, retry with exponential backoff, but only briefly; Web Push has its own TTL semantics.
- Monitoring: alert on APNS error rate, on 5xx upstream, and on subscription deletes; users notice missing pushes fast.
- Single-region hosting risk: if the proxy is down, push stops for every user. A short outage is usually fine because Web Push servers retry, but plan for failover or graceful degradation. Co-locating other proxied features (image alt text, translation) on the same host means a single failure takes them all down; consider splitting if uptime matters.
- TLS: terminate TLS at the proxy or a CDN in front; HTTP/2 is required by APNS.
- Authentication: optional. If you trust any upstream that knows the per-device URL, you do not need a shared secret. If you want to lock down, add a HMAC over the URL signed by a key returned at registration.

## Hosting alternatives

You can run the relay anywhere that supports long-lived HTTP/2 connections to Apple:

- A small VPS or container service (e.g., a single-region VM, Fly, Render).
- Cloudflare Workers for the inbound side, with a separate APNS sender (Workers limit on outbound HTTP/2 vary).
- AWS Lambda with API Gateway, paired with an APNS client SDK; cold starts can add latency.
- A traditional queue setup (NSQ, Redis Streams, SQS) decouples ingest from APNS send and helps with retries.

Pick the cheapest setup that meets your latency target. For most apps, a single small instance handles thousands of pushes per minute comfortably.
