import asyncio
from aiogram import Bot
from sqlalchemy import select

from database.connect import async_session
from database.models import Proxy
from utils.ping import ping_proxy
from data.config import ADMIN_IDS


async def notify_admins(bot: Bot, text: str):
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(chat_id=admin_id, text=text, disable_web_page_preview=True)
        except Exception:
            pass


async def background_proxy_checker(bot: Bot):
    """Фоновый чекер с защитой от ложных срабатываний (троекратная проверка)"""
    failed_strikes = {}  # Хранит количество неудачных пингов подряд {proxy_id: count}

    while True:
        async with async_session() as session:
            result = await session.scalars(select(Proxy))
            proxies = result.all()

            for proxy in proxies:
                was_active = proxy.is_active

                # Теперь ping_proxy возвращает одно число (чистый пинг)
                ping_ms = await ping_proxy(proxy.url)
                proxy.total_checks += 1

                if ping_ms is not None:
                    # ✅ Прокси работает! Сбрасываем страйки.
                    failed_strikes[proxy.id] = 0

                    proxy.success_checks += 1
                    proxy.is_active = True
                    proxy.score = ping_ms  # Просто сохраняем пинг как есть

                    # Оставляем алерт только на РЕАЛЬНЫЕ тормоза (например, пинг больше 1000мс)
                    # Но шлем его только если прокси был быстрым.
                    # Закомментируй этот блок, если тебе вообще не нужны алерты о скорости
                    if proxy.score >= 1000 and ping_ms < 1000:  # Логика инвертирована, чтобы не спамить
                        pass  # Можно убрать деградацию совсем, чтобы спать спокойно
                else:
                    # ❌ Прокси не ответил
                    strikes = failed_strikes.get(proxy.id, 0) + 1
                    failed_strikes[proxy.id] = strikes

                    # Если прокси упал 3 раза подряд (~9-10 минут)
                    if strikes >= 3:
                        proxy.is_active = False
                        proxy.score = 9999.0

                        if was_active:
                            short_url = proxy.url.split('@')[-1] if '@' in proxy.url else proxy.url
                            await notify_admins(
                                bot,
                                f"🚨 <b>ПРОКСИ УПАЛ</b>\n\n"
                                f"💀 Не отвечает уже 3 проверки подряд:\n"
                                f"🌐 <code>{short_url}</code>\n\n"
                                f"🔧 <i>Исключен из выдачи.</i>"
                            )

                await session.commit()
                await asyncio.sleep(0.5)

        # Ждем 3 минуты до следующего круга
        await asyncio.sleep(180)