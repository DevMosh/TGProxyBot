from datetime import datetime, timedelta

from sqlalchemy import select, func
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

        result = await session.scalars(query)
        all_proxies = list(result.all())

        if not all_proxies:
            return None

        # 1. Закреплённый прокси — только если это НЕ ротация
        if exclude_id is None:
            for p in all_proxies:
                if p.is_pinned:
                    return p

        # 2. Фильтр по стабильности
        stable_proxies = [
            p for p in all_proxies
            if (p.success_checks / p.total_checks * 100 if p.total_checks > 0 else 100) >= 80
            or p.total_checks < 5
        ]
        if not stable_proxies:
            stable_proxies = all_proxies

        # 3. Сортируем стабильно (по score, затем по id для детерминизма)
        stable_proxies.sort(key=lambda x: (x.score, x.id))

        # 4. Ротация по кругу: берём следующий после exclude_id
        if exclude_id is None:
            return stable_proxies[0]

        ids = [p.id for p in stable_proxies]
        if exclude_id in ids:
            idx = ids.index(exclude_id)
            return stable_proxies[(idx + 1) % len(stable_proxies)]
        else:
            # Текущий прокси выпал из стабильных — начинаем сначала
            return stable_proxies[0]


async def get_users_stats() -> tuple[int, int]:
    """Возвращает (всего_пользователей, активных_пользователей)"""
    async with async_session() as session:
        # Используем func.count для быстрого подсчета на стороне СУБД
        total_users = await session.scalar(select(func.count(User.id)))
        active_users = await session.scalar(
            select(func.count(User.id)).where(User.is_active == True)
        )
        return total_users or 0, active_users or 0


async def get_detailed_stats():
    """Возвращает словарь с развернутой статистикой пользователей"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)

    async with async_session() as session:
        # Общее кол-во и активные
        total = await session.scalar(select(func.count(User.id)))
        active = await session.scalar(select(func.count(User.id)).where(User.is_active == True))

        # Новые пользователи за периоды
        new_today = await session.scalar(
            select(func.count(User.id)).where(User.created_at >= today_start)
        )
        new_yesterday = await session.scalar(
            select(func.count(User.id)).where(
                User.created_at >= yesterday_start,
                User.created_at < today_start
            )
        )
        new_week = await session.scalar(
            select(func.count(User.id)).where(User.created_at >= week_start)
        )
        new_month = await session.scalar(
            select(func.count(User.id)).where(User.created_at >= month_start)
        )

        return {
            "total": total or 0,
            "active": active or 0,
            "today": new_today or 0,
            "yesterday": new_yesterday or 0,
            "week": new_week or 0,
            "month": new_month or 0
        }