# import asyncio
# from typing import Optional

# from sqlalchemy.ext.asyncio import create_async_engine
# from sqlmodel import Field, SQLModel, select
# from sqlmodel.ext.asyncio.session import AsyncSession


# class Hero(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str
#     secret_name: str
#     age: Optional[int] = None




# async def main() -> None:
#     engine = create_async_engine("sqlite+aiosqlite:///database.db")

#     async with engine.begin() as conn:
#         await conn.run_sync(SQLModel.metadata.create_all)

#     async with AsyncSession(engine) as session:
#         session.add(Hero(name="Spider-Boy", secret_name="Pedro Parqueador"))
#         await session.commit()

#     async with AsyncSession(engine) as session:
#         statement = select(Hero).where(Hero.name == "Spider-Boy")
#         reveal_type(session)
#         result = await session.exec(statement)
#         reveal_type(result)
#         reveal_type(result.first())


# asyncio.run(main())

a = {
    
}
