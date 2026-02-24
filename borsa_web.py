```python
import sys
import time
import streamlit as st
import pandas as pd
from tradingview_ta import get_multiple_analysis, Interval

# --- Fonksiyonlar ---
def fetch_normal(periyot, hisse_listesi):
    data = []
    limit = 100 
    paketler = [hisse_listesi[i:i + limit] for i in range(0, len(hisse_listesi), limit)]
    
    for paket in paketler:
        tv_hisseler = [f"BIST:{h}" for h in paket]
        try:
            analizler = get_multiple_analysis(screener="turkey", interval=periyot, symbols=tv_hisseler)
            if analizler:
                for symbol, analiz in analizler.items():
                    if analiz is None: continue
                    ind = analiz.indicators
                    
                    fiyat = ind.get("close", 0) or 0
                    degisim = ind.get("change", 0) or 0
                    rsi = ind.get("RSI", 0) or 0

                    data.append({
                        "Hisse": symbol.split(":")[1],
                        "Fiyat": round(fiyat, 2),
                        "Değişim %": round(degisim, 2),
                        "RSI": round(rsi, 2)
                    })
            time.sleep(0.4) 
        except: continue
    return data

def fetch_altin(hisse_listesi):
    data = []
    limit = 100 
    paketler = [hisse_listesi[i:i + limit] for i in range(0, len(hisse_listesi), limit)]
    
    for paket in paketler:
        tv_hisseler = [f"BIST:{h}" for h in paket]
        try:
            # 3 farklı periyotta analiz al
            analiz_1s = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_1_HOUR, symbols=tv_hisseler)
            analiz_4s = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_4_HOURS, symbols=tv_hisseler)
            analiz_1g = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_1_DAY, symbols=tv_hisseler)

            for symbol in tv_hisseler:
                try:
                    a1 = analiz_1s.get(symbol)
                    a4 = analiz_4s.get(symbol)
                    ag = analiz_1g.get(symbol)

                    if not (a1 and a4 and ag): continue

                    rsi1 = a1.indicators.get("RSI", 100)
                    rsi4 = a4.indicators.get("RSI", 100)
                    rsig = ag.indicators.get("RSI", 100)
                    fiyat = a1.indicators.get("close", 0)

                    # KRİTER: 3 periyotta da RSI < 40
                    if rsi1 < 40 and rsi4 < 40 and rsig < 40:
                        data.append({
                            "Hisse": symbol.split(":")[1],
                            "Fiyat": round(fiyat, 2),
                            "RSI (1S)": round(rsi1, 2),
                            "RSI (4S)": round(rsi4, 2),
                            "RSI (1G)": round(rsig, 2)
                        })
                except: continue
            
            time.sleep(0.5) # API limitlerine takılmamak için
        except: continue
    return data

# --- Stil Fonksiyonları ---
def style_normal(df):
    def apply_style(row):
        styles = [''] * len(row)
        if row['Değişim %'] > 0:
            styles[2] = 'color: #2e7d32'
        elif row['Değişim %'] < 0:
            styles[2] = 'color: #c62828'
        if row['RSI'] < 30:
            styles[3] = 'background-color: #c8e6c9'
        elif row['RSI'] > 70:
            styles[3] = 'background-color: #ffcdd2'
        return styles
    return df.style.apply(apply_style, axis=1)

def style_altin(df):
    def apply_style(row):
        styles = [''] * len(row)
        # Hisse: altın sarısı arka plan, kalın yazı
        styles[0] = 'background-color: #ffd700; font-weight: bold'
        # RSI sütunları: açık sarı arka plan, siyah yazı
        for i in range(2, 5):
            styles[i] = 'background-color: #fff9c4; color: #000000'
        return styles
    return df.style.apply(apply_style, axis=1)

# --- Streamlit Uygulaması ---
st.title("BIST Analiz - Altın Vuruş v2.0")

# Session state başlat
if 'data' not in st.session_state:
    st.session_state.data = None
    st.session_state.mode = None

# Sidebar kontrolleri
with st.sidebar:
    e_sel = st.selectbox("Endeks", ["BIST 30", "BIST TÜM"])
    p_sel = st.selectbox("Periyot", ["1 Saat", "4 Saat", "1 Gün", "1 Hafta", "1 Ay"])
    
    if st.button("🚀 Analizi Başlat"):
        with st.spinner("Tarama yapılıyor (Normal Mod)..."):
            p_map = {
                "1 Saat": Interval.INTERVAL_1_HOUR, 
                "4 Saat": Interval.INTERVAL_4_HOURS, 
                "1 Gün": Interval.INTERVAL_1_DAY,
                "1 Hafta": Interval.INTERVAL_1_WEEK,
                "1 Ay": Interval.INTERVAL_1_MONTH
            }
            bist30 = ["AKBNK", "ALARK", "ARCLK", "ASELS", "ASTOR", "BIMAS", "EKGYO", "ENKAI", "EREGL", "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KOZAA", "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TAVHL", "TCELL", "THYAO", "TOASO", "TUPRS"]
            bist_tum = sorted(list(set(bist30 + ["A1CAP", "ACSEL", "ADEL", "ADESE", "AEFES", "AFYON", "AGHOL", "AGROT", "AHGAZ", "AKCNS", "AKENR", "AKFGY", "AKSA", "AKSEN", "ALBRK", "ALFAS", "ALKA", "ALKIM", "ALVES", "ANELE", "ANGEN", "ANHYT", "ANSGR", "ARCLK", "ARDYZ", "ARENA", "ARSAN", "ASGYO", "ASUZU", "ATATP", "AYDEM", "AYGAZ", "BAGFS", "BANVT", "BARMA", "BERA", "BEYAZ", "BFREN", "BIENP", "BIGCH", "BJKAS", "BLCYT", "BOBET", "BORLS", "BRISA", "BRYAT", "BSOKE", "BTCIM", "BUCIM", "CANTE", "CATES", "CCOLA", "CIMSA", "CLEBI", "CONSE", "CVKMD", "CWENE", "DOAS", "DOHOL", "EBEBK", "ECILC", "ECZYT", "EGEEN", "EGGUB", "EGPRO", "EKGYO", "ENJSA", "ENKAI", "EREGL", "EUPWR", "EUREN", "FENER", "FROTO", "GARFA", "GEDIK", "GENIL", "GESAN", "GLYHO", "GOODY", "GOZDE", "GSRAY", "GUBRF", "GWIND", "HALKB", "HEKTS", "HLGYO", "HTTBT", "HUNER", "IHEVA", "IHLAS", "IMASM", "INDES", "INFO", "IPEKE", "ISCTR", "ISFIN", "ISGYO", "ISMEN", "IZENR", "KAREL", "KARSN", "KAYSE", "KCAER", "KCHOL", "KFEIN", "KLGYO", "KLRMP", "KLSYN", "KOCAER", "KONTR", "KONYA", "KORDS", "KOZAA", "KOZAL", "KRYPT", "KUTPO", "KUYAS", "KZBGY", "LIDER", "LOGO", "MAVI", "MEGMT", "MIATK", "MPARK", "MSGYO", "MTRKS", "NATEN", "NETAS", "NTGAZ", "NUHCM", "ODAS", "ONCSM", "ORGE", "OTKAR", "OYAKC", "OZKGY", "PAGYO", "PASEU", "PATEK", "PENTA", "PETKM", "PGSUS", "PNLSN", "POLHO", "QUAGR", "REEDR", "RYGYO", "RYSAS", "SAHOL", "SASA", "SAYAS", "SDTTR", "SISE", "SKBNK", "SMART", "SMRTG", "SNGYO", "SOKM", "TABGD", "TARKM", "TATEN", "TAVHL", "TCELL", "THYAO", "TKFEN", "TKNSA", "TMSN", "TOASO", "TRGYO", "TSKB", "TTKOM", "TTRAK", "TUKAS", "TUPRS", "TURSG", "ULKER", "ULUUN", "VAKBN", "VESBE", "VESTL", "YEOTK", "YKBNK", "YYLGD", "ZOREN"])))
            liste = bist30 if e_sel == "BIST 30" else bist_tum
            raw_data = fetch_normal(p_map[p_sel], liste)
            st.session_state.data = pd.DataFrame(raw_data)
            st.session_state.mode = "normal"
        st.success(f"İşlem Tamamlandı: {len(st.session_state.data)} hisse bulundu.")

    if st.button("🎯 ALTIN VURUŞ (3x RSI < 40)"):
        with st.spinner("Altın Vuruş Taraması: BIST TÜM için 3 periyot kontrol ediliyor..."):
            bist_tum = sorted(list(set(["AKBNK", "ALARK", "ARCLK", "ASELS", "ASTOR", "BIMAS", "EKGYO", "ENKAI", "EREGL", "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KOZAA", "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TAVHL", "TCELL", "THYAO", "TOASO", "TUPRS"] + ["A1CAP", "ACSEL", "ADEL", "ADESE", "AEFES", "AFYON", "AGHOL", "AGROT", "AHGAZ", "AKCNS", "AKENR", "AKFGY", "AKSA", "AKSEN", "ALBRK", "ALFAS", "ALKA", "ALKIM", "ALVES", "ANELE", "ANGEN", "ANHYT", "ANSGR", "ARCLK", "ARDYZ", "ARENA", "ARSAN", "ASGYO", "ASUZU", "ATATP", "AYDEM", "AYGAZ", "BAGFS", "BANVT", "BARMA", "BERA", "BEYAZ", "BFREN", "BIENP", "BIGCH", "BJKAS", "BLCYT", "BOBET", "BORLS", "BRISA", "BRYAT", "BSOKE", "BTCIM", "BUCIM", "CANTE", "CATES", "CCOLA", "CIMSA", "CLEBI", "CONSE", "CVKMD", "CWENE", "DOAS", "DOHOL", "EBEBK", "ECILC", "ECZYT", "EGEEN", "EGGUB", "EGPRO", "EKGYO", "ENJSA", "ENKAI", "EREGL", "EUPWR", "EUREN", "FENER", "FROTO", "GARFA", "GEDIK", "GENIL", "GESAN", "GLYHO", "GOODY", "GOZDE", "GSRAY", "GUBRF", "GWIND", "HALKB", "HEKTS", "HLGYO", "HTTBT", "HUNER", "IHEVA", "IHLAS", "IMASM", "INDES", "INFO", "IPEKE", "ISCTR", "ISFIN", "ISGYO", "ISMEN", "IZENR", "KAREL", "KARSN", "KAYSE", "KCAER", "KCHOL", "KFEIN", "KLGYO", "KLRMP", "KLSYN", "KOCAER", "KONTR", "KONYA", "KORDS", "KOZAA", "KOZAL", "KRYPT", "KUTPO", "KUYAS", "KZBGY", "LIDER", "LOGO", "MAVI", "MEGMT", "MIATK", "MPARK", "MSGYO", "MTRKS", "NATEN", "NETAS", "NTGAZ", "NUHCM", "ODAS", "ONCSM", "ORGE", "OTKAR", "OYAKC", "OZKGY", "PAGYO", "PASEU", "PATEK", "PENTA", "PETKM", "PGSUS", "PNLSN", "POLHO", "QUAGR", "REEDR", "RYGYO", "RYSAS", "SAHOL", "SASA", "SAYAS", "SDTTR", "SISE", "SKBNK", "SMART", "SMRTG", "SNGYO", "SOKM", "TABGD", "TARKM", "TATEN", "TAVHL", "TCELL", "THYAO", "TKFEN", "TKNSA", "TMSN", "TOASO", "TRGYO", "TSKB", "TTKOM", "TTRAK", "TUKAS", "TUPRS", "TURSG", "ULKER", "ULUUN", "VAKBN", "VESBE", "VESTL", "YEOTK", "YKBNK", "YYLGD", "ZOREN"])))
            raw_data = fetch_altin(bist_tum)
            st.session_state.data = pd.DataFrame(raw_data)
            st.session_state.mode = "altin"
        st.success(f"İşlem Tamamlandı: {len(st.session_state.data)} hisse kriterlere uygun bulundu.")

    rsi_filter = st.checkbox("📉 RSI < 35 Filtrele")
    search = st.text_input("Hisse Ara...", "")

# Ana içerik: Tablo ve filtreleme
if st.session_state.data is not None:
    df = st.session_state.data.copy()
    
    # Arama filtrele
    if search:
        df = df[df['Hisse'].str.contains(search.upper(), case=False, na=False)]
    
    # RSI filtrele
    if rsi_filter:
        if st.session_state.mode == "normal":
            df = df[df['RSI'] < 35]
        else:  # Altın mod için 4. sütun (RSI (4S)) filtrele
            if 'RSI (4S)' in df.columns:
                df = df[df['RSI (4S)'] < 35]
    
    # Stilleri uygula ve göster
    if st.session_state.mode == "normal":
        styled_df = style_normal(df)
    else:
        styled_df = style_altin(df)
    
    st.dataframe(styled_df, use_container_width=True)
else:
    st.info("Hazır. Bir analiz başlatın.")
```
