import streamlit as st
import pandas as pd
import time
from tradingview_ta import get_multiple_analysis, Interval

# Sayfa Ayarları
st.set_page_config(page_title="BIST Analiz - Altın Vuruş v2.0", layout="wide")

# --- Veri Sabitleri ---
BIST_30 = ["AKBNK", "ALARK", "ARCLK", "ASELS", "ASTOR", "BIMAS", "EKGYO", "ENKAI", "EREGL", "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KOZAA", "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TAVHL", "TCELL", "THYAO", "TOASO", "TUPRS"]
BIST_TUM = sorted(list(set(BIST_30 + ["A1CAP", "ACSEL", "ADEL", "ADESE", "AEFES", "AFYON", "AGHOL", "AGROT", "AHGAZ", "AKCNS", "AKENR", "AKFGY", "AKSA", "AKSEN", "ALBRK", "ALFAS", "ALKA", "ALKIM", "ALVES", "ANELE", "ANGEN", "ANHYT", "ANSGR", "ARCLK", "ARDYZ", "ARENA", "ARSAN", "ASGYO", "ASUZU", "ATATP", "AYDEM", "AYGAZ", "BAGFS", "BANVT", "BARMA", "BERA", "BEYAZ", "BFREN", "BIENP", "BIGCH", "BJKAS", "BLCYT", "BOBET", "BORLS", "BRISA", "BRYAT", "BSOKE", "BTCIM", "BUCIM", "CANTE", "CATES", "CCOLA", "CIMSA", "CLEBI", "CONSE", "CVKMD", "CWENE", "DOAS", "DOHOL", "EBEBK", "ECILC", "ECZYT", "EGEEN", "EGGUB", "EGPRO", "EKGYO", "ENJSA", "ENKAI", "EREGL", "EUPWR", "EUREN", "FENER", "FROTO", "GARFA", "GEDIK", "GENIL", "GESAN", "GLYHO", "GOODY", "GOZDE", "GSRAY", "GUBRF", "GWIND", "HALKB", "HEKTS", "HLGYO", "HTTBT", "HUNER", "IHEVA", "IHLAS", "IMASM", "INDES", "INFO", "IPEKE", "ISCTR", "ISFIN", "ISGYO", "ISMEN", "IZENR", "KAREL", "KARSN", "KAYSE", "KCAER", "KCHOL", "KFEIN", "KLGYO", "KLRMP", "KLSYN", "KOCAER", "KONTR", "KONYA", "KORDS", "KOZAA", "KOZAL", "KRYPT", "KUTPO", "KUYAS", "KZBGY", "LIDER", "LOGO", "MAVI", "MEGMT", "MIATK", "MPARK", "MSGYO", "MTRKS", "NATEN", "NETAS", "NTGAZ", "NUHCM", "ODAS", "ONCSM", "ORGE", "OTKAR", "OYAKC", "OZKGY", "PAGYO", "PASEU", "PATEK", "PENTA", "PETKM", "PGSUS", "PNLSN", "POLHO", "QUAGR", "REEDR", "RYGYO", "RYSAS", "SAHOL", "SASA", "SAYAS", "SDTTR", "SISE", "SKBNK", "SMART", "SMRTG", "SNGYO", "SOKM", "TABGD", "TARKM", "TATEN", "TAVHL", "TCELL", "THYAO", "TKFEN", "TKNSA", "TMSN", "TOASO", "TRGYO", "TSKB", "TTKOM", "TTRAK", "TUKAS", "TUPRS", "TURSG", "ULKER", "ULUUN", "VAKBN", "VESBE", "VESTL", "YEOTK", "YKBNK", "YYLGD", "ZOREN"])))

# --- Fonksiyonlar ---
def fetch_normal_data(hisse_listesi, periyot):
    sonuclar = []
    limit = 100
    paketler = [hisse_listesi[i:i + limit] for i in range(0, len(hisse_listesi), limit)]
    
    progress_bar = st.progress(0)
    for idx, paket in enumerate(paketler):
        tv_hisseler = [f"BIST:{h}" for h in paket]
        try:
            analizler = get_multiple_analysis(screener="turkey", interval=periyot, symbols=tv_hisseler)
            for symbol, analiz in analizler.items():
                if analiz:
                    ind = analiz.indicators
                    sonuclar.append({
                        "Hisse": symbol.split(":")[1],
                        "Fiyat": round(ind.get("close", 0), 2),
                        "Değişim %": round(ind.get("change", 0), 2),
                        "RSI": round(ind.get("RSI", 0), 2)
                    })
            time.sleep(0.4)
        except: continue
        progress_bar.progress((idx + 1) / len(paketler))
    return pd.DataFrame(sonuclar)

def fetch_altin_vurus(hisse_listesi):
    sonuclar = []
    limit = 100
    paketler = [hisse_listesi[i:i + limit] for i in range(0, len(hisse_listesi), limit)]
    
    progress_bar = st.progress(0)
    for idx, paket in enumerate(paketler):
        tv_hisseler = [f"BIST:{h}" for h in paket]
        try:
            a1s = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_1_HOUR, symbols=tv_hisseler)
            a4s = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_4_HOURS, symbols=tv_hisseler)
            a1g = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_1_DAY, symbols=tv_hisseler)

            for s in tv_hisseler:
                try:
                    if a1s[s] and a4s[s] and a1g[s]:
                        r1, r4, rg = a1s[s].indicators["RSI"], a4s[s].indicators["RSI"], a1g[s].indicators["RSI"]
                        if r1 < 40 and r4 < 40 and rg < 40:
                            sonuclar.append({
                                "Hisse": s.split(":")[1],
                                "Fiyat": round(a1s[s].indicators["close"], 2),
                                "RSI (1S)": round(r1, 2),
                                "RSI (4S)": round(r4, 2),
                                "RSI (1G)": round(rg, 2)
                            })
                except: continue
            time.sleep(0.5)
        except: continue
        progress_bar.progress((idx + 1) / len(paketler))
    return pd.DataFrame(sonuclar)

# --- Arayüz ---
st.title("🎯 BIST Analiz - Altın Vuruş")

col1, col2, col3, col4 = st.columns([2, 2, 2, 3])

with col1:
    evren = st.selectbox("Hisse Grubu", ["BIST 30", "BIST TÜM"])
with col2:
    periyot_str = st.selectbox("Periyot", ["1 Saat", "4 Saat", "1 Gün", "1 Hafta", "1 Ay"])
    p_map = {
        "1 Saat": Interval.INTERVAL_1_HOUR, "4 Saat": Interval.INTERVAL_4_HOURS,
        "1 Gün": Interval.INTERVAL_1_DAY, "1 Hafta": Interval.INTERVAL_1_WEEK, "1 Ay": Interval.INTERVAL_1_MONTH
    }

with col3:
    st.write("") # Boşluk
    run_normal = st.button("🚀 Analizi Başlat", use_container_width=True)

with col4:
    st.write("") # Boşluk
    run_altin = st.button("🎯 ALTIN VURUŞ (3x RSI < 40)", use_container_width=True)

# Filtreleme Alanı
search_query = st.text_input("🔍 Hisse Ara...", "").upper()

# --- Mantık ---
hisseler = BIST_30 if evren == "BIST 30" else BIST_TUM

if run_normal:
    with st.spinner('Veriler çekiliyor...'):
        df = fetch_normal_data(hisseler, p_map[periyot_str])
        st.session_state['data'] = df
        st.session_state['mode'] = 'normal'

if run_altin:
    with st.spinner('3 periyot taranıyor (Bu biraz zaman alabilir)...'):
        df = fetch_altin_vurus(hisseler)
        st.session_state['data'] = df
        st.session_state['mode'] = 'altin'

# --- Tablo Gösterimi ---
if 'data' in st.session_state:
    df_final = st.session_state['data']
    
    # Arama filtresi
    if search_query:
        df_final = df_final[df_final['Hisse'].str.contains(search_query)]

    # Renklendirme Fonksiyonu
    def color_rsi(val):
        if isinstance(val, float):
            if val < 35: return 'background-color: #c8e6c9' # Yeşilimsi
            if val > 70: return 'background-color: #ffcdd2' # Kırmızımsı
        return ''

    # Tabloyu ekrana bas
    st.subheader(f"Sonuçlar ({len(df_final)} Hisse)")
    
    if st.session_state['mode'] == 'normal':
        st.dataframe(df_final.style.applymap(color_rsi, subset=['RSI']), use_container_width=True)
    else:
        # Altın vuruşta hisse sütununu sarı yapalım
        st.dataframe(df_final.style.applymap(lambda x: 'background-color: #ffd700; color: black; font-weight: bold', subset=['Hisse']), use_container_width=True)

st.divider()
st.caption("Veriler TradingView üzerinden anlık çekilmektedir. Yatırım tavsiyesi değildir.")
