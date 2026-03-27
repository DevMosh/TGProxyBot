from sqlalchemy import select
from database.connect import async_session
from database.models import User, Channel, Proxy

async def get_all_users():
    async with async_session() as session:
        result = await session.scalars(select(User))
        return result.all()

async def get_all_channels():
    async with async_session() as session:
        result = await session.scalars(select(Channel))
        return result.all()

async def get_all_proxies():
    async with async_session() as session:
        result = await session.scalars(select(Proxy))
        return result.all()


async def get_best_proxy(exclude_id: int = None):
    async with async_session() as session:
        query = select(Proxy).where(Proxy.is_active == True)

        # Если юзер просит замену, исключаем его текущий прокси из поиска
        if exclude_id is not None:
            query = query.where(Proxy.id != exclude_id)

        result = await session.scalars(query)
        proxies = list(result.all())

        if not proxies:
            return None

        stable_proxies = []
        for p in proxies:
            uptime = (p.success_checks / p.total_checks * 100) if p.total_checks > 0 else 100
            if uptime >= 80 or p.total_checks < 5:
                stable_proxies.append(p)

        if not stable_proxies:
            stable_proxies = proxies

        stable_proxies.sort(key=lambda x: x.score)

        return stable_proxies[0]