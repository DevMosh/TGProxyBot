from urllib.parse import quote

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.ping import parse_proxy_url


def get_subscription_keyboard(channels: list):
    builder = InlineKeyboardBuilder()

    # Динамически добавляем кнопки каналов
    for channel in channels:
        builder.row(
            types.InlineKeyboardButton(
                text=channel.title,
                url=channel.url
            )
        )

    # Кнопка проверки подписки
    builder.row(
        types.InlineKeyboardButton(
            text="✅ Проверить подписку",
            callback_data="check_subscription"
        )
    )

    return builder.as_markup()


def admin_main_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📣 Рассылка", callback_data="admin_broadcast"))
    builder.row(types.InlineKeyboardButton(text="📢 Управление каналами", callback_data="admin_channels"))
    builder.row(types.InlineKeyboardButton(text="🌐 Управление прокси", callback_data="admin_proxies"))
    return builder.as_markup()


def admin_back_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔙 Назад в меню", callback_data="admin_main"))
    return builder.as_markup()


def admin_channels_kb(channels):
    builder = InlineKeyboardBuilder()
    for ch in channels:
        # Кнопка с названием канала и крестиком для удаления
        builder.row(types.InlineKeyboardButton(text=f"❌ Удал: {ch.title}", callback_data=f"del_ch_{ch.id}"))

    builder.row(types.InlineKeyboardButton(text="➕ Добавить канал", callback_data="add_channel"))
    builder.row(types.InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main"))
    return builder.as_markup()


def admin_proxies_kb(proxies_with_ping):
    builder = InlineKeyboardBuilder()
    # Теперь мы принимаем 4 параметра (добавился is_pinned)
    for proxy_id, url, ping, is_pinned in proxies_with_ping:
        status = f"{ping} мс 🟢" if ping else "Мертв 🔴"

        host, port = parse_proxy_url(url)
        display_name = f"{host}:{port}" if host and port else url[:20] + "..."

        pin_btn_text = "📍 Открепить" if is_pinned else "📌 Закрепить"

        # Делаем 2 кнопки в ряд: [Закреп] и [Удалить]
        builder.row(
            types.InlineKeyboardButton(text=pin_btn_text, callback_data=f"pin_prx_{proxy_id}"),
            types.InlineKeyboardButton(text=f"❌ {display_name} | {status}", callback_data=f"del_prx_{proxy_id}")
        )

    builder.row(types.InlineKeyboardButton(text="➕ Добавить прокси", callback_data="add_proxy"))
    builder.row(types.InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main"))
    return builder.as_markup()


def get_proxy_control_keyboard(current_proxy_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="🔄 Выдать другой прокси",
            callback_data=f"replace_proxy_{current_proxy_id}"
        )
    )

    share_text = (
        "🔥 Смотри, какой быстрый и бесплатный прокси я нашел! "
        "Подключайся в один клик 👇\n"
    )
    share_url = "https://t.me/Proxytochka_bot?start=share"
    share_link = (
        f"https://t.me/share/url?url={quote(share_text)}&text={quote(share_url)}"
    )

    builder.row(
        types.InlineKeyboardButton(
            text="📤 Поделиться прокси",
            url=share_link
        )
    )
    return builder.as_markup()