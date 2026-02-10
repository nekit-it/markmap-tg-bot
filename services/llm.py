import json
import requests

from config import YANDEX_API_KEY, YANDEX_FOLDER_ID, YANDEX_API_URL, YANDEX_OCR_URL, YANDEX_URL, OPENROUTER_API_KEY, OPENROUTER_API_URL

MODEL_MAPPING = {
    "YandexGPT 🇷🇺": "yandexgpt",
    "GPT-4o Mini 🤖": "openai/gpt-4o-mini",
    "Gemini 2.0 Flash ⚡️": "google/gemini-3-flash-preview",
    "DeepSeek R1 🐋": "arcee-ai/trinity-large-preview:free",
}

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


def generate_with_yandex(prompt):
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
            "maxTokens": "2000",
        },
        "messages": [
            {"role": "system", "text": SYSTEM_PROMPT},
            {"role": "user", "text": prompt},
        ],
        "jsonObject": True,
    }
    resp = requests.post(YANDEX_API_URL, headers=headers, data=json.dumps(body))
    resp.raise_for_status()
    data = resp.json()
    return data["result"]["alternatives"][0]["message"]["text"]

def generate_with_openrouter(prompt, model_id):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://telegram.org", # Требование OpenRouter
        "X-Title": "MapBot",
    }
    
    # Для DeepSeek R1 лучше не использовать json_object, он сам справляется,
    # но для остальных (GPT, Gemini) это повышает стабильность.
    response_format = {"type": "json_object"} if "deepseek" not in model_id else None

    body = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "response_format": response_format
    }

    resp = requests.post(OPENROUTER_API_URL, headers=headers, data=json.dumps(body))
    
    if resp.status_code != 200:
        print(f"OpenRouter Error: {resp.text}")
        
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def generate_markmap(text: str, depth: str, model_name: str = "YandexGPT 🇷🇺") -> dict:
    """
    Возвращает dict с структурой карты.
    model_name: текст с кнопки (ключ из MODEL_MAPPING)
    """
    prompt = f"""
Контекст документа:
{text}

Глубина анализа: {DEPTH_HINTS.get(depth, "")}
"""
    
    model_id = MODEL_MAPPING.get(model_name, "yandexgpt")
    print(f"Using model: {model_name} -> {model_id}")

    try:
        if model_id == "yandexgpt":
            content = generate_with_yandex(prompt)
        else:
            content = generate_with_openrouter(prompt, model_id)

        print("RAW LLM CONTENT:", repr(content))
        
        # Очистка markdown блоков json, если они есть
        clean_content = content.replace("```json", "").replace("```", "").strip()
        obj = json.loads(clean_content)

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
            flat_lines = ["- Ошибка структуры данных"]

        # Markmap markdown
        markmap_lines = [f"# {title}"]

        def walk_markmap(node, level=1):
            indent = "  " * level
            markmap_lines.append(f"{indent}- {str(node.get('title', '')).strip()}")
            for child in node.get("children", []) or []:
                walk_markmap(child, level + 1)

        for n in nodes:
            walk_markmap(n, level=1)

        return {
            "title": title,
            "nodes": nodes,
            "flat": flat_lines,
            "markmap": "\n".join(markmap_lines),
        }

    except Exception as e:
        print("PARSE/GENERATE ERROR:", e)
        return {
            "title": "Ошибка генерации",
            "nodes": [],
            "flat": ["- Произошла ошибка при обращении к нейросети"],
            "markmap": "# Ошибка генерации\n  - Попробуйте другую модель",
        }
