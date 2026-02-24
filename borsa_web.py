import streamlit as st
import pandas as pd
import time
from tradingview_ta import get_multiple_analysis, Interval

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="BIST Analiz - Altın Vuruş", layout="wide")

# --- VERİ LİSTESİ ---
BIST_30 = ["AKBNK", "ALARK", "ARCLK", "ASELS", "ASTOR", "BIMAS", "EKGYO", "ENKAI", "EREGL", "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KOZAA", "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TAVHL", "TCELL", "THYAO", "TOASO", "TUPRS"]
BIST_TUM = sorted(list(set(BIST_30 + ["A1CAP", "ACSEL", "ADEL", "ADESE", "AEFES", "AFYON", "AGHOL", "AGROT", "AHGAZ", "AKCNS", "AKENR", "AKFGY", "AKSA", "AKSEN", "ALBRK", "ALFAS", "ALKA", "ALKIM", "ALVES", "ANELE", "ANGEN", "ANHYT", "ANSGR", "ARCLK", "ARDYZ", "ARENA", "ARSAN", "ASGYO", "ASUZU", "ATATP", "AYDEM", "AYGAZ", "BAGFS", "BANVT", "BARMA", "BERA", "BEYAZ", "BFREN", "BIENP", "BIGCH", "BJKAS", "BLCYT", "BOBET", "BORLS", "BRISA", "BRYAT", "BSOKE", "BTCIM", "BUCIM", "CANTE", "CATES", "CCOLA", "CIMSA", "CLEBI", "CONSE", "CVKMD", "CWENE", "DOAS", "DOHOL", "EBEBK", "ECILC", "ECZYT", "EGEEN", "EGGUB", "EGPRO", "EKGYO", "ENJSA", "ENKAI", "EREGL", "EUPWR", "EUREN", "FENER", "FROTO", "GARFA", "GEDIK", "GENIL", "GESAN", "GLYHO", "GOODY", "GOZDE", "GSRAY", "GUBRF", "GWIND", "HALKB", "HEKTS", "HLGYO", "HTTBT", "HUNER", "IHEVA", "IHLAS", "IMASM", "INDES", "INFO", "IPEKE", "ISCTR", "ISFIN", "ISGYO", "ISMEN", "IZENR", "KAREL", "KARSN", "KAYSE", "KCAER", "KCHOL", "KFEIN", "KLGYO", "KLRMP", "KLSYN", "KOCAER", "KONTR", "KONYA", "KORDS", "KOZAA", "KOZAL", "KRYPT", "KUTPO", "KUYAS", "KZBGY", "LIDER", "LOGO", "MAVI", "MEGMT", "MIATK", "MPARK", "MSGYO", "MTRKS", "NATEN", "NETAS", "NTGAZ", "NUHCM", "ODAS", "ONCSM", "ORGE", "OTKAR", "OYAKC", "OZKGY", "PAGYO", "PASEU", "PATEK", "PENTA", "PETKM", "PGSUS", "PNLSN", "POLHO", "QUAGR", "REEDR", "RYGYO", "RYSAS", "SAHOL", "SASA", "SAYAS", "SDTTR", "SISE", "SKBNK", "SMART", "SMRTG", "SNGYO", "SOKM", "TABGD", "TARKM", "TATEN", "TAVHL", "TCELL", "THYAO", "TKFEN", "TKNSA", "TMSN", "TOASO", "TRGYO", "TSKB", "TTKOM", "TTRAK", "TUKAS", "TUPRS", "TURSG", "ULKER", "ULUUN", "VAKBN", "VESBE", "VESTL", "YEOTK", "YKBNK", "YYLGD", "ZOREN"])))

# --- FONKSİYONLAR ---
def veri_cek_normal(periyot, hisse_listesi):
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
        except:
            continue
        progress_bar.progress((idx + 1) / len(paketler))
    return pd.DataFrame(sonuclar)

def veri_cek_altin(hisse_listesi):
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

            for symbol in tv_hisseler:
                try:
                    r1, r4, rg = a1s[symbol].indicators["RSI"], a4s[symbol].indicators["RSI"], a1g[symbol].indicators["RSI"]
                    if r1 < 40 and r4 < 40 and rg < 40:
                        sonuclar.append({
                            "Hisse": symbol.split(":")[1],
                            "Fiyat": round(a1s[symbol].indicators["close"], 2),
                            "RSI (1S)": round(r1, 2),
                            "RSI (4S)": round(r4, 2),
                            "RSI (1G)": round(rg, 2)
                        })
                except: continue
            time.sleep(0.5)
        except: continue
        progress_bar.progress((idx + 1) / len(paketler))
    return pd.DataFrame(sonuclar)

# --- UI TASARIMI ---
st.title("🎯 BIST Analiz Portalı")

with st.sidebar:
    st.header("⚙️ Ayarlar")
    evren = st.selectbox("Hisse Kümesi", ["BIST 30", "BIST TÜM"])
    periyot_label = st.selectbox("Periyot (Normal Mod)", ["1 Saat", "4 Saat", "1 Gün", "1 Hafta", "1 Ay"])
    
    p_map = {
        "1 Saat": Interval.INTERVAL_1_HOUR, "4 Saat": Interval.INTERVAL_4_HOURS,
        "1 Gün": Interval.INTERVAL_1_DAY, "1 Hafta": Interval.INTERVAL_1_WEEK, "1 Ay": Interval.INTERVAL_1_MONTH
    }
    
    secili_liste = BIST_30 if evren == "BIST 30" else BIST_TUM
    
    st.divider()
    btn_normal = st.button("🚀 Analizi Başlat", use_container_width=True)
    btn_altin = st.button("🎯 ALTIN VURUŞ", use_container_width=True, type="primary")

# --- ANA EKRAN ---
col1, col2 = st.columns([2, 1])
with col2:
    search = st.text_input("🔍 Hisse Ara", "").upper()
with col1:
    rsi_filter = st.toggle("📉 Sadece RSI < 35 olanları göster")

# Analiz Mantığı
if btn_normal:
    st.subheader(f"📊 Normal Analiz Sonuçları ({periyot_label})")
    df = veri_cek_normal(p_map[periyot_label], secili_liste)
    
    if not df.empty:
        # Filtreleme
        if search:
            df = df[df['Hisse'].str.contains(search)]
        if rsi_filter:
            df = df[df['RSI'] < 35]
            
        # Renklendirme ve Tablo
        st.dataframe(df.style.background_gradient(subset=['RSI'], cmap='RdYlGn_r'), use_container_width=True)
    else:
        st.warning("Veri alınamadı.")

elif btn_altin:
    st.subheader("🎯 Altın Vuruş Sonuçları (3x RSI < 40)")
    df = veri_cek_altin(BIST_TUM)
    
    if not df.empty:
        if search:
            df = df[df['Hisse'].str.contains(search)]
        
        # Stil Verme
        styled_df = df.style.map(lambda x: 'background-color: #ffd700; color: black; font-weight: bold', subset=['Hisse'])
        st.dataframe(styled_df, use_container_width=True)
        st.success(f"Kritere uygun {len(df)} hisse bulundu.")
    else:
        st.info("Kriterlere uygun hisse bulunamadı.")
