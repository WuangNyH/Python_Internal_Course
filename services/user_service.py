from fastapi import HTTPException
from schemas.request.user_schema import UserCreate
from schemas.response.user_out_schema import UserOut

_users: list[dict] = []
_id_counter = 1


def create_user(user: UserCreate) -> UserOut:
    global _id_counter

    # Validation nghiệp vụ (khác với validation kiểu dữ liệu của Pydantic)
    if user.age < 18:
        # Tạm sử dụng HTTPException của FastAPI, buổi sau tự tạo Custom Exception
        raise HTTPException(status_code=400, detail="Age must be >= 18")

    stored_user = {
        "id": _id_counter,
        "name": user.name,
        "age": user.age,
        "address": user.address,  # lưu nội bộ, nhưng không trả ra UserOut
    }

    _users.append(stored_user)
    _id_counter += 1

    return UserOut(
        id=stored_user["id"],
        name=stored_user["name"],
        age=stored_user["age"],
    )
