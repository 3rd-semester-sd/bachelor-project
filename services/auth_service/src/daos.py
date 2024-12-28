from fastapi import Depends
from db.db_dependencies import GetDBSessionRO, GetDBSession

from typing import Annotated, Any
from uuid import UUID, uuid4

import sqlalchemy as sa


from dtos import BaseUserInputDTO
from models import BaseUser


class BaseUserReadDAO:
    """Class for accessing BaseUser table READ."""

    def __init__(self, session: GetDBSessionRO):
        self.session = session

    async def filter_one(
        self,
        **filter_params: Any,
    ) -> BaseUser | None:
        """Get a record by filters."""

        query = sa.select(BaseUser)

        for key, value in filter_params.items():
            if not hasattr(BaseUser, key):
                raise ValueError(
                    f"Model '{BaseUser.__name__}' does not have attr: '{key}'"
                )

            query = query.where(getattr(BaseUser, key) == value)

        query = query.limit(1)

        results = await self.session.execute(query)
        return results.scalar_one_or_none()


class BaseUserWriteDAO:
    """Class for accessing BaseUser table WRITE."""

    def __init__(self, session: GetDBSession):
        self.session = session

    async def create(
        self,
        input_dto: BaseUserInputDTO,
        id: UUID | None = None,
    ) -> UUID:
        """Create a record."""

        if id is None:
            id = uuid4()

        base = BaseUser(id=id, **input_dto.model_dump())
        self.session.add(base)
        await self.session.flush()
        return id


GetDAORO = Annotated[BaseUserReadDAO, Depends(BaseUserReadDAO)]
GetDAOWO = Annotated[BaseUserWriteDAO, Depends(BaseUserWriteDAO)]
