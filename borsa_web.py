import streamlit as st
import pandas as pd
import time
from tradingview_ta import get_multiple_analysis, Interval

# --- SAYFA KONFİGÜRASYONU ---
st.set_page_config(page_title="BIST Analiz v2.5", layout="wide")

# Liste PyQt6 kodundaki ile aynıdır
BIST_30 = ["AKBNK", "ALARK", "ARCLK", "ASELS", "ASTOR", "BIMAS", "EKGYO", "ENKAI", "EREGL", "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KOZAA", "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TAVHL", "TCELL", "THYAO", "TOASO", "TUPRS"]
BIST_TUM = sorted(list(set(BIST_30 + ["A1CAP", "ACSEL", "ADEL", "ADESE", "AEFES", "AFYON", "AGHOL", "AGROT", "AHGAZ", "AKCNS", "AKENR", "AKFGY", "AKSA", "AKSEN", "ALBRK", "ALFAS", "ALKA", "ALKIM", "ALVES", "ANELE", "ANGEN", "ANHYT", "ANSGR", "ARDYZ", "ARENA", "ARSAN", "ASGYO", "ASUZU", "ATATP", "AYDEM", "AYGAZ", "BAGFS", "BANVT", "BARMA", "BERA", "BEYAZ", "BFREN", "BIENP", "BIGCH", "BJKAS", "BLCYT", "BOBET", "BORLS", "BRISA", "BRYAT", "BSOKE", "BTCIM", "BUCIM", "CANTE", "CATES", "CCOLA", "CIMSA", "CLEBI", "CONSE", "CVKMD", "CWENE", "DOAS", "DOHOL", "EBEBK", "ECILC", "ECZYT", "EGEEN", "EGGUB", "EGPRO", "ENJSA", "EUPWR", "EUREN", "FENER", "GARFA", "GEDIK", "GENIL", "GESAN", "GLYHO", "GOODY", "GOZDE", "GSRAY", "GWIND", "HALKB", "HLGYO", "HTTBT", "HUNER", "IHEVA", "IHLAS", "IMASM", "INDES", "INFO", "IPEKE", "ISFIN", "ISGYO", "ISMEN", "IZENR", "KAREL", "KARSN", "KAYSE", "KCAER", "KFEIN", "KLGYO", "KLRMP", "KLSYN", "KOCAER", "KONYA", "KORDS", "KRYPT", "KUTPO", "KUYAS", "KZBGY", "LIDER", "LOGO", "MAVI", "MEGMT", "MIATK", "MPARK", "MSGYO", "MTRKS", "NATEN", "NETAS", "NTGAZ", "NUHCM", "ONCSM", "ORGE", "OTKAR", "OZKGY", "PAGYO", "PASEU", "PATEK", "PENTA", "PNLSN", "POLHO", "QUAGR", "REEDR", "RYGYO", "RYSAS", "SAYAS", "SDTTR", "SKBNK", "SMART", "SMRTG", "SNGYO", "SOKM", "TABGD", "TARKM", "TATEN", "TKFEN", "TKNSA", "TMSN", "TRGYO", "TSKB", "TTKOM", "TTRAK", "TUKAS", "TURSG", "ULKER", "ULUUN", "VAKBN", "VESBE", "VESTL", "YEOTK", "YKBNK", "YYLGD", "ZOREN"])))

# --- İSTEK MANTIĞI (PYQT6 İLE AYNI) ---

def run_normal_scan(liste, periyot):
    sonuclar = []
    limit = 100 # PyQt6'daki paket limiti
    paketler = [liste[i:i + limit] for i in range(0, len(liste), limit)]
    
    p_bar = st.progress(0)
    for idx, paket in enumerate(paketler):
        tv_hisseler = [f"BIST:{h}" for h in paket]
        try:
            # get_multiple_analysis kullanımı PyQt6 VeriCekici sınıfı ile aynı
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
            time.sleep(0.4) # PyQt6'daki bekleme süresi
        except: continue
        p_bar.progress((idx + 1) / len(paketler))
    return pd.DataFrame(sonuclar)

def run_altin_scan(liste):
    sonuclar = []
    limit = 100 # PyQt6'daki paket limiti
    paketler = [liste[i:i + limit] for i in range(0, len(liste), limit)]
    
    p_bar = st.progress(0)
    for idx, paket in enumerate(paketler):
        tv_hisseler = [f"BIST:{h}" for h in paket]
        try:
            # 3 Farklı periyotta analiz - PyQt6 AltinVurusWorker ile aynı
            a1s = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_1_HOUR, symbols=tv_hisseler)
            a4s = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_4_HOURS, symbols=tv_hisseler)
            a1g = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_1_DAY, symbols=tv_hisseler)

            for s in tv_hisseler:
                try:
                    a1, a4, ag = a1s.get(s), a4s.get(s), a1g.get(s)
                    if not (a1 and a4 and ag): continue
                    
                    r1, r4, rg = a1.indicators.get("RSI", 100), a4.indicators.get("RSI", 100), ag.indicators.get("RSI", 100)
                    fiyat = a1.indicators.get("close", 0)

                    # Kriter: 3 periyotta da RSI < 40 (Kodundaki gibi)
                    if r1 < 40 and r4 < 40 and rg < 40:
                        sonuclar.append({
                            "Hisse": s.split(":")[1],
                            "Fiyat": round(fiyat, 2),
                            "RSI (1S)": round(r1, 2),
                            "RSI (4S)": round(r4, 2),
                            "RSI (1G)": round(rg, 2)
                        })
                except: continue
            time.sleep(0.5) # PyQt6'daki bekleme süresi
        except: continue
        p_bar.progress((idx + 1) / len(paketler))
    return pd.DataFrame(sonuclar)

# --- ARAYÜZ ---

st.title("🎯 BIST Analiz - Altın Vuruş (PyQt6 Engine)")

# Kontrol Paneli
col1, col2, col3, col4 = st.columns([2,2,2,2])

with col1:
    e_sel = st.selectbox("Evren", ["BIST 30", "BIST TÜM"])
with col2:
    p_sel_text = st.selectbox("Periyot", ["1 Saat", "4 Saat", "1 Gün", "1 Hafta", "1 Ay"])
    p_map = {"1 Saat": Interval.INTERVAL_1_HOUR, "4 Saat": Interval.INTERVAL_4_HOURS, "1 Gün": Interval.INTERVAL_1_DAY, "1 Hafta": Interval.INTERVAL_1_WEEK, "1 Ay": Interval.INTERVAL_1_MONTH}
with col3:
    st.write(" ")
    btn_run = st.button("🚀 Analizi Başlat", use_container_width=True)
with col4:
    st.write(" ")
    btn_altin = st.button("🎯 ALTIN VURUŞ", use_container_width=True)

st.divider()

# Arama ve Hızlı Filtre (Sadece sonuç varsa çalışır)
search_col, filter_col = st.columns([2,1])
with search_col:
    search_query = st.text_input("🔍 Hisse Ara...", "").upper()
with filter_col:
    rsi_filter = st.checkbox("📉 RSI < 35 Filtrele")

# --- TETİKLEYİCİLER ---

target_list = BIST_30 if e_sel == "BIST 30" else BIST_TUM

if btn_run:
    st.session_state['res'] = run_normal_scan(target_list, p_map[p_sel_text])
    st.session_state['mode'] = "normal"

if btn_altin:
    st.session_state['res'] = run_altin_scan(BIST_TUM)
    st.session_state['mode'] = "altin"

# --- SONUÇLARI GÖSTER (STYLING) ---

if 'res' in st.session_state:
    df = st.session_state['res'].copy()
    
    # Filtreleme mantığı (PyQt6 run_all_filters ile aynı)
    if rsi_filter:
        col_name = "RSI" if st.session_state['mode'] == "normal" else "RSI (1S)"
        df = df[df[col_name] < 35]
    
    if search_query:
        df = df[df['Hisse'].str.contains(search_query)]

    # Renklendirme mantığı (PyQt6 add_row ile aynı)
    def apply_style(x):
        style_df = pd.DataFrame('', index=x.index, columns=x.columns)
        
        if st.session_state['mode'] == "normal":
            # Değişim rengi
            style_df['Değişim %'] = x['Değişim %'].apply(lambda v: 'color: #2e7d32' if v > 0 else ('color: #c62828' if v < 0 else ''))
            # RSI Arkaplanı
            style_df['RSI'] = x['RSI'].apply(lambda v: 'background-color: #c8e6c9' if v < 30 else ('background-color: #ffcdd2' if v > 70 else ''))
        else:
            # Altın Vuruş Stili
            style_df['Hisse'] = 'background-color: #ffd700; color: black; font-weight: bold'
            for c in ["RSI (1S)", "RSI (4S)", "RSI (1G)"]:
                style_df[c] = 'background-color: #fff9c4; color: black'
        
        return style_df

    st.dataframe(df.style.apply(apply_style, axis=None), use_container_width=True, height=600)
    st.success(f"İşlem Tamamlandı: {len(df)} hisse bulundu.")
