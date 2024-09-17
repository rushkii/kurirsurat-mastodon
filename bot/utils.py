from pyrogram import types as t


def get_text(text: str | None):
    if not text:
        return ""

    split = text.split()

    if len(split) < 2:
        return ""

    return text.replace(f"{split[0]} ", "")


def get_full_name(user: t.User):
    if not user.last_name:
        return user.first_name

    return f"{user.first_name} {user.last_name}"


def get_absolute_message(m: t.Message):
    return m.reply_to_message or m


def is_media(m: t.Message):
    msg = get_absolute_message(m)
    return msg.media


def is_spoiler(m: t.Message):
    msg = get_absolute_message(m)
    return msg.has_media_spoiler


def is_media_met_requirements(m: t.Message):
    # you need to call is_media() first, before call this function
    # e.g:
    # if not utils.is_media(m) return
    # is_media_met_requirements(m)

    MB_16 = (1024 * 1024) * 16  # 16MB
    MB_99 = (1024 * 1024) * 99  # 99MB

    msg = get_absolute_message(m)

    return (
        (msg.photo and msg.photo.file_size <= MB_16)
        or (msg.animation and msg.animation.file_size <= MB_16)
        or (msg.video and msg.video.file_size <= MB_99)
        or (msg.audio and msg.audio.file_size <= MB_99)
        or (
            (msg.document and msg.document.file_size <= MB_99)
            and not (msg.photo or msg.animation or msg.video or msg.audio)
        )
    )
