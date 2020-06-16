# Identity

Identity contains information that identify the user to other threebot machines.
Multiple identities can be configured. By default if only one is configured it will be used as default `me`.

## configuring identity

To configure your identity:

```python
me = j.core.identity.new("name", "threebot_name", "threebot_mail", "words")
```

To access his threebot id:

```python
me.tid
# or
j.core.identity.me.tid
```

To change the default `me`
```python
j.core.identity.set_default("othername")
```

The tool gets the id as follows:

- If user already registered on the same machine will get directly from config
- If is a new registration will contact the explorer to gets the user information and verifies it against local config and set the id
- If a new user will create the user and register it on the explorer and continue like the preceding point

## Encryption

`nacl` property wrapes some signing/encrypting functionalities using the user private key which is generated from his seed words.

The user private key can be accessed from the identity:

```python
j.core.identity.me.nacl.private_key
<nacl.public.PrivateKey at 0x7f2749f4e510>
```

Same with the signing key:

```python
j.core.identity.me.nacl.signing_key
<nacl.signing.SigningKey at 0x7f2760aecf10>
```
