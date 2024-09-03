---
hide: footer
---
# `rg.User`

A user in Argilla is a profile that uses the SDK or UI. Their profile can be used to track their feedback activity and to manage their access to the Argilla server.

## Usage Examples

To create a new user, instantiate the `User` object with the client and the username:

```python
user = rg.User(username="my_username", password="my_password")
user.create()
```

Existing users can be retrieved by their username:

```python
user = client.users("my_username")
```

The current user of the `rg.Argilla` client can be accessed using the `me` attribute:

```python
client.me
```

---

::: src.argilla.users._resource.User