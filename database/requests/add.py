from sqlalchemy import select
from database.connect import async_session
from database.models import User, Channel, Proxy


async def add_user(tg_id: int, username: str | None = None):
    """Добавляет пользователя в БД, если его там еще нет."""
    async with async_session() as session:
        # Проверяем, существует ли пользователь с таким tg_id
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()

        if not user:
            new_user = User(
                tg_id=tg_id,
                username=username
            )
            session.add(new_user)
            await session.commit()
        else:
            # Если юзернейм поменялся, можно его обновить
            if user.username != username:
                user.username = username
                await session.commit()


async def add_channel(channel_id: int, title: str, url: str):
    async with async_session() as session:
        session.add(Channel(channel_id=channel_id, title=title, url=url))
        await session.commit()

async def add_proxy(url: str):
    async with async_session() as session:
        session.add(Proxy(url=url))
        await session.commit()