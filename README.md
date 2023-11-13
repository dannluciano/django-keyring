# Django Keyring

Django Integration with Keyring: A simple encryption-at-rest with key rotation support for Python.

![keyring: Simple encryption-at-rest with key rotation support for Python.](https://raw.githubusercontent.com/dannluciano/keyring-python/main/keyring.png)

N.B.: **keyring** is _not_ for encrypting passwords--for that, you should use
something like [bcrypt](https://pypi.org/project/bcrypt/). It's meant for
encrypting sensitive data you will need to access in plain text (e.g. storing
OAuth token from users). Passwords do not fall in that category.

The goal of this project is providing a easily integration with Django ORM.

## Installation

Add package `django-keyring` to your `requirements.txt` or:

```console
pip install django-keyring
```

## Usage

### Encryption

By default, AES-128-CBC is the algorithm used for encryption. This algorithm
uses 16 bytes keys, but you're required to use a key that's double the size
because half of that keys will be used to generate the HMAC. The first 16 bytes
will be used as the encryption key, and the last 16 bytes will be used to
generate the HMAC.

Using random data base64-encoded is the recommended way. You can easily generate
keys by using the following command:

```console
$ dd if=/dev/urandom bs=32 count=1 2>/dev/null | openssl base64 -A
qUjOJFgZsZbTICsN0TMkKqUvSgObYxnkHDsazTqE5tM=
```

Include the result of this command in the `value` section of the key description
in the keyring. Half this key is used for encryption, and half for the HMAC.

#### Key size

The key size depends on the algorithm being used. The key size should be double
the size as half of it is used for HMAC computation.

- `aes-128-cbc`: 16 bytes (encryption) + 16 bytes (HMAC).
<!-- - `aes-192-cbc`: 24 bytes (encryption) + 24 bytes (HMAC).
- `aes-256-cbc`: 32 bytes (encryption) + 32 bytes (HMAC). -->

#### About the encrypted message

Initialization vectors (IV) should be unpredictable and unique; ideally, they
will be cryptographically random. They do not have to be secret: IVs are
typically just added to ciphertext messages unencrypted. It may sound
contradictory that something has to be unpredictable and unique, but does not
have to be secret; it is important to remember that an attacker must not be able
to predict ahead of time what a given IV will be.

With that in mind, _keyring_ uses
`base64(hmac(unencrypted iv + encrypted message) + unencrypted iv + encrypted message)`
as the final message. If you're planning to migrate from other encryption
mechanisms or read encrypted values from the database without using _keyring_,
make sure you account for this. The HMAC is 32-bytes long and the IV is 16-bytes
long.

### Keyring

Keys are managed through a keyring--a short python Dictionary describing your
encryption keys. The keyring must be a Dictionary object mapping numeric ids of the
keys to the key values. A keyring must have at least one key. For example:

```python settings.py
...
KEYRINGPY_KEYS = {
    "1": "uDiMcWVNTuz//naQ88sOcN+E40CyBRGzGTT7OkoBS6M=",
    "2": "VN8UXRVMNbIh9FWEFVde0q7GUA1SGOie1+FgAKlNYHc="
}


KEYRINGPY_SALT = "salt_and_peepers"
...
```

The `id` is used to track which key encrypted which piece of data; a key with a
larger id is assumed to be newer. The value is the actual bytes of the
encryption key.

### Key Rotation

With **keyring** you can have multiple encryption keys at once and key rotation
is fairly straightforward: if you add a key to the _keyring_ with a higher id
than any other key, that key will automatically be used for encryption when
objects are either created or updated. Any keys that are no longer in use can be
safely removed from the _keyring_.

It's extremely important that you save the keyring id returned by `encrypt()`;
otherwise, you may not be able to decrypt values (you can always decrypt values
if you still possess _all_ encryption keys).

If you're using **keyring** to encrypt database columns, it's recommended to use
a separated _keyring_ for each table you're planning to encrypt: this allows an
easier key rotation in case you need (e.g. key leaking).

N.B.: Keys are hardcoded on these examples, but you shouldn't do it on your code
base. You can retrieve _keyring_ from environment variables if you're deploying
to [Heroku](https://heroku.com) and alike, or deploy a JSON file with your
configuration management software (e.g. Ansible, Puppet, Chef, etc).

### Basic usage of django-keyring

```python models.py
from django.db import models
from keyring.fields import KeyringField


class Message(models.Model):
    user = KeyringField(
        disgest_field=True
    )
    
    text = KeyringField()

    room = KeyringField(
        disgest_field='room_sha_digest'
    )

```

<!-- #### Change encryption algorithm

You can choose between `AES-128-CBC`, `AES-192-CBC` and `AES-256-CBC`. By
default, `AES-128-CBC` will be used.

To specify the encryption algorithm, set the `encryption` option. The following
example uses `AES-256-CBC`.

```python
from keyring import Keyring

keys = { "1": "uDiMcWVNTuz//naQ88sOcN+E40CyBRGzGTT7OkoBS6M=" }
encryptor = Keyring(keys, {
  "encryption": "aes-256-cbc",
  "digest_salt": "<custom salt>",
})
``` -->

### Exchange data with Ruby

If you use Ruby, you may be interested in
<https://github.com/fnando/attr_keyring>, which is able to read and write
messages using the same format.

### Exchange data with Node.js

If you use Node.js, you may be interested in
<https://github.com/fnando/keyring-node>, which is able to read and write
messages using the same format.


## Development

After checking out the repo, run `pip install -r requirements.dev.txt` to install dependencies. Then,
run `pytest` to run the tests.

## Contributing

Bug reports and pull requests are welcome on GitHub at
<https://github.com/dannluciano/django-keyring>. This project is intended to be a safe,
welcoming space for collaboration, and contributors are expected to adhere to
the [Contributor Covenant](http://contributor-covenant.org) code of conduct.

## License

The gem is available as open source under the terms of the
[MIT License](https://opensource.org/licenses/MIT).

## Icon

Icon made by [Icongeek26](https://www.flaticon.com/authors/icongeek26) from
[Flaticon](https://www.flaticon.com/) is licensed by Creative Commons BY 3.0.

<!-- ## Code of Conduct

Everyone interacting in the **keyring** project’s codebases, issue trackers,
chat rooms and mailing lists is expected to follow the
[code of conduct](https://github.com/dannluciano/keyring-python/blob/main/CODE_OF_CONDUCT.md). -->

## Acknowledgments

Inspired:

* by [@fnando](https://github.com/fnando) on [keyring-node](https://github.com/fnando/keyring-node) and [attr_keyring](https://github.com/fnando/attr_keyring)

Thanks to [IFPI](https://www.ifpi.edu.br/) for pay my salary!

![IFPI](https://github.com/dannluciano/liveboards/raw/master/doc/ifpi.png)