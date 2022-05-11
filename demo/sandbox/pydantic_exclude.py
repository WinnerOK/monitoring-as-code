from pydantic import BaseModel, SecretStr


class User(BaseModel):
    id: int
    username: str
    password: SecretStr


class Transaction(BaseModel):
    id: str
    user: User
    value: int


t = Transaction(
    id="1234567890",
    user=User(id=42, username="JohnDoe", password="hashedpassword"),
    value=9876543210,
)

# using a set:
print(t.json(exclude={"user", "value"}))
# > {'id': '1234567890'}

# using a dict:
print(t.json(exclude={"user": {"username", "password"}, "value": True}))
# > {'id': '1234567890', 'user': {'id': 42}}

print(t.json(include={"id": True, "user": {"id"}}))
# > {'id': '1234567890', 'user': {'id': 42}}
