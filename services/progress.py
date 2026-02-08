async def update_status(message, text: str):
    try:
        await message.edit_text(text)
    except:
        pass
