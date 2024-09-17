import mastodon
from bot import utils

from pyrogram import Client, filters
from pyrogram import types as t


@Client.on_message(filters.command(["surat"]) & ~filters.me)
async def kirim_surat(c: Client, m: t.Message):
    message = utils.get_text(m.text or m.caption)
    media_ids = []

    status = ""
    text = ""

    if message:
        status = f'"{message}"\n\n'

    m_state = await m.reply("__Tunggu ya...__")

    if utils.is_media(m):
        if not utils.is_media_met_requirements(m):
            return await m_state.edit(
                "Ukuran media terlalu besar, lihat persyaratan di bawah\n\nhttps://docs.joinmastodon.org/user/posting/#attachments"
            )

        dl_text = "__Pesan media terdeteksi, sedang mengunduh...__"
        await m_state.edit(dl_text)

        try:

            async def progress(current, total, text):
                percent = current * 100 / total
                if percent % 50 == 0:
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

    if not message and not utils.is_media(m):
        return await m_state.edit("Pesan /surat tidak boleh kosong!")

    user = m.from_user

    status += f"- {utils.get_full_name(user)} | https://{user.username}.t.me"

    data, is_error = await mastodon.send_status(
        status, media_ids=media_ids, spoiler=utils.is_spoiler(m)
    )

    if is_error:
        return await m_state.edit(data["error"])

    if message:
        text = f'**"{message}"**\n\n'

    text += f"__- {utils.get_full_name(user)} (@{user.username})__\n\n"
    text += data["url"]

    return await m_state.edit(text)
