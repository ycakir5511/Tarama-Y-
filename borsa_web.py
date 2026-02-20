import streamlit as st
import pandas as pd
from tradingview_ta import get_multiple_analysis, Interval
import time

# Sayfa Yapılandırması
st.set_page_config(page_title="BIST Stratejik Terminal", layout="wide")

# --- Hisse Listeleri ---
bist30 = ["AKBNK", "ALARK", "ARCLK", "ASELS", "ASTOR", "BIMAS", "EKGYO", "ENKAI", "EREGL", "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KOZAA", "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TAVHL", "TCELL", "THYAO", "TOASO", "TUPRS"]

bist100 = sorted(list(set(bist30 + [
    "AEFES", "AGHOL", "AHGAZ", "AKCNS", "AKFGY", "AKFYE", "AKSA", "AKSEN", "ALBRK", "ALFAS", "ASUZU", "AYDEM", "BAGFS", "BERA", "BRYAT", "BUCIM", "CANTE", "CCOLA", "CIMSA", "CWENE", "DOAS", "DOHOL", "EGEEN", "EUREN", "GENIL", "GESAN", "GLYHO", "GSDHO", "HALKB", "IPEKE", "ISGYO", "ISMEN", "IZMDC", "KARDMD", "KAYSE", "KCAER", "KLRMP", "KOCAER", "KORDS", "MAVI", "MGROS", "MIATK", "NETAS", "NTGAZ", "OTKAR", "PENTA", "QUAGR", "REEDR", "SAYAS", "SDTTR", "SMRTG", "SOKM", "TABGD", "TARKM", "TATEN", "TKFEN", "TKNSA", "TMSN", "TSKB", "TTKOM", "TTRAK", "TURSG", "ULKER", "VAKBN", "VESBE", "VESTL", "YEOTK", "YYKDR", "ZOREN"
])))

# BIST TÜM (Genişletilmiş Liste)
bist_tum = sorted(list(set(bist100 + [
    "ADEL", "ADESE", "AFYON", "AGESA", "AGROT", "AKENR", "AKGRT", "AKMGY", "ALCTL", "ALKA", "ALKIM", "ALMAD", "ALTNY", "ALVES", "ANGEN", "ANSGR", "ARASE", "ARDYZ", "ARENA", "ARSAN", "ARZUM", "ASGYO", "ATAGY", "ATEKS", "ATLAS", "AVHOL", "AVOD", "AVTUR", "AYCES", "AYGAZ", "AZTEK", "BAKAB", "BANVT", "BARMA", "BATIS", "BAYSZ", "BIENP", "BIGCH", "BIZIM", "BMSCH", "BMSTL", "BNASL", "BOBET", "BORLS", "BORSK", "BRISA", "BRKO", "BRSAN", "BSOKE", "BTCIM", "BURCE", "BURVA", "BVSAN", "BYDNR", "CASA", "CECAN", "CELHA", "CEMAS", "CEMTS", "CEOEM", "CLEBI", "CONSE", "COSMO", "CRDFA", "CUSAN", "CVKMD", "DAGHL", "DAGI", "DAPGM", "DARDL", "DENGE", "DERHL", "DERIM", "DESA", "DESPC", "DGNMO", "DIRIT", "DITAS", "DMSAS", "DNISI", "DOBUR", "DOCO", "DOGUB", "DOKTA", "DURDO", "DYOBY", "EBEBK", "ECILC", "ECZYT", "EDATA", "EDIP", "EGEPO", "EGGUB", "EGSER", "EKIZ", "EMKEL", "ENERY", "ENTRA", "ERCB", "ERSU", "ESCOM", "ESEN", "ETILR", "EUPWR", "EYGYO", "FADE", "FENER", "FLAP", "FONET", "FORMT", "FRIGO", "FZLGY", "GARFA", "GEDIK", "GEDZA", "GENTS", "GEREL", "GIPTA", "GLBMD", "GLRYH", "GMTAS", "GOKNR", "GOODY", "GOZDE", "GRSEL", "GSDDE", "GSRAY", "GWIND", "GZNMI", "HATEK", "HATSN", "HEDEF", "HOROZ", "HRKET", "HUBVC", "HUNER", "ICBCT", "IDEAS", "IDGYO", "IHEVA", "IHLAS", "IHLGM", "IHYAY", "IMASM", "INDES", "INFO", "INGRM", "INTEM", "INVEO", "INVES", "ISKPL", "ISSEN", "ISYAT", "ITTFH", "IZFAS", "IZINV", "JANTS", "KAPLM", "KAREL", "KARSN", "KARTN", "KARYE", "KATMR", "KBCER", "KIMMR", "KIRVL", "KLGYO", "KLMSN", "KLNMA", "KLSYN", "KLYN", "KMEPU", "KNFRT", "KONKA", "KONYA", "KRGYO", "KRONT", "KRSTL", "KRVGD", "KSTUR", "KUTPO", "KUVVA", "LIDER", "LIDFA", "LINK", "LMKDC", "LOGO", "LKMNH", "LUKSK", "MAKTK", "MANAS", "MARKA", "MARTI", "MEDTR", "MEGAP", "MEPET", "MERCN", "MERKO", "METUR", "MHRGY", "MIPAZ", "MMCAS", "MNDRS", "MNDTR", "MOBTL", "MOGAN", "MPARK", "MRGYO", "MRSHL", "MSGYO", "MTRKS", "MTRYO", "MZHLD", "NATEN", "NIBAS", "NUHCM", "OBAMS", "OBASE", "OFSYM", "ONCSM", "ORCAY", "ORGE", "OSMEN", "OSTIM", "OYAYO", "OYLUM", "OZGYO", "OZKGY", "OZRDN", "OZSUB", "PAGYO", "PAMEL", "PAPIL", "PARSN", "PASEU", "PATEK", "PCILT", "PEGYO", "PEKGY", "PENGD", "PINSU", "PKART", "PKENT", "PNLSN", "PNSUT", "POLHO", "POLTK", "PRKAB", "PRKME", "PRZMA", "PSGYO", "RALYH", "RAYSG", "RNPOL", "RODRG", "RTALB", "RUBNS", "RYGYO", "RYSAS", "SAFKR", "SAMAT", "SANEL", "SANFO", "SANKO", "SARKY", "SEGYO", "SEKFK", "SEKUR", "SELEC", "SELGD", "SELVA", "SEYKM", "SILVR", "SKBNK", "SKYMD", "SKYLP", "SMCRT", "SNGYO", "SNICA", "SNKPA", "SONME", "SRVGY", "SUMAS", "SUNTK", "SURGY", "TABGD", "TAPDI", "TARKM", "TATGD", "TATEN", "TEKTU", "TERA", "TETMT", "TGSAS", "TLMAN", "TMPOL", "TMSN", "TRCAS", "TRGYO", "TRILC", "TSGYO", "TSPOR", "TUCLK", "TUREX", "TURGG", "UFUK", "ULAS", "ULUFA", "ULUSE", "UNLU", "USAK", "UTPYA", "VAKFN", "VAKKO", "VANGD", "VBTYZ", "VERTU", "VERUS", "VKFYO", "VKGYO", "YAPRK", "YATAS", "YAYLA", "YBTAS", "YESIL", "YGGYO", "YGYO", "YKSLN", "YONGA", "YUNSA", "ZEDUR", "ZRGV"
])))

# --- Sidebar ---
st.sidebar.header("⚙️ Ayarlar")
secilen_endeks = st.sidebar.selectbox("Endeks Seçimi", ["BIST 30", "BIST 100", "BIST TÜM"])
secilen_periyot = st.sidebar.selectbox("Periyot", ["1 Saat", "4 Saat", "1 Gün", "1 Hafta", "1 Ay"])

p_map = {
    "1 Saat": Interval.INTERVAL_1_HOUR, "4 Saat": Interval.INTERVAL_4_HOURS, 
    "1 Gün": Interval.INTERVAL_1_DAY, "1 Hafta": Interval.INTERVAL_1_WEEK, "1 Ay": Interval.INTERVAL_1_MONTH
}

# --- Main App ---
st.title("🚀 BIST Stratejik Tarama Web")
st.write(f"Şu anki seçim: **{secilen_endeks}** | Periyot: **{secilen_periyot}**")

if st.sidebar.button("📊 Taramayı Başlat"):
    # Seçime göre liste belirleme
    if secilen_endeks == "BIST 30": target_list = bist30
    elif secilen_endeks == "BIST 100": target_list = bist100
    else: target_list = bist_tum

    tv_hisseler = [f"BIST:{h}" for h in target_list]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    all_data = []

    # 100'erli paketleme (TradingView Limiti)
    limit = 100
    paketler = [tv_hisseler[i:i + limit] for i in range(0, len(tv_hisseler), limit)]
    
    start_time = time.time()

    for idx, paket in enumerate(paketler):
        status_text.text(f"📡 Veriler alınıyor: Paket {idx+1}/{len(paketler)}...")
        try:
            analizler = get_multiple_analysis(
                screener="turkey", 
                interval=p_map[secilen_periyot], 
                symbols=paket
            )
            
            if analizler:
                for symbol, analiz in analizler.items():
                    if analiz is None: continue
                    ind = analiz.indicators
                    fiyat = ind.get("close", 0)
                    rsi = ind.get("RSI", 0)
                    macd = ind.get("MACD.macd", 0)
                    signal = ind.get("MACD.signal", 0)
                    sma200 = ind.get("SMA200", 0)
                    
                    sinyal = "NÖTR"
                    if rsi < 35 and macd > signal: sinyal = "GÜÇLÜ AL 🔥"
                    elif rsi > 65 and macd < signal: sinyal = "GÜÇLÜ SAT ❄️"
                    elif fiyat > sma200: sinyal = "POZİTİF"

                    all_data.append({
                        "Hisse": symbol.split(":")[1],
                        "Fiyat": round(fiyat, 2),
                        "Değişim %": round(ind.get("change", 0), 2),
                        "RSI": round(rsi, 2),
                        "MACD": round(macd, 2),
                        "SMA 200 Durum": "ÜSTÜNDE" if fiyat > sma200 else "ALTINDA",
                        "STRATEJİ": sinyal
                    })
        except Exception as e:
            st.warning(f"Bir pakette hata oluştu, atlanıyor...")
            
        progress_bar.progress((idx + 1) / len(paketler))
        time.sleep(1.5) # Sunucuyu yormamak için mola

    df = pd.DataFrame(all_data)
    
    # Görsel İyileştirmeler
    def color_rows(val):
        if val == "GÜÇLÜ AL 🔥": return 'background-color: #d4edda; color: #155724; font-weight: bold;'
        if val == "GÜÇLÜ SAT ❄️": return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
        return ''

    st.success(f"✅ Tarama Bitti! Toplam {len(df)} hisse bulundu. (Süre: {int(time.time() - start_time)} sn)")
    
    # Arama Filtresi (Web Üzerinde)
    search_term = st.text_input("Tabloda Hisse Ara:", "")
    if search_term:
        df = df[df['Hisse'].str.contains(search_term.upper())]

    st.dataframe(df.style.applymap(color_rows, subset=['STRATEJİ']), use_container_width=True)

    # İndirme Butonu
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Sonuçları CSV Olarak İndir", csv, "Bist_Tarama.csv", "text/csv")

else:
    st.info("Tarama yapmak için sol taraftaki 'Taramayı Başlat' butonuna basın.")