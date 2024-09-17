import mastodon
from bot import utils

from pyrogram import Client, filters
from pyrogram import types as t


@Client.on_message(filters.command(["surat"]) & ~filters.me)
async def kirim_surat(c: Client, m: t.Message):
    abs_msg = utils.get_absolute_message(m)
    msg_text = utils.get_text(m.text or m.caption)
    user = m.from_user

    if not msg_text:
        # if msg text or caption not included use the replied msg instead
        msg_text = utils.get_text(abs_msg.text or abs_msg.caption)
        user = abs_msg.from_user

    media_ids = []
    status = ""
    text = ""

    if msg_text:
        status = f'"{msg_text}"\n\n'

    m_state = await m.reply("__Tunggu ya...__")

    if utils.is_media(m):
        if not utils.is_media_met_requirements(m):
            return await m_state.edit(
                "Ukuran media terlalu besar, lihat persyaratan di bawah\n\nhttps://docs.joinmastodon.org/user/posting/#attachments"
            )

        dl_text = "__Pesan media terdeteksi, sedang mengunduh...__"
        await m_state.edit(f"{dl_text}\n\n0%")

        try:

            async def progress(current, total, text):
                percent = current * 100 / total
                if percent % 20 == 0:
                    await m_state.edit(f"{text}\n\n{percent:.1f}%")

            byte_obj = await c.download_media(
                utils.get_absolute_message(m),
                in_memory=True,
                progress=progress,
                progress_args=(dl_text,),
            )
        except TimeoutError as e:
            return await m_state.edit(
                f"TimeoutError: Unduh media melebihi batas waktu\n\n{e or ''}".strip()
            )

        await m_state.edit("__Media berhasil diunduh, melanjutkan proses upload...__")

        data, is_error = await mastodon.upload(byte_obj, filename=byte_obj.name)

        if is_error:
            return await m_state.edit(data["error"])

        media_ids.append(data["id"])

    if not msg_text and not m.reply_to_message and not utils.is_media(m):
        return await m_state.edit("Pesan /surat tidak boleh kosong!")

    status += f"- {utils.get_full_name(user)} | https://{user.username}.t.me"

    data, is_error = await mastodon.send_status(
        status, media_ids=media_ids, spoiler=utils.is_spoiler(m)
    )

    if is_error:
        return await m_state.edit(data["error"])

    if msg_text:
        text = f'**"{msg_text}"**\n\n'

    text += f"__- {utils.get_full_name(user)} (@{user.username})__\n\n"
    text += data["url"]

    return await m_state.edit(text)
