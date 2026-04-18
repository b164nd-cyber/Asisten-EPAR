from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import NetworkError, TimedOut
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

    # run_polling() adalah blocking call yang mengelola event loop-nya sendiri
    # JANGAN di-await dan JANGAN dibungkus asyncio.run()
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    main()
