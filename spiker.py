import discord
from discord.ext import commands
import asyncio
import random

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

mac_devam_ediyor = False
takim_1_adi = "Ev Sahibi"
takim_1_kadro = []
takim_2_adi = "Deplasman"
takim_2_kadro = []

# Kart takibi için sözlük
sari_kartlar = {}

# Detaylı Pozisyon Havuzu
normal_pozisyonlar = [
    "orta sahada şık bir çalımla önünü boşalttı, pasını aktarıyor.",
    "sağ kanattan adeta bir rüzgar gibi çizgiye indi, içeriye kesiyor!",
    "ceza sahası dışından kaleyi gördü, sert vurdu! Kaleci iki hamlede kontrol ediyor.",
    "savunmanın arkasına sızdı ama yardımcı hakemin bayrağı havada! Ofsayt!",
    "uzak köşeye harika plase gönderdi, top az farkla auta çıkıyor!",
    "kornerden gelen topa harika yükseldi, kafa vuruşu! Üst ağlarda kaldı.",
    "rakiplerini tek tek ipe dizdi, ceza sahasına girdi ama son anda savunma ayak koydu!"
]

stoper_pozisyonlar = [
    "son adam pozisyonunda inanılmaz bir kademeyle {hucumcu}'nun şutunu engelledi! Muazzam müdahale!",
    "kaleciyle karşı karşıya kalacaktı ama {defans} adeta gövdesini siper etti ve topu kaptı!",
    "hava topu mücadelesinde {hucumcu}'ya geçit vermedi, topu uzaklaştırıyor."
]

direk_pozisyonlar = [
    "ceza sahası çizgi üzerinden füze gönderdi! VE TOP DİREKTEN DÖNDÜ! İnanılmaz bir an!",
    "kalecinin öne çıktığını gördü, aşırtma vuruş... ÇAT! Direğe çarpan top oyun alanına geri dönüyor!"
]

faul_pozisyonlar = [
    "hızla ilerleyen {hucumcu}'yu arkadan çekerek durdurdu. Hakem faul noktasını gösteriyor.",
    "orta sahada {hucumcu}'ya sert bir müdahalede bulundu. Hakem oyunu durdurdu."
]

@bot.event
async def on_ready():
    print(f"Kadro motoru hazır. Bot {bot.user} olarak giriş yaptı!")

@bot.command()
async def takimkur(ctx, *, icerik: str):
    global takim_1_adi, takim_1_kadro, takim_2_adi, takim_2_kadro
    try:
        parcalar = icerik.split("/")
        takim_adi = parcalar[0].strip()
        oyuncular = [o.strip() for o in parcalar[1].split(",")]
        
        if not takim_1_kadro or takim_1_adi == "Ev Sahibi":
            takim_1_adi = takim_adi
            takim_1_kadro = oyuncular
            await ctx.send(f"⚽ **{takim_1_adi}** kuruldu! Kadro: {', '.join(takim_1_kadro)}")
        else:
            takim_2_adi = takim_adi
            takim_2_kadro = oyuncular
            await ctx.send(f"⚽ **{takim_2_adi}** kuruldu! Kadro: {', '.join(takim_2_kadro)}")
    except:
        await ctx.send("❌ Hatalı kullanım! Örnek: `!takımkur Beşiktaş / Oyuncu1, Oyuncu2`")

async def kart_kontrol(ctx, oyuncu, takim_adi, kadro):
    kart_sansi = random.random()
    
    # %50 ihtimalle hakem sadece sözlü uyarır, kart vermez
    if kart_sansi < 0.50:
        await ctx.send(f"🗣 **[Erdem]:** Hakem oraya gitti, {oyuncu}'yu sert bir dille uyarıyor ama kart çıkmadı.\n🗣 **[Berat]:** Evet Erdem, bu dakikada hakem kartına başvurmak istemedi.")
    
    # %40 ihtimalle sarı kart
    elif kart_sansi < 0.90:
        if oyuncu not in sari_kartlar:
            sari_kartlar[oyuncu] = 1
            await ctx.send(f"🟨 **[Erdem]:** Ve hakem elini cebine attı! {takim_adi} takımından **{oyuncu}** sarı kart görüyor!")
        else:
            sari_kartlar[oyuncu] += 1
            if sari_kartlar[oyuncu] == 2:
                await ctx.send(f"🟥 **[Erdem]:** İNANILMAZ BİR AN! {oyuncu}'nun daha önceden sarı kartı vardı! Hakem ikinci sarıdan **KIRMIZI KARTINI** çıkardı!!\n🗣 **[Berat]:** Büyük sorumsuzluk Erdem, takımı {takim_adi} şimdi sahada 10 kişi kaldı!")
                if oyuncu in kadro:
                    kadro.remove(oyuncu)
                    
    # %10 ihtimalle doğrudan kırmızı kart
    else:
        await ctx.send(f"🟥 **[Erdem]:** AMAN ALLAH'IM! DOĞRUDAN KIRMIZI KART! Hakem tereddütsüz kırmızıyı çıkardı! **{oyuncu}** oyundan atılıyor!\n🗣 **[Berat]:** Çok sert bir müdahaleydi Erdem, kırmızı kart son derece haklı bir karar.")
        if oyuncu in kadro:
            kadro.remove(oyuncu)

async def pozisyon_oynat(ctx, dakika, t1_skor, t2_skor):
    if not takim_1_kadro or not takim_2_kadro:
        return t1_skor, t2_skor

    secilen_takim = random.choice([1, 2])
    olasilik = random.random()
    
    if secilen_takim == 1:
        atak_takim, defans_takim = takim_1_adi, takim_2_adi
        atak_kadro, defans_kadro = takim_1_kadro, takim_2_kadro
    else:
        atak_takim, defans_takim = takim_2_adi, takim_1_adi
        atak_kadro, defans_kadro = takim_2_kadro, takim_1_kadro

    hucumcu = random.choice(atak_kadro)
    defansci = random.choice(defans_kadro) if defans_kadro else "Savunma"

    # 1. SENARYO: STOPER DURDURMASI (%30)
    if olasilik < 0.30:
        pozisyon = random.choice(stoper_pozisyonlar).format(defans=defansci, hucumcu=hucumcu)
        await ctx.send(f"🎙 **[{dakika}'] [{defans_takim}]** {pozisyon}")
        
    # 2. SENARYO: FAUL DURUMU (%20)
    elif olasilik < 0.50:
        pozisyon = random.choice(faul_pozisyonlar).format(savunma=defansci, hucumcu=hucumcu)
        await ctx.send(f"🎙 **[{dakika}'] [FAUL]** {defansci}, {pozisyon}")
        # Takılmaya sebep olan sleep kaldırıldı, direkt kart kontrolüne geçiyor
        if secilen_takim == 1:
            await kart_kontrol(ctx, defansci, takim_2_adi, takim_2_kadro)
        else:
            await kart_kontrol(ctx, defansci, takim_1_adi, takim_1_kadro)

    # 3. SENARYO: DİREKTEN DÖNEN TOP (%5)
    elif olasilik < 0.55:
        pozisyon = random.choice(direk_pozisyonlar).format(oyuncu=hucumcu)
        await ctx.send(f"🎙 **[{dakika}'] [{atak_takim}]** {pozisyon}\n🗣 **[Berat]:** İnanılmaz bir şanssızlık anı Erdem, kaleci çaresiz kalmıştı!")

    # 4. SENARYO: NORMAL ATAK VE GOL İHTİMALİ (%45)
    else:
        pozisyon = random.choice(normal_pozisyonlar).format(oyuncu=hucumcu)
        await ctx.send(f"🎙 **[{dakika}'] [{atak_takim}]** {hucumcu} {pozisyon}")
        
        if random.random() < 0.35 and ("auta" not in pozisyon and "Ofsayt" not in pozisyon and "kontrol ediyor" not in pozisyon):
            if secilen_takim == 1:
                t1_skor += 1
            else:
                t2_skor += 1
            await ctx.send(f"⚽ **[Erdem]: GOOOOLLL!! GOOOOLLL!!** {hucumcu} muhteşem vurdu ve top ağlarda!\n🗣 **[Berat]:** Harika bir bitiricilik Erdem, topu adeta iğne deliğinden geçirdi!\n📊 **Skor:** {takim_1_adi} {t1_skor} - {t2_skor} {takim_2_adi}")

    return t1_skor, t2_skor

@bot.command()
async def maçbaşlat(ctx):
    global mac_devam_ediyor, takim_1_adi, takim_1_kadro, takim_2_adi, takim_2_kadro, sari_kartlar
    if not takim_1_kadro or not takim_2_kadro:
        await ctx.send("❌ Maçı başlatmak için önce iki takımı da kurmalısın!")
        return
    if mac_devam_ediyor:
        await ctx.send("⚠ Maç zaten devam ediyor!")
        return
        
    mac_devam_ediyor = True
    sari_kartlar.clear()
    t1_skor, t2_skor = 0, 0
    
    # --- SPİKER AÇILIŞI VE İLK 11'LER ---
    await ctx.send(f"🎙 **[Erdem]:** Merhaba sevgili futbolseverler! Muhteşem bir atmosferde, dev derbide karşınızdayız. Yanımda yorumcum Berat var. Berat hoş geldin, heyecan dorukta!")
    await asyncio.sleep(4)
    await ctx.send(f"🗣 **[Berat]:** Hoş bulduk Erdem. Gerçekten harika bir hava var, iki takıma da başarılar diliyorum. Kadrolar nefes kesiyor.")
    await asyncio.sleep(4)
    
    # İlk 11'leri sayma
    await ctx.send(f"📋 **[Erdem]:** Hemen takımların sahaya çıkan kadrolarını aktaralım.\n🏠 **{takim_1_adi} İlk 11:** {', '.join(takim_1_kadro)}")
    await asyncio.sleep(4)
    await ctx.send(f"📋 **[Erdem]:** Ve konuk ekip!\n🚀 **{takim_2_adi} İlk 11:** {', '.join(takim_2_kadro)}")
    await asyncio.sleep(4)
    await ctx.send(f"🟢 **[Erdem]:** Hakem tribünleri kontrol etti, saatine baktı ve dev maçın başlama düdüğü çaldı! İki takıma da başarılar!")
    
    # --- İLK YARI (20 POZİSYON) ---
    ilk_yari_dakikalar = [2, 4, 7, 9, 11, 14, 16, 19, 21, 24, 26, 28, 31, 33, 35, 38, 40, 42, 44, 45]
    for dak in ilk_yari_dakikalar:
        if not mac_devam_ediyor: break
        await asyncio.sleep(7)
        t1_skor, t2_skor = await pozisyon_oynat(ctx, dak, t1_skor, t2_skor)

    if mac_devam_ediyor:
        await ctx.send(f"☕ **[45'+2] [Erdem]:** Ve hakem ilk yarının son düdüğünü çalıyor! İlk 20 pozisyonluk maraton bitti.\n🗣 **[Berat]:** Tempolu ve taktiksel bir ilk yarı izledik Erdem.\n📊 **İlk Yarı Skoru:** {takim_1_adi} {t1_skor} - {t2_skor} {takim_2_adi}\nDevre arası başladı (15 saniye)...")
        await asyncio.sleep(15)
        
    # --- İKİNCİ YARI (20 POZİSYON) ---
    if mac_devam_ediyor:
        await ctx.send(f"🔥 **[46'] [Erdem]:** Sevgili seyirciler, takımlar sahaya döndü. İkinci yarıda yeniden mikrofondayız. Berat, ikinci yarıdan beklentin ne?")
        await asyncio.sleep(3)
        await ctx.send(f"🗣 **[Berat]:** Erdem iki takım da risk alacaktır, gol veya goller izleyebiliriz. İkinci yarı başladı!")

    ikinci_yari_dakikalar = [47, 49, 51, 54, 56, 59, 61, 64, 66, 68, 71, 73, 75, 78, 80, 83, 85, 87, 89, 90]
    for dak in ikinci_yari_dakikalar:
        if not mac_devam_ediyor: break
        await asyncio.sleep(7)
        t1_skor, t2_skor = await pozisyon_oynat(ctx, dak, t1_skor, t2_skor)
                
    # --- UZATMALAR (10 POZİSYON) ---
    if mac_devam_ediyor and t1_skor == t2_skor:
        await ctx.send(f"🚨 **[90'] [Erdem]:** Eşitlik bozulmadı! Maç uzatmalara gidiyor seyirciler!\n🗣 **[Berat]:** Fizik gücü yüksek olanın kazanacağı dakikalara girdik Erdem.")
        await asyncio.sleep(8)
        
        uzat_dakikalar = [93, 96, 99, 102, 105, 108, 111, 114, 117, 120]
        for dak in uzat_dakikalar:
            if not mac_devam_ediyor: break
            await asyncio.sleep(7)
            t1_skor, t2_skor = await pozisyon_oynat(ctx, dak, t1_skor, t2_skor)

    # --- SERİ PENALTILAR ---
    if mac_devam_ediyor and t1_skor == t2_skor:
        await ctx.send(f"🔥 **[120'] [Erdem]:** İnanılmaz! Uzatmalarda da düğüm çözülmedi. İş penaltılara kaldı Berat!\n🗣 **[Berat]:** Tamamen şans ve kaleci becerisi Erdem, nefesler tutuldu.")
        await asyncio.sleep(8)
        
        p1_skor, p2_skor = 0, 0
        for atis in range(1, 6):
            if not mac_devam_ediyor: break
            
            # Takım 1
            if takim_1_kadro:
                o1 = random.choice(takim_1_kadro)
                await ctx.send(f"🎯 **[{takim_1_adi}]** {o1} penaltı için topun başında geliyor...")
                await asyncio.sleep(4)
                if random.random() < 0.75:
                    p1_skor += 1
                    await ctx.send(f"⚽ **[Erdem]: GOOLL!** {o1} kaleciyi çaresiz bıraktı! (Penaltılar: {p1_skor} - {p2_skor})")
                else:
                    await ctx.send(f"❌ **[Erdem]: KAÇTI!** {o1} kaleciyi geçemedi! (Penaltılar: {p1_skor} - {p2_skor})")
                
            # Takım 2
            if takim_2_kadro:
                o2 = random.choice(takim_2_kadro)
                await ctx.send(f"🎯 **[{takim_2_adi}]** Şimdi cevap vermek için {o2} geliyor...")
                await asyncio.sleep(4)
                if random.random() < 0.75:
                    p2_skor += 1
                    await ctx.send(f"⚽ **[Erdem]: GOOLL!** {o2} ağları havalandırdı! (Penaltılar: {p1_skor} - {p2_skor})")
                else:
                    await ctx.send(f"❌ **[Erdem]: KAÇTI!** Top dışarıda! (Penaltılar: {p1_skor} - {p2_skor})")

        # Seri penaltılarda ölüm kalış devresi
        seri_no = 6
        while mac_devam_ediyor and p1_skor == p2_skor:
            await ctx.send(f"🔄 **[Erdem]:** Eşitlik yine bozulmadı! Tekli penaltılara geçiyoruz. Berat kalbim dayanmıyor!")
            await asyncio.sleep(4)
            
            o1 = random.choice(takim_1_kadro) if takim_1_kadro else "Oyuncu"
            await ctx.send(f"🎯 **[{takim_1_adi}]** {o1} topun gerisinde...")
            await asyncio.sleep(4)
            if random.random() < 0.75:
                p1_skor += 1
                await ctx.send(f"⚽ **[Erdem]: VE GOL!** {o1} çok soğukkanlı! (Penaltılar: {p1_skor} - {p2_skor})")
            else:
                await ctx.send(f"❌ **[Erdem]: KAÇIRDI!** {o1} kaçırdı, büyük fırsat! (Penaltılar: {p1_skor} - {p2_skor})")
                
            o2 = random.choice(takim_2_kadro) if takim_2_kadro else "Oyuncu"
            await ctx.send(f"🎯 **[{takim_2_adi}]** {o2} maçı bitirmek ya da uzatmak için geliyor...")
            await asyncio.sleep(4)
            if random.random() < 0.75:
                p2_skor += 1
                await ctx.send(f"⚽ **[Erdem]: GOL!** Seri devam ediyor! (Penaltılar: {p1_skor} - {p2_skor})")
            else:
                await ctx.send(f"❌ **[Erdem]: KAÇTI!** İnanılmaz bir dram!")
                
            seri_no += 1
            
        await ctx.send(f"🏆 **[Erdem]: VE MAÇ BİTTİ!** Penaltılar neticesinde kupanın sahibi **{takim_1_adi if p1_skor > p2_skor else takim_2_adi}** oluyor!\n🗣 **[Berat]:** Müthiş bir football şöleni izledik, şampiyonu tebrik ederiz Erdem. Yayını kapatıyoruz.")

    else:
        if mac_devam_ediyor:
            await ctx.send(f"🏁 **[90'+2] [Erdem]:** Ve son düdük çaldı! Bu muhteşem 40 pozisyonluk maratonun galibi belli oldu!\n🗣 **[Berat]:** Hak edilmiş bir galibiyet Erdem, kazananı kutlarız.\n🏆 **Maç Sonucu:** {takim_1_adi} {t1_skor} - {t2_skor} {takim_2_adi}")
    
    # Sıfırlama
    takim_1_adi, takim_1_kadro = "Ev Sahibi", []
    takim_2_adi, takim_2_kadro = "Deplasman", []
    mac_devam_ediyor = False

@bot.command()
async def maçbitir(ctx):
    global mac_devam_ediyor, takim_1_adi, takim_1_kadro, takim_2_adi, takim_2_kadro
    mac_devam_ediyor = False
    takim_1_adi, takim_1_kadro = "Ev Sahibi", []
    takim_2_adi, takim_2_kadro = "Deplasman", []
    await ctx.send("⏹ Spiker Erdem ve Berat yayını acil durum nedeniyle erken kapatıyor, takımlar sıfırlandı.")

# BOT TOKENİNİ BURAYA YAPIŞTIR
bot.run("BURADA_SENIN_GIZLI_BOT_SIFREN_YAZIYOR")