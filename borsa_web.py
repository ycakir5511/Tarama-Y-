import streamlit as st
import pandas as pd
import time
from tradingview_ta import get_multiple_analysis, Interval

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="BIST Analiz v2.1", layout="wide")

# CSS: Buton ve Arayüz Güzelleştirme
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; transition: 0.3s; }
    .stButton>button:hover { border-color: #ffd700; color: #ffd700; }
    </style>
""", unsafe_allow_html=True)

# --- VERİ SETLERİ ---
BIST_30 = ["AKBNK", "ALARK", "ARCLK", "ASELS", "ASTOR", "BIMAS", "EKGYO", "ENKAI", "EREGL", "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KOZAA", "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TAVHL", "TCELL", "THYAO", "TOASO", "TUPRS"]
BIST_TUM = sorted(list(set(BIST_30 + ["A1CAP", "ACSEL", "ADEL", "ADESE", "AEFES", "AFYON", "AGHOL", "AGROT", "AHGAZ", "AKCNS", "AKENR", "AKFGY", "AKSA", "AKSEN", "ALBRK", "ALFAS", "ALKA", "ALKIM", "ALVES", "ANELE", "ANGEN", "ANHYT", "ANSGR", "ARDYZ", "ARENA", "ARSAN", "ASGYO", "ASUZU", "ATATP", "AYDEM", "AYGAZ", "BAGFS", "BANVT", "BARMA", "BERA", "BEYAZ", "BFREN", "BIENP", "BIGCH", "BJKAS", "BLCYT", "BOBET", "BORLS", "BRISA", "BRYAT", "BSOKE", "BTCIM", "BUCIM", "CANTE", "CATES", "CCOLA", "CIMSA", "CLEBI", "CONSE", "CVKMD", "CWENE", "DOAS", "DOHOL", "EBEBK", "ECILC", "ECZYT", "EGEEN", "EGGUB", "EGPRO", "ENJSA", "EUPWR", "EUREN", "FENER", "GARFA", "GEDIK", "GENIL", "GESAN", "GLYHO", "GOODY", "GOZDE", "GSRAY", "GWIND", "HALKB", "HLGYO", "HTTBT", "HUNER", "IHEVA", "IHLAS", "IMASM", "INDES", "INFO", "IPEKE", "ISFIN", "ISGYO", "ISMEN", "IZENR", "KAREL", "KARSN", "KAYSE", "KCAER", "KFEIN", "KLGYO", "KLRMP", "KLSYN", "KOCAER", "KONYA", "KORDS", "KRYPT", "KUTPO", "KUYAS", "KZBGY", "LIDER", "LOGO", "MAVI", "MEGMT", "MIATK", "MPARK", "MSGYO", "MTRKS", "NATEN", "NETAS", "NTGAZ", "NUHCM", "ONCSM", "ORGE", "OTKAR", "OZKGY", "PAGYO", "PASEU", "PATEK", "PENTA", "PNLSN", "POLHO", "QUAGR", "REEDR", "RYGYO", "RYSAS", "SAYAS", "SDTTR", "SKBNK", "SMART", "SMRTG", "SNGYO", "SOKM", "TABGD", "TARKM", "TATEN", "TKFEN", "TKNSA", "TMSN", "TRGYO", "TSKB", "TTKOM", "TTRAK", "TUKAS", "TURSG", "ULKER", "ULUUN", "VAKBN", "VESBE", "VESTL", "YEOTK", "YKBNK", "YYLGD", "ZOREN"])))

# --- ANALİZ FONKSİYONLARI ---
def fetch_data(hisse_listesi, mode="normal", periyot=Interval.INTERVAL_1_HOUR):
    sonuclar = []
    limit = 50 # Paket boyutunu 100'den 50'ye düşürdük (daha stabil)
    paketler = [hisse_listesi[i:i + limit] for i in range(0, len(hisse_listesi), limit)]
    
    p_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, paket in enumerate(paketler):
        tv_hisseler = [f"BIST:{h}" for h in paket]
        try:
            status_text.text(f"İşleniyor: Paket {idx+1}/{len(paketler)}...")
            
            if mode == "normal":
                analizler = get_multiple_analysis(screener="turkey", interval=periyot, symbols=tv_hisseler)
                if analizler:
                    for symbol, analiz in analizler.items():
                        if analiz:
                            ind = analiz.indicators
                            sonuclar.append({
                                "Hisse": symbol.split(":")[1],
                                "Fiyat": round(ind.get("close", 0) or 0, 2),
                                "Değişim %": round(ind.get("change", 0) or 0, 2),
                                "RSI": round(ind.get("RSI", 100) or 100, 2)
                            })
            else: # Altın Vuruş Modu
                a1s = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_1_HOUR, symbols=tv_hisseler)
                time.sleep(0.3) # API'yi dinlendir
                a4s = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_4_HOURS, symbols=tv_hisseler)
                time.sleep(0.3)
                a1g = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_1_DAY, symbols=tv_hisseler)

                for s in tv_hisseler:
                    if s in a1s and s in a4s and s in a1g:
                        if a1s[s] and a4s[s] and a1g[s]:
                            r1, r4, rg = a1s[s].indicators.get("RSI", 100), a4s[s].indicators.get("RSI", 100), a1g[s].indicators.get("RSI", 100)
                            if r1 < 40 and r4 < 40 and rg < 40:
                                sonuclar.append({
                                    "Hisse": s.split(":")[1],
                                    "Fiyat": round(a1s[s].indicators.get("close", 0) or 0, 2),
                                    "RSI (1S)": round(r1 or 0, 2),
                                    "RSI (4S)": round(r4 or 0, 2),
                                    "RSI (1G)": round(rg or 0, 2)
                                })
            
            time.sleep(0.6) # Her paketten sonra bekleme süresini artırdık
        except Exception as e:
            st.warning(f"Bağlantı hatası: {idx+1}. paket atlandı.")
            continue
            
        p_bar.progress((idx + 1) / len(paketler))
    
    status_text.empty()
    return pd.DataFrame(sonuclar)

# --- ARAYÜZ ---
st.title("🎯 BIST Analiz - Altın Vuruş v2.1")

c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
with c1:
    evren = st.selectbox("Hisse Grubu", ["BIST 30", "BIST TÜM"])
with c2:
    periyot_str = st.selectbox("Periyot", ["1 Saat", "4 Saat", "1 Gün", "1 Hafta", "1 Ay"])
    p_map = {"1 Saat": Interval.INTERVAL_1_HOUR, "4 Saat": Interval.INTERVAL_4_HOURS, "1 Gün": Interval.INTERVAL_1_DAY, "1 Hafta": Interval.INTERVAL_1_WEEK, "1 Ay": Interval.INTERVAL_1_MONTH}
with c3:
    st.write(" ")
    btn_normal = st.button("🚀 Normal Analiz")
with c4:
    st.write(" ")
    btn_altin = st.button("🎯 ALTIN VURUŞ")

st.divider()

f1, f2 = st.columns([3, 5])
with f1:
    rsi_filtre = st.toggle("📉 Sadece RSI < 35 Filtresi", value=False)
with f2:
    search_query = st.text_input("🔍 Hisse Ara...", "").upper()

# --- TETİKLEYİCİLER ---
hisseler = BIST_30 if evren == "BIST 30" else BIST_TUM

if btn_normal:
    # Eski veriyi temizle ve yeni çek
    st.session_state['data'] = fetch_data(hisseler, mode="normal", periyot=p_map[periyot_str])
    st.session_state['mode'] = 'normal'

if btn_altin:
    st.session_state['data'] = fetch_data(hisseler, mode="altin")
    st.session_state['mode'] = 'altin'

# --- GÖRÜNTÜLEME ---
if 'data' in st.session_state and not st.session_state['data'].empty:
    df_final = st.session_state['data'].copy()

    # Filtreler
    if rsi_filtre:
        col = 'RSI' if st.session_state['mode'] == 'normal' else 'RSI (1S)'
        df_final = df_final[df_final[col] < 35]
    
    if search_query:
        df_final = df_final[df_final['Hisse'].str.contains(search_query)]

    st.subheader(f"📊 Sonuçlar ({len(df_final)} Hisse)")

    # Renklendirme
    def style_df(x):
        c = pd.DataFrame('', index=x.index, columns=x.columns)
        if 'RSI' in x.columns:
            c.loc[x['RSI'] < 35, 'RSI'] = 'background-color: #d4edda; color: #155724'
        if 'Hisse' in x.columns and st.session_state['mode'] == 'altin':
            c['Hisse'] = 'background-color: #fff3cd; font-weight: bold'
        return c

    st.dataframe(df_final.style.apply(style_df, axis=None), use_container_width=True, height=500)
elif 'data' in st.session_state:
    st.warning("Kriterlere uygun hisse bulunamadı veya veri çekilemedi.")
else:
    st.info("Lütfen bir analiz başlatın.")
