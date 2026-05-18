import discord
from discord.ext import commands
import asyncio
import random
from flask import Flask
import threading
import os

# =========================
# FLASK SERVER
# =========================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot aktif!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_web).start()

# =========================
# DISCORD BOT
# =========================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================
# GLOBAL
# =========================

mac_devam_ediyor = False

takim_1_adi = "Ev Sahibi"
takim_1_kadro = {}

takim_2_adi = "Deplasman"
takim_2_kadro = {}

sari_kartlar = {}

# =========================
# POZİSYONLAR
# =========================

normal_pozisyonlar = [
    "orta sahada çalımlar atıyor!",
    "sağ kanattan indi!",
    "ceza sahası dışından vurdu!",
    "savunma arkasına sarktı!",
    "uzak köşeye plase gönderdi!",
    "harika kafa vurdu!",
    "rakiplerini geçti!"
]

stoper_pozisyonlar = [
    "{defans} kritik müdahaleyi yaptı!",
    "{defans} son anda araya girdi!",
    "{defans} topu uzaklaştırdı!"
]

direk_pozisyonlar = [
    "ŞUT VE TOP DİREKTEN DÖNDÜ!",
    "Top direkten geri geldi!"
]

faul_pozisyonlar = [
    "{hucumcu} yerde kaldı, faul!",
    "{hucumcu}'ya sert müdahale!"
]

# =========================
# BOT READY
# =========================

@bot.event
async def on_ready():
    print(f"Bot aktif: {bot.user}")

# =========================
# TAKIM KUR
# =========================

@bot.command(name="takimkur")
async def takimkur(ctx, *, icerik: str):

    global takim_1_adi
    global takim_1_kadro

    global takim_2_adi
    global takim_2_kadro

    try:

        parcalar = icerik.split("/")

        takim_adi = parcalar[0].strip()

        oyuncular = {}

        for oyuncu in parcalar[1].split(","):

            veri = oyuncu.strip()

            if ":" in veri:

                mevki, isim = veri.split(":", 1)

                oyuncular[isim.strip()] = mevki.strip().upper()

        if not takim_1_kadro:

            takim_1_adi = takim_adi
            takim_1_kadro = oyuncular

            ilk11 = "\n".join(
                [
                    f"{mevki} - {isim}"
                    for isim, mevki
                    in takim_1_kadro.items()
                ]
            )

            await ctx.send(
                f"⚽ {takim_1_adi} kuruldu!\n\n"
                f"{ilk11}"
            )

        else:

            takim_2_adi = takim_adi
            takim_2_kadro = oyuncular

            ilk11 = "\n".join(
                [
                    f"{mevki} - {isim}"
                    for isim, mevki
                    in takim_2_kadro.items()
                ]
            )

            await ctx.send(
                f"⚽ {takim_2_adi} kuruldu!\n\n"
                f"{ilk11}"
            )

    except:

        await ctx.send(
            "❌ Kullanım:\n\n"
            "!takimkur Galatasaray /\n"
            "GK: Muslera,\n"
            "RB: Kaan Ayhan,\n"
            "CB: Davinson,\n"
            "LB: Köhn,\n"
            "CM: Torreira,\n"
            "RW: Ziyech,\n"
            "LW: Kerem,\n"
            "ST: Icardi"
        )

# =========================
# KART KONTROL
# =========================

async def kart_kontrol(
    ctx,
    oyuncu,
    takim_adi,
    kadro
):

    kart_sansi = random.random()

    if kart_sansi < 0.50:

        await ctx.send(
            f"🗣 **[Erdem]:** "
            f"Hakem {oyuncu} oyuncusunu uyardı."
        )

    elif kart_sansi < 0.90:

        if oyuncu not in sari_kartlar:

            sari_kartlar[oyuncu] = 1

            await ctx.send(
                f"🟨 **[Erdem]:** "
                f"{takim_adi} takımından "
                f"{oyuncu} sarı kart gördü!"
            )

        else:

            sari_kartlar[oyuncu] += 1

            if sari_kartlar[oyuncu] == 2:

                await ctx.send(
                    f"🟥 **[Erdem]:** "
                    f"{oyuncu} ikinci sarıdan atıldı!"
                )

                if oyuncu in kadro:
                    del kadro[oyuncu]

    else:

        await ctx.send(
            f"🟥 **[Erdem]:** "
            f"DOĞRUDAN KIRMIZI KART!\n"
            f"{oyuncu} oyundan atıldı!"
        )

        if oyuncu in kadro:
            del kadro[oyuncu]

# =========================
# GOL ŞANSI
# =========================

def gol_ihtimali(mevki):

    if mevki == "ST":
        return 0.60

    elif mevki in ["RW", "LW"]:
        return 0.40

    elif mevki in ["CM"]:
        return 0.25

    elif mevki in ["RB", "LB"]:
        return 0.15

    elif mevki in ["CB"]:
        return 0.08

    return 0.02

# =========================
# POZİSYON OYNAT
# =========================

async def pozisyon_oynat(
    ctx,
    dakika,
    t1_skor,
    t2_skor
):

    if not takim_1_kadro or not takim_2_kadro:
        return t1_skor, t2_skor

    secilen_takim = random.choice([1, 2])

    olasilik = random.random()

    if secilen_takim == 1:

        atak_takim = takim_1_adi
        defans_takim = takim_2_adi

        atak_kadro = takim_1_kadro
        defans_kadro = takim_2_kadro

    else:

        atak_takim = takim_2_adi
        defans_takim = takim_1_adi

        atak_kadro = takim_2_kadro
        defans_kadro = takim_1_kadro

    hucumcu = random.choice(
        list(atak_kadro.keys())
    )

    hucum_mevki = atak_kadro[hucumcu]

    if defans_kadro:

        defansci = random.choice(
            list(defans_kadro.keys())
        )

    else:

        defansci = "Savunma"

    # STOPER POZİSYONU
    if olasilik < 0.30:

        pozisyon = random.choice(
            stoper_pozisyonlar
        ).format(defans=defansci)

        await ctx.send(
            f"🎙 [{dakika}'] "
            f"[{defans_takim}] "
            f"{pozisyon}"
        )

    # FAUL
    elif olasilik < 0.50:

        pozisyon = random.choice(
            faul_pozisyonlar
        ).format(hucumcu=hucumcu)

        await ctx.send(
            f"🎙 [{dakika}'] "
            f"[FAUL] "
            f"{pozisyon}"
        )

        if secilen_takim == 1:

            await kart_kontrol(
                ctx,
                defansci,
                takim_2_adi,
                takim_2_kadro
            )

        else:

            await kart_kontrol(
                ctx,
                defansci,
                takim_1_adi,
                takim_1_kadro
            )

    # DİREK
    elif olasilik < 0.55:

        pozisyon = random.choice(
            direk_pozisyonlar
        )

        await ctx.send(
            f"🎙 [{dakika}'] "
            f"[{atak_takim}] "
            f"{pozisyon}"
        )

    # ATAK
    else:

        pozisyon = random.choice(
            normal_pozisyonlar
        )

        await ctx.send(
            f"🎙 [{dakika}'] "
            f"[{atak_takim}] "
            f"{hucumcu} ({hucum_mevki}) "
            f"{pozisyon}"
        )

        gol_sansi = gol_ihtimali(
            hucum_mevki
        )

        if random.random() < gol_sansi:

            # KALECİ
            kaleciler = [
                isim
                for isim, mevki
                in defans_kadro.items()
                if mevki == "GK"
            ]

            kaleci = (
                kaleciler[0]
                if kaleciler
                else "Kaleci"
            )

            # KURTARIŞ ŞANSI
            if random.random() < 0.30:

                await ctx.send(
                    f"🧤 **[Erdem]:** "
                    f"{kaleci} inanılmaz çıkardı!"
                )

            else:

                if secilen_takim == 1:
                    t1_skor += 1
                else:
                    t2_skor += 1

                await ctx.send(
                    f"⚽ **[Erdem]:** "
                    f"GOOOOLLL!!\n"
                    f"{hucumcu} ({hucum_mevki}) "
                    f"ağları havalandırdı!\n\n"
                    f"📊 Skor:\n"
                    f"{takim_1_adi} {t1_skor} - "
                    f"{t2_skor} {takim_2_adi}"
                )

    return t1_skor, t2_skor

# =========================
# MAÇ BAŞLAT
# =========================

@bot.command(name="macbaslat")
async def macbaslat(ctx):

    global mac_devam_ediyor
    global sari_kartlar

    global takim_1_adi
    global takim_1_kadro

    global takim_2_adi
    global takim_2_kadro

    if not takim_1_kadro or not takim_2_kadro:

        await ctx.send(
            "❌ Önce iki takım kur!"
        )

        return

    if mac_devam_ediyor:

        await ctx.send(
            "⚠ Maç zaten devam ediyor!"
        )

        return

    mac_devam_ediyor = True

    sari_kartlar.clear()

    t1_skor = 0
    t2_skor = 0

    # =========================
    # SPİKER AÇILIŞ
    # =========================

    await ctx.send(
        f"🎙 **[Erdem]:** "
        f"Merhaba futbolseverler!\n"
        f"{takim_1_adi} ile "
        f"{takim_2_adi} karşı karşıya geliyor!"
    )

    await asyncio.sleep(3)

    await ctx.send(
        f"🗣 **[Berat]:** "
        f"Harika bir atmosfer var Erdem!"
    )

    await asyncio.sleep(3)

    ilk11_1 = "\n".join(
        [
            f"{mevki} - {isim}"
            for isim, mevki
            in takim_1_kadro.items()
        ]
    )

    ilk11_2 = "\n".join(
        [
            f"{mevki} - {isim}"
            for isim, mevki
            in takim_2_kadro.items()
        ]
    )

    await ctx.send(
        f"📋 **{takim_1_adi} İlk 11:**\n\n"
        f"{ilk11_1}"
    )

    await asyncio.sleep(3)

    await ctx.send(
        f"📋 **{takim_2_adi} İlk 11:**\n\n"
        f"{ilk11_2}"
    )

    await asyncio.sleep(3)

    await ctx.send(
        "🟢 Hakem düdüğü çaldı "
        "ve maç başladı!"
    )

    # =========================
    # DAKİKALAR
    # =========================

    dakikalar = list(range(1, 91))

    for dakika in dakikalar:

        if not mac_devam_ediyor:
            break

        await asyncio.sleep(1.5)

        t1_skor, t2_skor = await pozisyon_oynat(
            ctx,
            dakika,
            t1_skor,
            t2_skor
        )

    # =========================
    # MAÇ SONU
    # =========================

    if mac_devam_ediyor:

        await ctx.send(
            f"🏁 **[Erdem]:** "
            f"Ve maç sona erdi!\n\n"
            f"📊 Final Skoru:\n"
            f"{takim_1_adi} {t1_skor} - "
            f"{t2_skor} {takim_2_adi}"
        )

    # RESET

    takim_1_adi = "Ev Sahibi"
    takim_1_kadro = {}

    takim_2_adi = "Deplasman"
    takim_2_kadro = {}

    mac_devam_ediyor = False

# =========================
# MAÇ BİTİR
# =========================

@bot.command(name="macbitir")
async def macbitir(ctx):

    global mac_devam_ediyor

    global takim_1_adi
    global takim_1_kadro

    global takim_2_adi
    global takim_2_kadro

    mac_devam_ediyor = False

    takim_1_adi = "Ev Sahibi"
    takim_1_kadro = {}

    takim_2_adi = "Deplasman"
    takim_2_kadro = {}

    await ctx.send(
        "⏹ Maç zorla bitirildi."
    )

# =========================
# TOKEN
# =========================

bot.run(
    os.environ.get("DISCORD_TOKEN")
            )
