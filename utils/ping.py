import time
import asyncio
from urllib.parse import urlparse, parse_qs


def parse_proxy_url(proxy_url: str):
    """Извлекает IP/домен и порт из любой ссылки на прокси"""
    host, port = None, None
    try:
        # Если это ссылка Telegram (proxy или socks)
        if "t.me/" in proxy_url or proxy_url.startswith("tg://"):
            parsed_url = urlparse(proxy_url)
            qs = parse_qs(parsed_url.query)
            if 'server' in qs and 'port' in qs:
                host = qs['server'][0]
                port = int(qs['port'][0])
        else:
            # Обычный http/socks прокси
            if "://" not in proxy_url:
                proxy_url = "http://" + proxy_url
            parsed_url = urlparse(proxy_url)
            host = parsed_url.hostname
            port = parsed_url.port
    except Exception:
        pass

    return host, port


async def ping_proxy(proxy_url: str, timeout_seconds: int = 4) -> float | None:
    """Возвращает только чистый TCP пинг в миллисекундах. Никакого мусора в сокет."""
    host, port = parse_proxy_url(proxy_url)
    if not host or not port:
        return None

    start_tcp = time.time()
    try:
        # Устанавливаем TCP-соединение
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout_seconds
        )
        tcp_ping_ms = round((time.time() - start_tcp) * 1000, 2)

        # Закрываем соединение чисто
        writer.close()
        await writer.wait_closed()

        return tcp_ping_ms
    except Exception:
        return None