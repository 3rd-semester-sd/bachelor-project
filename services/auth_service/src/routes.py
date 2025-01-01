from fastapi import APIRouter
import dtos
import daos
import exceptions
import auth_utils

base_router = APIRouter(prefix="/api")
base_router_v1 = APIRouter(prefix="/v1")
auth_router = APIRouter(prefix="/auth")


@base_router.get("/health")
async def health_check() -> bool:
    """Return True if the service is healthy."""

    return True


@auth_router.post("/login-email", status_code=201)
async def login(
    input_dto: dtos.UserLoginDTO,
    r_daos: daos.GetDAORO,
) -> dtos.DataResponse[dtos.LoginResponse]:
    """Login by email and password."""

    user = await r_daos.filter_one(email=input_dto.email)

    if user is None:
        raise exceptions.Http401("Wrong email or password")

    is_valid_password = auth_utils.verify_password(
        input_dto.password.get_secret_value(), user.password
    )

    if not is_valid_password:
        raise exceptions.Http401("Wrong email or password")

    token = auth_utils.create_access_token(
        data=dtos.TokenData(
            user_id=user.id,
        )
    )

    return dtos.DataResponse(data=dtos.LoginResponse(access_token=token))


@auth_router.post("/register", status_code=201)
async def register(
    input_dto: dtos.UserCreateDTO,
    r_daos: daos.GetDAORO,
    w_daos: daos.GetDAOWO,
) -> dtos.DefaultCreatedResponse:
    """Register by email and password."""

    user = await r_daos.filter_one(email=input_dto.email)

    if user:
        raise exceptions.Http401("User already exists")

    user_id = await w_daos.create(
        dtos.BaseUserInputDTO(
            email=input_dto.email,
            password=auth_utils.hash_password(
                input_dto.password.get_secret_value(),
            ),
        )
    )

    return dtos.DefaultCreatedResponse(
        data=dtos.CreatedResponse(
            id=user_id,
        )
    )


@auth_router.get("/users/me", status_code=200)
async def get_current_user(
    current_user: auth_utils.GetCurrentUser,
) -> dtos.DataResponse[dtos.BaseUserDTO]:
    """Get current user."""

    return dtos.DataResponse(data=current_user)


base_router_v1.include_router(auth_router)
base_router.include_router(base_router_v1)
