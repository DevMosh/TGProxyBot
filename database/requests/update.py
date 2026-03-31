from sqlalchemy import select, update
from database.connect import async_session
from database.models import User, Proxy


async def update_user_status(tg_id: int, is_active: bool):
    """Обновляет статус активности пользователя"""
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user and user.is_active != is_active:
            user.is_active = is_active
            await session.commit()


async def toggle_pin_proxy(proxy_id: int):
    """Закрепляет прокси (и открепляет остальные) или снимает закрепление"""
    async with async_session() as session:
        proxy = await session.get(Proxy, proxy_id)
        if not proxy:
            return

        new_status = not proxy.is_pinned

        if new_status:
            # Если мы хотим закрепить этот, сначала открепляем ВСЕ остальные
            await session.execute(update(Proxy).values(is_pinned=False))

        # Меняем статус текущему
        proxy.is_pinned = new_status
        await session.commit()