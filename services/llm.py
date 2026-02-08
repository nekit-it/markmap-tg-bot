import json
import requests

from config import YANDEX_API_KEY, YANDEX_FOLDER_ID, YANDEX_API_URL, YANDEX_OCR_URL, YANDEX_URL

SYSTEM_PROMPT = """
Ты помощник, который строит структурированную интеллект-карту (mindmap) документа.

Отвечай СТРОГО в JSON, без текста до или после.
Формат:

{
  "title": "Краткое название карты",
  "nodes": [
    {
      "title": "Краткий заголовок узла",
      "children": [
        {
          "title": "Подузел",
          "children": []
        }
      ]
    }
  ]
}

Правила:
- Только JSON, без комментариев и пояснений.
- title и у корня, и у узлов — короткие фразы.
- children — массив таких же объектов, можно делать 1–2 уровня вложенности.
- Не используй null, если нет детей — ставь "children": [].
- Пиши по-русски.
"""

DEPTH_HINTS = {
    "Лёгкая": "Сделай очень краткую карту, только ключевые идеи.",
    "Средняя": "Сбалансированная карта с основными пунктами.",
    "Глубокая": "Детальная карта с логической структурой.",
}


def generate_markmap(text: str, depth: str) -> dict:
    """
    Возвращает dict:
    {
      "title": str,
      "nodes": [...],   # список узлов (dict)
      "flat": [...],    # плоский список строк для чата
      "markmap": str    # markdown для Markmap
    }
    """

    prompt = f"""
Контекст документа:
{text}

Глубина анализа: {DEPTH_HINTS.get(depth, "")}
"""

    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json",
        "x-folder-id": YANDEX_FOLDER_ID,
    }

    body = {
        "modelUri": YANDEX_URL,
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": "1024",
        },
        "messages": [
            {"role": "system", "text": SYSTEM_PROMPT},
            {"role": "user", "text": prompt},
        ],
        "jsonObject": True,
    }

    resp = requests.post(YANDEX_API_URL, headers=headers, data=json.dumps(body))
    print("YANDEX RESPONSE:", resp.status_code, resp.text)
    resp.raise_for_status()

    data = resp.json()

    try:
        alt = data["result"]["alternatives"][0]
        content = alt["message"]["text"]
        print("RAW LLM CONTENT:", repr(content))

        # Парсим JSON
        obj = json.loads(content)

        title = obj.get("title") or "Без названия"
        nodes = obj.get("nodes") or []

        # Плоский список строк для Telegram
        flat_lines = []

        def walk(node, level=0):
            prefix = "  " * level + "- "
            flat_lines.append(prefix + str(node.get("title", "")).strip())
            for child in node.get("children", []) or []:
                walk(child, level + 1)

        for n in nodes:
            walk(n, level=0)

        if not flat_lines:
            flat_lines = [
                "- Введение",
                "- Ключевые идеи",
                "- Основные пункты",
                "- Выводы",
            ]

        # Markmap markdown
        # https://markmap.js.org/repl
        markmap_lines = [f"# {title}"]

        def walk_markmap(node, level=1):
            indent = "  " * level
            markmap_lines.append(f"{indent}- {str(node.get('title', '')).strip()}")
            for child in node.get("children", []) or []:
                walk_markmap(child, level + 1)

        for n in nodes:
            walk_markmap(n, level=1)

        if len(markmap_lines) == 1:  # только заголовок
            markmap_lines.extend(
                [
                    "  - Введение",
                    "  - Ключевые идеи",
                    "  - Основные пункты",
                    "  - Выводы",
                ]
            )

        return {
            "title": title,
            "nodes": nodes,
            "flat": flat_lines,
            "markmap": "\n".join(markmap_lines),
        }

    except Exception as e:
        print("PARSE ERROR:", e)
        # Полный fallback
        return {
            "title": "Ошибка генерации",
            "nodes": [],
            "flat": [
                "- Введение",
                "- Ключевая идея",
                "- Основные пункты",
                "- Выводы",
            ],
            "markmap": "# Ошибка генерации\n  - Введение\n  - Ключевая идея\n  - Основные пункты\n  - Выводы",
        }