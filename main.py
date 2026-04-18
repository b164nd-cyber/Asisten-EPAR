from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import os

from sheet_service import append_row

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

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("beli", beli))

    app.run_polling()

if __name__ == "__main__":
    main()
