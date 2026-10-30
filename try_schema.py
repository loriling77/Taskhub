from pydantic import ValidationError
from app.schemas import RegisterRequest

try:
    user = RegisterRequest(
        username="abc",
        email="alice@example.com",
        password="MyPassword123!"
    )

    print("验证成功！")
    print(user.username)
    print(user.email)

except ValidationError as error:
    print(error)