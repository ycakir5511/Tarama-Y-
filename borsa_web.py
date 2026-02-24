import streamlit as st
import pandas as pd
import time
from tradingview_ta import get_multiple_analysis, Interval

# Sayfa Ayarları
st.set_page_config(page_title="BIST RSI & Altın Vuruş Tarayıcı", layout="wide")

# Hisse Listeleri
BIST30 = ["AKBNK", "ALARK", "ARCLK", "ASELS", "ASTOR", "BIMAS", "EKGYO", "ENKAI", "EREGL", "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KOZAA", "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TAVHL", "TCELL", "THYAO", "TOASO", "TUPRS"]

BIST_TUM = sorted(list(set(BIST30 + [
    "A1CAP", "ACSEL", "ADEL", "ADESE", "ADGYO", "AEFES", "AFYON", "AGESA", "AGHOL", "AGROT", "AHGAZ", "AKCNS", "AKENR", "AKFGY", "AKFYE", "AKGRT", "AKMGY", "AKSA", "AKSEN", "AKSGY", "AKSUE", "AKTVY", "ALBRK", "ALCAR", "ALCTL", "ALFAS", "ALKA", "ALKIM", "ALMAD", "ALTNY", "ALVES", "ANELE", "ANGEN", "ANHYT", "ANSGR", "ANTEK", "ARASE", "ARDYZ", "ARENA", "ARSAN", "ARTMS", "ASGYO", "ASHOL", "ASURA", "ASUZU", "ATAGY", "ATAKP", "ATATP", "ATEKS", "ATLAS", "ATSYH", "AVGYO", "AVHOL", "AVOD", "AVTUR", "AYDEM", "AYEN", "AYES", "AYGAZ", "AZTEK", "BAGFS", "BAKAB", "BALAT", "BANVT", "BARMA", "BASCM", "BASGZ", "BAYRK", "BEBEK", "BEGYO", "BERA", "BEYAZ", "BFREN", "BIENP", "BIGCH", "BIPAN", "BIZIM", "BJKAS", "BLCYT", "BMSCH", "BMSTL", "BNASL", "BOBET", "BORLS", "BORSK", "BOSSA", "BRISA", "BRKO", "BRKSN", "BRMEN", "BRKVY", "BRLSM", "BRYAT", "BSOKE", "BTCIM", "BUCIM", "BURCE", "BURVA", "BVSAN", "BYDNR", "CANTE", "CASA", "CATES", "CCOLA", "CELHA", "CEMAS", "CEMTS", "CENIT", "CEOEM", "CIMSA", "CLEBI", "CONSE", "COSMO", "CRDFA", "CRFSA", "CUSAN", "CVKMD", "CWENE", "DAGHL", "DAGI", "DAPGM", "DARDL", "DGATE", "DGGYO", "DGNMO", "DIRIT", "DITAS", "DMSAS", "DNISI", "DOAS", "DOCO", "DOGUB", "DOHOL", "DOKTA", "DURDO", "DYOBY", "DZGYO", "EBEBK", "ECILC", "ECZYT", "EDATA", "EDIP", "EGEEN", "EGEPO", "EGGUB", "EGPRO", "EGSER", "EKIZ", "EKSUN", "ELITE", "EMKEL", "ENERY", "ENJSA", "ENTRA", "ERBOS", "ERCB", "ERSU", "ESCOM", "ESEN", "ETILR", "EUPWR", "EUREN", "EUHOL", "EUYO", "EYGYO", "FADE", "FENER", "FLAP", "FMIZP", "FONET", "FORMT", "FORTE", "FRIGO", "FZLGY", "GARFA", "GEDIK", "GEDZA", "GENIL", "GENTS", "GEREL", "GESAN", "GIPTA", "GLBMD", "GLCVY", "GLRYH", "GLYHO", "GMTAS", "GOKNR", "GOLTS", "GOODY", "GOZDE", "GRNYO", "GRSEL", "GSDDE", "GSDHO", "GSRAY", "GWIND", "GZNMI", "HALKB", "HATEK", "HDFGS", "HEDEF", "HKTM", "HLGYO", "HTTBT", "HUBVC", "HUNER", "HURGZ", "ICBCT", "IDGYO", "IEYHO", "IHEVA", "IHGZT", "IHLAS", "IHLGM", "IHYAY", "IMASM", "INDES", "INFO", "INGRM", "INTEM", "IPEKE", "ISATR", "ISBTR", "ISFIN", "ISGSY", "ISGYO", "ISMEN", "ISSEN", "ISYAT", "IZENR", "IZFAS", "IZMDC", "JANTS", "KAPLM", "KAREL", "KARSN", "KARTN", "KARYE", "KATMR", "KAYSE", "KCAER", "KFEIN", "KGYO", "KIMMR", "KLGYO", "KLMSN", "KLNMA", "KLRMP", "KLSYN", "KLYAS", "KMEPU", "KNFRT", "KOCAER", "KOCMT", "KONKA", "KONYA", "KORDS", "KOTON", "KPOWR", "KRGYO", "KRONT", "KRPLS", "KRSTL", "KRTEK", "KSTUR", "KTSKR", "KUTPO", "KUVVA", "KUYAS", "KZBGY", "KZGYO", "LIDER", "LIDFA", "LINK", "LMKDC", "LOGO", "LRSHO", "LUKSK", "MAALT", "MAGEN", "MAKIM", "MAKTK", "MANAS", "MARKA", "MARTI", "MAVI", "MEDTR", "MEGAP", "MEGMT", "MEPET", "MERCN", "MERIT", "MERKO", "METRO", "METUR", "MHRGY", "MIATK", "MIPAZ", "MMCAS", "MNDRS", "MNDTR", "MOBTL", "MPARK", "MRGYO", "MRSHL", "MSGYO", "MTRKS", "MTRYO", "MZHLD", "NATEN", "NETAS", "NIBAS", "NTGAZ", "NUGYO", "NUHCM", "OBAMS", "OBASE", "ONCSM", "ORCAY", "ORGE", "OTKAR", "OYAYO", "OYLUM", "OYYAT", "OZGYO", "OZKGY", "OZRDN", "OZSUB", "PAGYO", "PAMEL", "PAPIL", "PARSN", "PASEU", "PATEK", "PCILT", "PEGYO", "PEKGY", "PENTA", "PETUN", "PINSU", "PKART", "PKENT", "PLTUR", "PNLSN", "PNSUT", "POLHO", "POLTK", "PRKAB", "PRKME", "PRZMA", "PSDTC", "PSGYO", "QUAGR", "RALYH", "RAYSG", "REEDR", "RNPOL", "RODRG", "RTALB", "RUBNS", "RYGYO", "RYSAS", "SAFKR", "SAMAT", "SANEL", "SANFO", "SANKO", "SARKY", "SARTN", "SAYAS", "SDTTR", "SEGYO", "SEKFK", "SEKUR", "SELGD", "SELVA", "SEYKM", "SILVR", "SKBNK", "SKTAS", "SMART", "SMRTG", "SNGYO", "SNICA", "SNKPA", "SOKM", "SONME", "SRVGY", "SUMAS", "SUNTK", "SURGY", "TABGD", "TARKM", "TATEN", "TATGD", "TBORG", "TDGYO", "TEKTU", "TERA", "TETMT", "TEZOL", "TGSAS", "TKFEN", "TKNSA", "TLMAN", "TMPOL", "TMSN", "TRCAS", "TRGYO", "TRILC", "TSKB", "TSPOR", "TTKOM", "TTRAK", "TUCLK", "TUKAS", "TUREX", "TURSG", "UFUK", "ULAS", "ULKER", "ULLY", "ULUFA", "ULUSE", "ULUUN", "UMPAS", "UNMAS", "USAK", "VAKBN", "VAKFN", "VAKKO", "VANGD", "VBTYZ", "VERTU", "VERUS", "VESBE", "VESTL", "VKGYO", "VKING", "YAPRK", "YATAS", "YAYLA", "YEOTK", "YESIL", "YGGYO", "YGYO", "YKBNK", "YKSLN", "YONGA", "YOTAS", "YUNSA", "YYLGD", "ZEDUR", "ZOREN", "ZRGYO"
])))

# --- YARDIMCI FONKSİYONLAR ---

def veri_cek(periyot, hisse_listesi):
    sonuclar = []
    limit = 50  # Hata riskini azaltmak için limit düşürüldü
    paketler = [hisse_listesi[i:i + limit] for i in range(0, len(hisse_listesi), limit)]
    
    ilerleme_cubugu = st.progress(0)
    durum_metni = st.empty()
    
    for idx, paket in enumerate(paketler):
        tv_hisseler = [f"BIST:{h}" for h in paket]
        try:
            analizler = get_multiple_analysis(screener="turkey", interval=periyot, symbols=tv_hisseler)
            if analizler:
                for symbol, analiz in analizler.items():
                    if analiz is None or not hasattr(analiz, 'indicators'): continue
                    ind = analiz.indicators
                    sonuclar.append({
                        "Hisse": symbol.split(":")[1],
                        "Fiyat": round(ind.get("close", 0) or 0, 2),
                        "Değişim %": round(ind.get("change", 0) or 0, 2),
                        "RSI": round(ind.get("RSI", 0) or 0, 2)
                    })
            time.sleep(0.6) # Sunucu koruması
            ilerleme_cubugu.progress((idx + 1) / len(paketler))
            durum_metni.text(f"İşleniyor: Paket {idx+1}/{len(paketler)}")
        except Exception as e:
            st.error(f"Paket hatası: {e}")
            continue
    return pd.DataFrame(sonuclar)

def altin_vurus_cek(hisse_listesi):
    sonuclar = []
    limit = 40 
    paketler = [hisse_listesi[i:i + limit] for i in range(0, len(hisse_listesi), limit)]
    
    ilerleme_cubugu = st.progress(0)
    durum_metni = st.empty()
    
    for idx, paket in enumerate(paketler):
        tv_hisseler = [f"BIST:{h}" for h in paket]
        try:
            # 3 periyot sorgusu
            a1s = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_1_HOUR, symbols=tv_hisseler)
            time.sleep(0.3)
            a4s = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_4_HOURS, symbols=tv_hisseler)
            time.sleep(0.3)
            a1g = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_1_DAY, symbols=tv_hisseler)

            for s in tv_hisseler:
                res1, res4, resg = a1s.get(s), a4s.get(s), a1g.get(s)
                if res1 and res4 and resg:
                    rsi1 = res1.indicators.get("RSI", 100)
                    rsi4 = res4.indicators.get("RSI", 100)
                    rsig = resg.indicators.get("RSI", 100)
                    
                    if rsi1 < 40 and rsi4 < 40 and rsig < 40:
                        sonuclar.append({
                            "Hisse": s.split(":")[1],
                            "Fiyat": round(res1.indicators.get("close", 0), 2),
                            "RSI (1S)": round(rsi1, 2),
                            "RSI (4S)": round(rsi4, 2),
                            "RSI (1G)": round(rsig, 2)
                        })
            
            time.sleep(0.8)
            ilerleme_cubugu.progress((idx + 1) / len(paketler))
            durum_metni.text(f"Altın Vuruş: Paket {idx+1}/{len(paketler)}")
        except Exception as e:
            st.error(f"Altın Vuruş hatası: {e}")
            continue
    return pd.DataFrame(sonuclar)

# --- UI ---
st.title("🚀 BIST RSI Tarayıcı")

c1, c2, c3, c4 = st.columns([2,2,2,2])

with c1:
    evren = st.selectbox("Hisse Grubu", ["BIST 30", "BIST TÜM"])
with c2:
    periyot_str = st.selectbox("Periyot", ["1 Saat", "4 Saat", "1 Gün", "1 Hafta", "1 Ay"])
    p_map = {"1 Saat": Interval.INTERVAL_1_HOUR, "4 Saat": Interval.INTERVAL_4_HOURS, "1 Gün": Interval.INTERVAL_1_DAY, "1 Hafta": Interval.INTERVAL_1_WEEK, "1 Ay": Interval.INTERVAL_1_MONTH}
with c3:
    rsi_filtre = st.checkbox("Sadece RSI < 35")

with c4:
    st.write("")
    btn_normal = st.button("Analizi Başlat", use_container_width=True)
    btn_altin = st.button("🎯 ALTIN VURUŞ", use_container_width=True)

# Normal Analiz
if btn_normal:
    liste = BIST30 if evren == "BIST 30" else BIST_TUM
    df = veri_cek(p_map[periyot_str], liste)
    if not df.empty:
        if rsi_filtre: df = df[df["RSI"] < 35]
        st.subheader(f"Sonuçlar ({len(df)} Hisse)")
        st.dataframe(df.style.applymap(lambda x: 'background-color: #c8e6c9' if isinstance(x, float) and x < 30 else ('background-color: #ffcdd2' if isinstance(x, float) and x > 70 else ''), subset=['RSI']), use_container_width=True)
    else: st.warning("Veri bulunamadı.")

# Altın Vuruş Analizi
if btn_altin:
    st.info("BIST TÜM üzerinde 3 periyotluk (1S, 4S, 1G) RSI < 40 taraması yapılıyor...")
    df_altin = altin_vurus_cek(BIST_TUM)
    if not df_altin.empty:
        st.subheader(f"🎯 Altın Vuruş Sonuçları ({len(df_altin)} Hisse)")
        st.dataframe(df_altin.style.applymap(lambda x: 'background-color: #ffd700; color: black; font-weight: bold', subset=['Hisse']).applymap(lambda x: 'background-color: #fff9c4', subset=['RSI (1S)', 'RSI (4S)', 'RSI (1G)']), use_container_width=True)
    else: st.warning("Kriterlere uygun hisse bulunamadı.")
