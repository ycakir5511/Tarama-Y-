import streamlit as st
import pandas as pd
import time
from tradingview_ta import get_multiple_analysis, Interval

# Sayfa Ayarları
st.set_page_config(page_title="BIST RSI Tarayıcı", layout="wide")

# Hisse Listeleri
BIST30 = ["AKBNK", "ALARK", "ARCLK", "ASELS", "ASTOR", "BIMAS", "EKGYO", "ENKAI", "EREGL", "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KOZAA", "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TAVHL", "TCELL", "THYAO", "TOASO", "TUPRS"]
# Not: Hız için buraya sadece örnek ekledim, sizin tam listenizi buraya yapıştırabilirsiniz
BIST_TUM = sorted(list(set(BIST30 + [
            "A1CAP", "ACSEL", "ADEL", "ADESE", "ADGYO", "AEFES", "AFYON", "AGESA", "AGHOL", "AGROT", "AHGAZ", "AKCNS", "AKENR", "AKFGY", "AKFYE", "AKGRT", "AKMGY", "AKSA", "AKSEN", "AKSGY", "AKSUE", "AKTVY", "ALBRK", "ALCAR", "ALCTL", "ALFAS", "ALKA", "ALKIM", "ALMAD", "ALTNY", "ALVES", "ANELE", "ANGEN", "ANHYT", "ANSGR", "ANTEK", "ARASE", "ARCLK", "ARDYZ", "ARENA", "ARSAN", "ARTMS", "ASGYO", "ASHOL", "ASURA", "ASUZU", "ATAGY", "ATAKP", "ATATP", "ATEKS", "ATLAS", "ATSYH", "AVGYO", "AVHOL", "AVOD", "AVTUR", "AYDEM", "AYEN", "AYES", "AYGAZ", "AZTEK", "BAGFS", "BAKAB", "BALAT", "BANVT", "BARMA", "BASCM", "BASGZ", "BAYRK", "BEBEK", "BEGYO", "BERA", "BEYAZ", "BFREN", "BIENP", "BIGCH", "BIPAN", "BIZIM", "BJKAS", "BLCYT", "BMSCH", "BMSTL", "BNASL", "BOBET", "BORLS", "BORSK", "BOSSA", "BRISA", "BRKO", "BRKSN", "BRMEN", "BRKVY", "BRLSM", "BRYAT", "BSOKE", "BTCIM", "BUCIM", "BURCE", "BURVA", "BVSAN", "BYDNR", "CANTE", "CASA", "CATES", "CCOLA", "CELHA", "CEMAS", "CEMTS", "CENIT", "CEOEM", "CIMSA", "CLEBI", "CONSE", "COSMO", "CRDFA", "CRFSA", "CUSAN", "CVKMD", "CWENE", "DAGHL", "DAGI", "DAPGM", "DARDL", "DGATE", "DGGYO", "DGNMO", "DIRIT", "DITAS", "DMSAS", "DNISI", "DOAS", "DOCO", "DOGUB", "DOHOL", "DOKTA", "DURDO", "DYOBY", "DZGYO", "EBEBK", "ECILC", "ECZYT", "EDATA", "EDIP", "EGEEN", "EGEPO", "EGGUB", "EGPRO", "EGSER", "EKGYO", "EKIZ", "EKSUN", "ELITE", "EMKEL", "ENERY", "ENJSA", "ENKAI", "ENTRA", "ERBOS", "ERCB", "EREGL", "ERSU", "ESCOM", "ESEN", "ETILR", "EUPWR", "EUREN", "EUHOL", "EUYO", "EYGYO", "FADE", "FENER", "FLAP", "FMIZP", "FONET", "FORMT", "FORTE", "FRIGO", "FROTO", "FZLGY", "GARFA", "GEDIK", "GEDZA", "GENIL", "GENTS", "GEREL", "GESAN", "GIPTA", "GLBMD", "GLCVY", "GLRYH", "GLYHO", "GMTAS", "GOKNR", "GOLTS", "GOODY", "GOZDE", "GRNYO", "GRSEL", "GSDDE", "GSDHO", "GSRAY", "GUBRF", "GWIND", "GZNMI", "HALKB", "HATEK", "HDFGS", "HEDEF", "HEKTS", "HKTM", "HLGYO", "HTTBT", "HUBVC", "HUNER", "HURGZ", "ICBCT", "IDGYO", "IEYHO", "IHEVA", "IHGZT", "IHLAS", "IHLGM", "IHYAY", "IMASM", "INDES", "INFO", "INGRM", "INTEM", "IPEKE", "ISATR", "ISBTR", "ISCTR", "ISFIN", "ISGSY", "ISGYO", "ISMEN", "ISSEN", "ISYAT", "IZENR", "IZFAS", "IZMDC", "JANTS", "KAPLM", "KAREL", "KARSN", "KARTN", "KARYE", "KATMR", "KAYSE", "KCAER", "KCHOL", "KFEIN", "KGYO", "KIMMR", "KLGYO", "KLMSN", "KLNMA", "KLRMP", "KLSYN", "KLYAS", "KMEPU", "KNFRT", "KOCAER", "KOCMT", "KONKA", "KONTR", "KONYA", "KORDS", "KOTON", "KOZAA", "KOZAL", "KPOWR", "KRGYO", "KRONT", "KRPLS", "KRSTL", "KRTEK", "KSTUR", "KTSKR", "KUTPO", "KUVVA", "KUYAS", "KZBGY", "KZGYO", "LIDER", "LIDFA", "LINK", "LMKDC", "LOGO", "LRSHO", "LUKSK", "MAALT", "MAGEN", "MAKIM", "MAKTK", "MANAS", "MARKA", "MARTI", "MAVI", "MEDTR", "MEGAP", "MEGMT", "MEPET", "MERCN", "MERIT", "MERKO", "METRO", "METUR", "MHRGY", "MIATK", "MIPAZ", "MMCAS", "MNDRS", "MNDTR", "MOBTL", "MPARK", "MRGYO", "MRSHL", "MSGYO", "MTRKS", "MTRYO", "MZHLD", "NATEN", "NETAS", "NIBAS", "NTGAZ", "NUGYO", "NUHCM", "OBAMS", "OBASE", "ODAS", "ONCSM", "ORCAY", "ORGE", "OTKAR", "OYAKC", "OYAYO", "OYLUM", "OYYAT", "OZGYO", "OZKGY", "OZRDN", "OZSUB", "PAGYO", "PAMEL", "PAPIL", "PARSN", "PASEU", "PATEK", "PCILT", "PEGYO", "PEKGY", "PENTA", "PETKM", "PETUN", "PGSUS", "PINSU", "PKART", "PKENT", "PLTUR", "PNLSN", "PNSUT", "POLHO", "POLTK", "PRKAB", "PRKME", "PRZMA", "PSDTC", "PSGYO", "QUAGR", "RALYH", "RAYSG", "REEDR", "RNPOL", "RODRG", "RTALB", "RUBNS", "RYGYO", "RYSAS", "SAFKR", "SAHOL", "SAMAT", "SANEL", "SANFO", "SANKO", "SARKY", "SARTN", "SASA", "SAYAS", "SDTTR", "SEGYO", "SEKFK", "SEKUR", "SELGD", "SELVA", "SEYKM", "SILVR", "SISE", "SKBNK", "SKTAS", "SMART", "SMRTG", "SNGYO", "SNICA", "SNKPA", "SOKM", "SONME", "SRVGY", "SUMAS", "SUNTK", "SURGY", "TABGD", "TARKM", "TATEN", "TATGD", "TAVHL", "TBORG", "TCELL", "TDGYO", "TEKTU", "TERA", "TETMT", "TEZOL", "TGSAS", "THYAO", "TKFEN", "TKNSA", "TLMAN", "TMPOL", "TMSN", "TOASO", "TRCAS", "TRGYO", "TRILC", "TSKB", "TSPOR", "TTKOM", "TTRAK", "TUCLK", "TUKAS", "TUPRS", "TUREX", "TURSG", "UFUK", "ULAS", "ULKER", "ULLY", "ULUFA", "ULUSE", "ULUUN", "UMPAS", "UNMAŞ", "USAK", "VAKBN", "VAKFN", "VAKKO", "VANGD", "VBTYZ", "VERTU", "VERUS", "VESBE", "VESTL", "VKGYO", "VKING", "YAPRK", "YATAS", "YAYLA", "YEOTK", "YESIL", "YGGYO", "YGYO", "YKBNK", "YKSLN", "YONGA", "YOTAS", "YUNSA", "YYLGD", "ZEDUR", "ZOREN", "ZRGYO"
        ]))) 

def veri_cek(periyot, hisse_listesi):
    sonuclar = []
    limit = 100
    paketler = [hisse_listesi[i:i + limit] for i in range(0, len(hisse_listesi), limit)]
    
    ilerleme_cubugu = st.progress(0)
    durum_metni = st.empty()
    
    toplam_paket = len(paketler)
    
    for idx, paket in enumerate(paketler):
        tv_hisseler = [f"BIST:{h}" for h in paket]
        try:
            analizler = get_multiple_analysis(screener="turkey", interval=periyot, symbols=tv_hisseler)
            if analizler:
                for symbol, analiz in analizler.items():
                    if analiz is None: continue
                    ind = analiz.indicators
                    
                    sonuclar.append({
                        "Hisse": symbol.split(":")[1],
                        "Fiyat": round(ind.get("close", 0) or 0, 2),
                        "Değişim %": round(ind.get("change", 0) or 0, 2),
                        "RSI": round(ind.get("RSI", 0) or 0, 2)
                    })
            time.sleep(0.4)
            ilerleme_cubugu.progress((idx + 1) / toplam_paket)
            durum_metni.text(f"Paket {idx+1}/{toplam_paket} işleniyor...")
        except Exception as e:
            st.error(f"Hata oluştu: {e}")
            continue
            
    return pd.DataFrame(sonuclar)

# --- UI TASARIMI ---
st.title("🚀 BIST RSI Tarayıcı")

col1, col2, col3 = st.columns(3)

with col1:
    evren = st.selectbox("Hisse Grubu", ["BIST 30", "BIST TÜM"])
with col2:
    periyot_str = st.selectbox("Periyot", ["1 Saat", "4 Saat", "1 Gün", "1 Hafta", "1 Ay"])
    p_map = {
        "1 Saat": Interval.INTERVAL_1_HOUR,
        "4 Saat": Interval.INTERVAL_4_HOURS,
        "1 Gün": Interval.INTERVAL_1_DAY,
        "1 Hafta": Interval.INTERVAL_1_WEEK,
        "1 Ay": Interval.INTERVAL_1_MONTH
    }
with col3:
    rsi_filtre = st.checkbox("Sadece RSI < 35 olanları göster")

if st.button("Analizi Başlat"):
    liste = BIST30 if evren == "BIST 30" else BIST_TUM
    df = veri_cek(p_map[periyot_str], liste)
    
    if not df.empty:
        # Filtreleme
        if rsi_filtre:
            df = df[df["RSI"] < 35]
            
        # Renklendirme Fonksiyonu
        def renklendir(val):
            if isinstance(val, float):
                if val < 30: return 'background-color: #c8e6c9' # Yeşil (Aşırı Satım)
                if val > 70: return 'background-color: #ffcdd2' # Kırmızı (Aşırı Alım)
            return ''

        # Tabloyu Göster
        st.subheader(f"Tarama Sonuçları ({len(df)} Hisse)")
        st.dataframe(
            df.style.applymap(renklendir, subset=['RSI']),
            use_container_width=True,
            height=600
        )
    else:
        st.warning("Veri çekilemedi.")
