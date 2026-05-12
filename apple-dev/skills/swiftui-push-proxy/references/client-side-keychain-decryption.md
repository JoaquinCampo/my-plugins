# Client-side keychain and RFC 8291 decryption

The on-device half: generate keys, store in shared keychain, decrypt incoming Web Push payloads in the NotificationService extension.

## 1. Key generation (CryptoKit)

```swift
import CryptoKit
import Security

let privateKey = P256.KeyAgreement.PrivateKey()
let publicKey = privateKey.publicKey
let publicKeyX963 = publicKey.x963Representation
let privateKeyData = privateKey.rawRepresentation

var authBytes = [UInt8](repeating: 0, count: 16)
let status = SecRandomCopyBytes(kSecRandomDefault, 16, &authBytes)
precondition(status == errSecSuccess)
let authSecret = Data(authBytes)
```

The public key is x9.63 (uncompressed, 65 bytes, leading `0x04`); both the proxy and the upstream Web Push server expect that wire format, usually URL-safe base64 encoded.

## 2. Keychain storage with shared access group

Both the main app target and the NotificationService extension target need a `keychain-access-groups` entitlement with the same team-prefixed identifier, for example `ABCDE12345.com.example.myapp`. Then write items with `kSecAttrAccessGroup` set to that string.

```swift
func storeKey(_ data: Data, key: String, accessGroup: String) {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key,
        kSecAttrAccessGroup as String: accessGroup,
        kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlock,
        kSecValueData as String: data,
    ]
    SecItemDelete(query as CFDictionary)
    SecItemAdd(query as CFDictionary, nil)
}
```

Use `kSecAttrAccessibleAfterFirstUnlock`, not `WhenUnlocked`: the extension may run before the user has unlocked since boot. A third-party wrapper like `KeychainSwift` is fine for ergonomics; the access group is the only critical attribute.

## 3. NotificationService extension entry point

```swift
import UserNotifications

final class NotificationService: UNNotificationServiceExtension {
    var contentHandler: ((UNNotificationContent) -> Void)?
    var bestAttempt: UNMutableNotificationContent?

    override func didReceive(
        _ request: UNNotificationRequest,
        withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void
    ) {
        self.contentHandler = contentHandler
        self.bestAttempt = (request.content.mutableCopy() as? UNMutableNotificationContent)
        Task { await build(request: request) }
    }

    override func serviceExtensionTimeWillExpire() {
        if let bestAttempt { contentHandler?(bestAttempt) }
    }
}
```

Always call `contentHandler` exactly once, even on failure. The 30-second wall clock budget includes any network and crypto work.

## 4. RFC 8291 aesgcm decryption

The APNS payload arrives with three URL-safe base64 fields in `userInfo`: `m` (ciphertext), `k` (server P-256 public key, x9.63), `s` (16-byte salt).

```swift
import CryptoKit

func decrypt(
    payload: Data, salt: Data, auth: Data,
    privateKey: P256.KeyAgreement.PrivateKey,
    serverPublicKey: P256.KeyAgreement.PublicKey
) throws -> Data {
    let shared = try privateKey.sharedSecretFromKeyAgreement(with: serverPublicKey)

    let keyMaterial = shared.hkdfDerivedSymmetricKey(
        using: SHA256.self,
        salt: auth,
        sharedInfo: Data("Content-Encoding: auth\0".utf8),
        outputByteCount: 32
    )

    let clientPub = privateKey.publicKey.x963Representation
    let serverPub = serverPublicKey.x963Representation

    let contentKey = SymmetricKey(data: keyMaterial).hkdfDerivedSymmetricKey(
        using: SHA256.self,
        salt: salt,
        sharedInfo: info(type: "aesgcm", clientPub: clientPub, serverPub: serverPub),
        outputByteCount: 16
    )
    let nonce = SymmetricKey(data: keyMaterial).hkdfDerivedSymmetricKey(
        using: SHA256.self,
        salt: salt,
        sharedInfo: info(type: "nonce", clientPub: clientPub, serverPub: serverPub),
        outputByteCount: 12
    ).withUnsafeBytes { Data($0) }

    let box = try AES.GCM.SealedBox(combined: nonce + payload)
    let plain = try AES.GCM.open(box, using: contentKey)

    // Strip 2-byte big-endian padding length prefix
    let padLen = (Int(plain[0]) << 8) | Int(plain[1])
    return plain.dropFirst(2 + padLen)
}

func info(type: String, clientPub: Data, serverPub: Data) -> Data {
    var d = Data("Content-Encoding: \(type)\0P-256\0".utf8)
    d.append(0x00); d.append(0x41); d.append(clientPub)  // length 65
    d.append(0x00); d.append(0x41); d.append(serverPub)
    return d
}
```

## 5. Build the final content

```swift
struct PushBody: Decodable { let title: String; let body: String; let badge: Int? }
let json = try JSONDecoder().decode(PushBody.self, from: plaintext)
bestAttempt?.title = json.title
bestAttempt?.body = json.body
if let badge = json.badge { bestAttempt?.badge = NSNumber(value: badge) }
contentHandler?(bestAttempt!)
```

## 6. Optional INSendMessageIntent enrichment

For sender avatars, after decryption fetch the sender icon, build an `INPerson` with `INImage(imageData:)`, attach to an `INSendMessageIntent`, donate, then call `bestAttempt.updating(from: intent)`. Use `UNNotificationAttachment` only for media; the intent path is what iOS uses to render the round avatar tile.
