from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import NetworkError, TimedOut, Conflict
from datetime import datetime
import asyncio
import logging
import os

from sheet_service import append_row

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot jagung aktif 🚀")

async def beli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 5:
        await update.message.reply_text(
            "Format salah.\nContoh: /beli PakHadi Lampung 8000 4800 cash"
        )
        return

    supplier, lokasi, qty_kg, harga, bayar = context.args[:5]

    try:
        qty_kg = int(qty_kg)
        harga = int(harga)
    except ValueError:
        await update.message.reply_text("qty_kg dan harga harus angka")
        return

    total = qty_kg * harga
    beli_id = f"BELI-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    append_row("pembelian", [
        beli_id,
        tanggal,
        supplier,
        lokasi,
        qty_kg,
        harga,
        total,
        bayar,
        "MENUNGGU_VALIDASI",
        str(update.effective_user.id),
        "",
        "",
        ""
    ])

    await update.message.reply_text(
        f"{beli_id} tercatat.\nTotal: Rp{total:,}\nStatus: MENUNGGU_VALIDASI"
    )

async def _delete_webhook(token: str):
    from telegram import Bot
    bot = Bot(token=token)
    async with bot:
        await bot.delete_webhook(drop_pending_updates=True)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("beli", beli))

    # Hapus webhook aktif agar tidak konflik dengan polling
    # asyncio.run() digunakan HANYA di sini, sebelum run_polling() mengambil alih event loop
    try:
        asyncio.run(_delete_webhook(TOKEN))
        logger.info("Webhook dihapus, memulai polling...")
    except (NetworkError, TimedOut) as e:
        logger.warning(f"Gagal menghapus webhook (akan tetap lanjut): {e}")

    # asyncio.run() menutup event loop setelah selesai, sehingga perlu dibuat
    # event loop baru agar run_polling() tidak crash dengan RuntimeError
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # run_polling() adalah blocking call yang mengelola event loop-nya sendiri
    # JANGAN di-await dan JANGAN dibungkus asyncio.run()
    # Retry dengan exponential backoff untuk handle Conflict error (instance lain
    # yang belum fully shutdown atau delay propagasi webhook deletion di Telegram API)
    MAX_RETRIES = 5
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            app.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
            )
            break  # Keluar dari loop jika polling berjalan normal
        except Conflict as e:
            if attempt < MAX_RETRIES:
                wait_seconds = 2 ** attempt  # 2, 4, 8, 16, 32 detik
                logger.warning(
                    f"Conflict error (attempt {attempt}/{MAX_RETRIES}): {e}. "
                    f"Menunggu {wait_seconds} detik sebelum retry..."
                )
                import time
                time.sleep(wait_seconds)

                # Buat ulang app dan event loop untuk retry yang bersih
                app = Application.builder().token(TOKEN).build()
                app.add_handler(CommandHandler("start", start))
                app.add_handler(CommandHandler("beli", beli))
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            else:
                logger.error(
                    f"Conflict error setelah {MAX_RETRIES} percobaan. Bot berhenti: {e}"
                )
                raise

if __name__ == "__main__":
    main()
