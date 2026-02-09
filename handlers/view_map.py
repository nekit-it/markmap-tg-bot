from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from services.storage import get_user_maps  

router = Router()


def _flatten_nodes(nodes: list) -> list[str]:
    """Преобразуем иерархию узлов из storage в плоский список строк."""
    lines: list[str] = []

    def walk(node: dict, level: int = 0):
        prefix = "  " * level + "• "
        title = str(node.get("title", "")).strip()
        if title:
            lines.append(prefix + title)
        for child in node.get("children", []) or []:
            walk(child, level + 1)

    for n in nodes:
        walk(n, 0)

    return lines


@router.callback_query(F.data.startswith("open_map:"))
async def open_map_handler(callback: CallbackQuery):
    map_id = callback.data.split(":", 1)[1]
    user_id = callback.from_user.id

    
    maps = get_user_maps(user_id)
    target = next((m for m in maps if m["id"] == map_id), None)

    if not target:
        await callback.message.answer("Карта не найдена.")
        await callback.answer()
        return

    # Проверка на наличие структуры (для HTML импорта она пустая)
    if target.get("structure"):
        lines = _flatten_nodes(target["structure"])
        body = "\n".join(lines) if lines else "Нет данных по структуре."
    else:
        body = "📄 (Импортированная HTML-карта)"

    text = (
        f"🗺 {target['title']}\n"
        f"Глубина: {target['depth']}\n\n"
        f"{body}"
    )

    # Добавляем кнопку открытия, если есть ссылка
    reply_markup = None
    if target.get("url"):
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Открыть карту", web_app=WebAppInfo(url=target["url"]))]
        ])

    await callback.message.answer(text, reply_markup=reply_markup)
    await callback.answer()
