import re
from aiogram import Router, F, types
from sqlalchemy import select, func
from database.connect import async_session
from database.models import User, ReferralLink

router = Router()


# Ловим сообщения, содержащие ссылки вида t.me/bot?start=xxx
@router.message(F.text.regexp(r'(?:https?://)?t\.me/\w+\?start=([\w-]+)'))
async def process_advertiser_link(message: types.Message):
    # Извлекаем само "название" (код) из ссылки
    match = re.search(r'start=([\w-]+)', message.text)
    if not match:
        return

    code = match.group(1)
    owner_id = message.from_user.id

    async with async_session() as session:
        # Ищем, существует ли уже такая ссылка в базе
        ref_link = await session.scalar(select(ReferralLink).where(ReferralLink.code == code))

        if not ref_link:
            # Ссылки нет - создаем её
            new_link = ReferralLink(code=code, owner_id=owner_id)
            session.add(new_link)
            await session.commit()

            await message.answer(
                f"✅ <b>Реферальная ссылка успешно создана!</b>\n\n"
                f"🔗 <code>{message.text}</code>\n\n"
                f"<i>Вы можете начать рекламу. Чтобы посмотреть статистику, просто отправьте эту ссылку мне снова.</i>"
            )
        else:
            # Ссылка существует. Проверяем, принадлежит ли она отправителю
            if ref_link.owner_id != owner_id:
                await message.answer("⚠️ Эта ссылка уже занята другим рекламодателем. Придумайте другое название.")
                return

            # Вытаскиваем статистику по этому коду
            total = await session.scalar(select(func.count(User.id)).where(User.ref_code == code))
            active = await session.scalar(
                select(func.count(User.id)).where(User.ref_code == code, User.is_active == True))

            total_count = total or 0
            active_count = active or 0

            await message.answer(
                f"📊 <b>Статистика по ссылке:</b> <code>{code}</code>\n\n"
                f"👥 Всего переходов: <b>{total_count}</b>\n"
                f"🟢 Из них активных: <b>{active_count}</b>\n"
                f"🔴 Отписалось/Удалило: <b>{total_count - active_count}</b>\n\n"
                f"<i>(Статистика обновляется в реальном времени)</i>",
                disable_web_page_preview=True
            )