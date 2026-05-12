---
name: swiftui-push-proxy
description: Build E2E-encrypted iOS push for services that speak Web Push (not APNS-native): relay proxy + RFC 8291 aesgcm decryption on device, keys in shared keychain. Triggers on Web Push, APNS, RFC 8291, `UNNotificationServiceExtension`, federated push.
---

# SwiftUI Push Proxy

## When this applies

Your upstream service speaks Web Push (RFC 8291), but iOS apps need APNS, and you do not want the upstream to ever see plaintext push contents. Common cases: federated social networks, self-hosted backends, third-party services where you cannot run a custom APNS client.

## Architecture

```
Upstream service (Web Push) --> Relay proxy --> APNS --> Device
                                    |                      |
                                    v                      v
                                forwards               decrypts via
                                opaque blob            keychain key
```

## Trust model

- Proxy sees ciphertext only, never plaintext.
- The P-256 keypair and 16-byte auth secret never leave the device.
- The proxy is a single point of failure for delivery, not for confidentiality. If the proxy goes down, pushes stop; if it is compromised, the attacker still cannot read messages.

## The 6-step setup

1. Generate a P-256 keypair and a 16-byte auth secret on device. Store both in the keychain. Use a shared access group so the NotificationService extension can read them.
2. Register the device with your relay proxy: POST the public key (x9.63 raw), the auth secret, and the APNS push token.
3. Subscribe to the upstream service's Web Push, pointing the `endpoint` parameter at your relay (with the APNS token embedded in the URL path).
4. Implement a `UNNotificationServiceExtension` to receive the APNS payload, read ciphertext, salt, and server public key from `userInfo`, and decrypt locally.
5. Decrypt via RFC 8291 aesgcm: ECDH shared secret + HKDF over the auth secret to derive the content encryption key (16 bytes) and nonce (12 bytes), then open the AES-GCM sealed box.
6. Build a `UNMutableNotificationContent` from the decrypted JSON payload and pass it to `contentHandler`. Optionally attach an `INSendMessageIntent` for sender avatars.

## What lives in the keychain (shared access group)

- Private key, base64 raw representation of `P256.KeyAgreement.PrivateKey`.
- Public key, derived from the private key on demand (or cached as x9.63).
- Auth secret, 16 random bytes from `SecRandomCopyBytes`.
- Proxy registration token or account identifier, for multi-account apps.

All entries use `kSecAttrAccessibleAfterFirstUnlock` so the extension can read them after a reboot before unlock has happened.

## Deep dives in references/

- `client-side-keychain-decryption.md` covers CryptoKit key generation, keychain storage with `kSecAttrAccessGroup`, the NotificationService extension entry point, the full RFC 8291 aesgcm decryption (HKDF info strings, salt, nonce, AES-GCM-128), and INSendMessageIntent enrichment.
- `proxy-server-architecture.md` covers the relay HTTPS endpoint, the device-to-APNS-token mapping, statelessness about message contents, rate limiting and retry, and hosting alternatives.

## Gotchas

- Do not store keys in `UserDefaults` or a plist; only the keychain with `kSecAttrAccessibleAfterFirstUnlock`.
- `UNNotificationServiceExtension` has a 30-second budget. Do crypto carefully and fast; avoid synchronous network calls before `contentHandler` is invoked at least once.
- The shared keychain access group requires `keychain-access-groups` entitlements in BOTH the app target and the extension target, with the same team-prefixed identifier.
- Some Web Push servers send raw padding bytes prefixed to plaintext (2-byte big-endian length). Strip the padding before JSON decoding.
- URL-safe base64 is not the same as standard base64. Decode `m`, `k`, and `s` fields with URL-safe alphabet.
- In DEBUG builds APNS uses the sandbox environment; the relay must know which environment to target (a `?sandbox=true` query flag works).
