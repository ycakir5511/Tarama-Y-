import streamlit as st
import pandas as pd
import time
from tradingview_ta import get_multiple_analysis, Interval

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="BIST Analiz - Altın Vuruş v2.0", layout="wide")

# CSS ile butonları ve tabloları daha şık hale getirelim
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .altin-button { background-color: #ffd700 !important; color: black !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

# --- VERİ SETLERİ ---
BIST_30 = ["AKBNK", "ALARK", "ARCLK", "ASELS", "ASTOR", "BIMAS", "EKGYO", "ENKAI", "EREGL", "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KOZAA", "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TAVHL", "TCELL", "THYAO", "TOASO", "TUPRS"]
BIST_TUM = sorted(list(set(BIST_30 + ["A1CAP", "ACSEL", "ADEL", "ADESE", "AEFES", "AFYON", "AGHOL", "AGROT", "AHGAZ", "AKCNS", "AKENR", "AKFGY", "AKSA", "AKSEN", "ALBRK", "ALFAS", "ALKA", "ALKIM", "ALVES", "ANELE", "ANGEN", "ANHYT", "ANSGR", "ARCLK", "ARDYZ", "ARENA", "ARSAN", "ASGYO", "ASUZU", "ATATP", "AYDEM", "AYGAZ", "BAGFS", "BANVT", "BARMA", "BERA", "BEYAZ", "BFREN", "BIENP", "BIGCH", "BJKAS", "BLCYT", "BOBET", "BORLS", "BRISA", "BRYAT", "BSOKE", "BTCIM", "BUCIM", "CANTE", "CATES", "CCOLA", "CIMSA", "CLEBI", "CONSE", "CVKMD", "CWENE", "DOAS", "DOHOL", "EBEBK", "ECILC", "ECZYT", "EGEEN", "EGGUB", "EGPRO", "EKGYO", "ENJSA", "ENKAI", "EREGL", "EUPWR", "EUREN", "FENER", "FROTO", "GARFA", "GEDIK", "GENIL", "GESAN", "GLYHO", "GOODY", "GOZDE", "GSRAY", "GUBRF", "GWIND", "HALKB", "HEKTS", "HLGYO", "HTTBT", "HUNER", "IHEVA", "IHLAS", "IMASM", "INDES", "INFO", "IPEKE", "ISCTR", "ISFIN", "ISGYO", "ISMEN", "IZENR", "KAREL", "KARSN", "KAYSE", "KCAER", "KCHOL", "KFEIN", "KLGYO", "KLRMP", "KLSYN", "KOCAER", "KONTR", "KONYA", "KORDS", "KOZAA", "KOZAL", "KRYPT", "KUTPO", "KUYAS", "KZBGY", "LIDER", "LOGO", "MAVI", "MEGMT", "MIATK", "MPARK", "MSGYO", "MTRKS", "NATEN", "NETAS", "NTGAZ", "NUHCM", "ODAS", "ONCSM", "ORGE", "OTKAR", "OYAKC", "OZKGY", "PAGYO", "PASEU", "PATEK", "PENTA", "PETKM", "PGSUS", "PNLSN", "POLHO", "QUAGR", "REEDR", "RYGYO", "RYSAS", "SAHOL", "SASA", "SAYAS", "SDTTR", "SISE", "SKBNK", "SMART", "SMRTG", "SNGYO", "SOKM", "TABGD", "TARKM", "TATEN", "TAVHL", "TCELL", "THYAO", "TKFEN", "TKNSA", "TMSN", "TOASO", "TRGYO", "TSKB", "TTKOM", "TTRAK", "TUKAS", "TUPRS", "TURSG", "ULKER", "ULUUN", "VAKBN", "VESBE", "VESTL", "YEOTK", "YKBNK", "YYLGD", "ZOREN"])))

# --- ANALİZ FONKSİYONLARI ---
def fetch_normal_data(hisse_listesi, periyot):
    sonuclar = []
    limit = 100
    paketler = [hisse_listesi[i:i + limit] for i in range(0, len(hisse_listesi), limit)]
    
    p_bar = st.progress(0)
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
                        "RSI": round(ind.get("RSI", 100), 2)
                    })
            time.sleep(0.4)
        except: continue
        p_bar.progress((idx + 1) / len(paketler))
    return pd.DataFrame(sonuclar)

def fetch_altin_vurus(hisse_listesi):
    sonuclar = []
    limit = 100
    paketler = [hisse_listesi[i:i + limit] for i in range(0, len(hisse_listesi), limit)]
    
    p_bar = st.progress(0)
    for idx, paket in enumerate(paketler):
        tv_hisseler = [f"BIST:{h}" for h in paket]
        try:
            a1s = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_1_HOUR, symbols=tv_hisseler)
            a4s = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_4_HOURS, symbols=tv_hisseler)
            a1g = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_1_DAY, symbols=tv_hisseler)

            for s in tv_hisseler:
                try:
                    if a1s[s] and a4s[s] and a1g[s]:
                        r1 = a1s[s].indicators.get("RSI", 100)
                        r4 = a4s[s].indicators.get("RSI", 100)
                        rg = a1g[s].indicators.get("RSI", 100)
                        
                        if r1 < 40 and r4 < 40 and rg < 40:
                            sonuclar.append({
                                "Hisse": s.split(":")[1],
                                "Fiyat": round(a1s[s].indicators.get("close", 0), 2),
                                "RSI (1S)": round(r1, 2),
                                "RSI (4S)": round(r4, 2),
                                "RSI (1G)": round(rg, 2)
                            })
                except: continue
            time.sleep(0.5)
        except: continue
        p_bar.progress((idx + 1) / len(paketler))
    return pd.DataFrame(sonuclar)

# --- ARAYÜZ TASARIMI ---
st.title("🎯 BIST Analiz - Altın Vuruş v2.0")

# Üst Kontrol Paneli
with st.container():
    c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
    with c1:
        evren = st.selectbox("Hisse Grubu", ["BIST 30", "BIST TÜM"])
    with c2:
        periyot_str = st.selectbox("Periyot", ["1 Saat", "4 Saat", "1 Gün", "1 Hafta", "1 Ay"])
        p_map = {
            "1 Saat": Interval.INTERVAL_1_HOUR, "4 Saat": Interval.INTERVAL_4_HOURS,
            "1 Gün": Interval.INTERVAL_1_DAY, "1 Hafta": Interval.INTERVAL_1_WEEK, "1 Ay": Interval.INTERVAL_1_MONTH
        }
    with c3:
        st.write(" ") # Hizalama için
        btn_normal = st.button("🚀 Analizi Başlat")
    with c4:
        st.write(" ") # Hizalama için
        btn_altin = st.button("🎯 ALTIN VURUŞ", help="3 periyotta da RSI < 40 olanları bulur.")

st.divider()

# Filtreleme Paneli
f1, f2 = st.columns([3, 5])
with f1:
    rsi_filtre = st.toggle("📉 Sadece RSI < 35 olanları göster", value=False)
with f2:
    search_query = st.text_input("🔍 Hisse Ara...", "").upper()

# --- VERİ İŞLEME VE GÖSTERİM ---
hisseler = BIST_30 if evren == "BIST 30" else BIST_TUM

if btn_normal:
    with st.spinner('Normal tarama yapılıyor...'):
        df = fetch_normal_data(hisseler, p_map[periyot_str])
        st.session_state['data'] = df
        st.session_state['mode'] = 'normal'

if btn_altin:
    with st.spinner('Altın Vuruş taraması yapılıyor (3 periyot kontrolü)...'):
        df = fetch_altin_vurus(hisseler)
        st.session_state['data'] = df
        st.session_state['mode'] = 'altin'

# Sonuçları Göster
if 'data' in st.session_state:
    df_display = st.session_state['data'].copy()

    # Filtre 1: RSI 35 Altı
    if rsi_filtre:
        if st.session_state['mode'] == 'normal':
            df_display = df_display[df_display['RSI'] < 35]
        else:
            # Altın vuruşta zaten hepsi < 40, 35 altına daha sıkı filtre uygularız
            df_display = df_display[(df_display['RSI (1S)'] < 35) & (df_display['RSI (4S)'] < 35)]

    # Filtre 2: Arama
    if search_query:
        df_display = df_display[df_display['Hisse'].str.contains(search_query)]

    st.subheader(f"📊 Bulunan Hisse Sayısı: {len(df_display)}")

    # Renklendirme ve Stil
    def highlight_cells(x):
        color_df = pd.DataFrame('', index=x.index, columns=x.columns)
        
        # RSI Renklendirme (Normal Mod)
        if 'RSI' in x.columns:
            mask = x['RSI'] < 35
            color_df.loc[mask, 'RSI'] = 'background-color: #c8e6c9; color: black'
            mask_high = x['RSI'] > 70
            color_df.loc[mask_high, 'RSI'] = 'background-color: #ffcdd2; color: black'
            
        # Değişim Renklendirme
        if 'Değişim %' in x.columns:
            color_df['Değişim %'] = x['Değişim %'].apply(lambda v: 'color: green' if v > 0 else ('color: red' if v < 0 else ''))

        # Altın Vuruş Özel Stil
        if st.session_state['mode'] == 'altin':
            color_df['Hisse'] = 'background-color: #ffd700; color: black; font-weight: bold'
            
        return color_df

    st.dataframe(df_display.style.apply(highlight_cells, axis=None), use_container_width=True, height=600)

else:
    st.info("Analizi başlatmak için yukarıdaki butonları kullanın.")

st.divider()
st.caption("Veriler TradingView üzerinden çekilmektedir. Yatırım tavsiyesi değildir.")
