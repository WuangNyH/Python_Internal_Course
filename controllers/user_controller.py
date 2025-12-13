from fastapi import APIRouter

from schemas.request.user_schema import UserCreate
from schemas.response.error_response import ErrorResponse
from schemas.response.user_out_schema import UserOut
from services import user_service

user_router = APIRouter()


@user_router.post(
    "",
    status_code=201,
    response_model=UserOut,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input on business logic"}
    },
)
def create_user(user: UserCreate) -> UserOut:
    return user_service.create_user(user)


# @user_router.post("/bookings")
# def create_booking(booking: BookingCreate):
#     return {
#         "message": "Booking created successfully",
#         "data": booking
#     }