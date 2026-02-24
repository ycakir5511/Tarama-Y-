import streamlit as st
import pandas as pd
import time
from tradingview_ta import get_multiple_analysis, Interval

# Sayfa Ayarları
st.set_page_config(page_title="BIST Analiz Terminali", layout="wide")

st.title("📈 BIST Teknik Analiz Paneli")

# --- LİSTELER ---
BIST_30 = ["AKBNK", "ALARK", "ARCLK", "ASELS", "ASTOR", "BIMAS", "EKGYO", "ENKAI", "EREGL", "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KOZAA", "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TAVHL", "TCELL", "THYAO", "TOASO", "TUPRS"]
# BIST_TUM listesini buraya eksiksiz ekleyebilirsiniz.
BIST_TUM = sorted(list(set(BIST_30 + ["A1CAP", "ACSEL", "ADEL", "ADESE", "AEFES", "AFYON", "AGHOL", "AGROT", "AHGAZ", "AKCNS", "AKENR", "AKFGY", "AKSA", "AKSEN", "ALBRK", "ALFAS", "ALKA", "ALKIM", "ALVES", "ANELE", "ANGEN", "ANHYT", "ANSGR", "ARCLK", "ARDYZ", "ARENA", "ARSAN", "ASGYO", "ASUZU", "ATATP", "AYDEM", "AYGAZ", "BAGFS", "BANVT", "BARMA", "BERA", "BEYAZ", "BFREN", "BIENP", "BIGCH", "BJKAS", "BLCYT", "BOBET", "BORLS", "BRISA", "BRYAT", "BSOKE", "BTCIM", "BUCIM", "CANTE", "CATES", "CCOLA", "CIMSA", "CLEBI", "CONSE", "CVKMD", "CWENE", "DOAS", "DOHOL", "EBEBK", "ECILC", "ECZYT", "EGEEN", "EGGUB", "EGPRO", "EKGYO", "ENJSA", "ENKAI", "EREGL", "EUPWR", "EUREN", "FENER", "FROTO", "GARFA", "GEDIK", "GENIL", "GESAN", "GLYHO", "GOODY", "GOZDE", "GSRAY", "GUBRF", "GWIND", "HALKB", "HEKTS", "HLGYO", "HTTBT", "HUNER", "IHEVA", "IHLAS", "IMASM", "INDES", "INFO", "IPEKE", "ISCTR", "ISFIN", "ISGYO", "ISMEN", "IZENR", "KAREL", "KARSN", "KAYSE", "KCAER", "KCHOL", "KFEIN", "KLGYO", "KLRMP", "KLSYN", "KOCAER", "KONTR", "KONYA", "KORDS", "KOZAA", "KOZAL", "KUTPO", "KUYAS", "KZBGY", "LIDER", "LOGO", "MAVI", "MEGMT", "MIATK", "MPARK", "MSGYO", "MTRKS", "NATEN", "NETAS", "NTGAZ", "NUHCM", "ODAS", "ONCSM", "ORGE", "OTKAR", "OYAKC", "OZKGY", "PAGYO", "PASEU", "PATEK", "PENTA", "PETKM", "PGSUS", "PNLSN", "POLHO", "QUAGR", "REEDR", "RYGYO", "RYSAS", "SAHOL", "SASA", "SAYAS", "SDTTR", "SISE", "SKBNK", "SMART", "SMRTG", "SNGYO", "SOKM", "TABGD", "TARKM", "TATEN", "TAVHL", "TCELL", "THYAO", "TKFEN", "TKNSA", "TMSN", "TOASO", "TRGYO", "TSKB", "TTKOM", "TTRAK", "TUKAS", "TUPRS", "TURSG", "ULKER", "ULUUN", "VAKBN", "VESBE", "VESTL", "YEOTK", "YKBNK", "YYLGD", "ZOREN"])))

# --- KENAR ÇUBUĞU ---
st.sidebar.header("⚙️ Ayarlar")
tarama_modu = st.sidebar.radio("Tarama Modu", ["Normal Tarama", "Altın Vuruş (3 Periyot)"])
hisse_grubu = st.sidebar.selectbox("Hisse Grubu", ["BIST 30", "BIST TÜM"])

periyot_map = {
    "1 Saat": Interval.INTERVAL_1_HOUR,
    "4 Saat": Interval.INTERVAL_4_HOURS,
    "1 Gün": Interval.INTERVAL_1_DAY,
    "1 Hafta": Interval.INTERVAL_1_WEEK
}

# RSI Eşiğini 35 Olarak Ayarlıyoruz
rsi_esik = st.sidebar.slider("RSI Eşik Değeri", 10, 70, 35)

if tarama_modu == "Normal Tarama":
    secili_periyot = st.sidebar.selectbox("Periyot Seçin", list(periyot_map.keys()))
    # Yazıyı da 35 olarak güncelledik
    rsi_filtre_aktif = st.sidebar.checkbox(f"Sadece RSI < {rsi_esik} olanları göster", value=True)
else:
    st.sidebar.info("Altın Vuruş: 1S, 4S ve Günlük RSI değerlerinin tamamı seçilen eşiğin altında olmalıdır.")
    rsi_filtre_aktif = True

baslat = st.sidebar.button("🚀 Analizi Başlat")

# --- FONKSİYONLAR ---
def normal_tarama(liste, periyot_str):
    veriler = []
    tv_periyot = periyot_map[periyot_str]
    paketler = [liste[i:i + 100] for i in range(0, len(liste), 100)]
    
    p_bar = st.progress(0)
    for idx, paket in enumerate(paketler):
        symbols = [f"BIST:{h}" for h in paket]
        try:
            analizler = get_multiple_analysis(screener="turkey", interval=tv_periyot, symbols=symbols)
            for s, a in analizler.items():
                if a:
                    rsi = a.indicators.get("RSI", 0)
                    fiyat = a.indicators.get("close", 0)
                    degisim = a.indicators.get("change", 0)
                    
                    data = {"Hisse": s.split(":")[1], "Fiyat": round(fiyat, 2), "Değişim %": round(degisim, 2), "RSI": round(rsi, 2)}
                    
                    if rsi_filtre_aktif:
                        if rsi < rsi_esik: veriler.append(data)
                    else:
                        veriler.append(data)
        except: continue
        p_bar.progress((idx + 1) / len(paketler))
        time.sleep(0.4)
    return veriler

def altin_vurus_tarama(liste):
    veriler = []
    paketler = [liste[i:i + 100] for i in range(0, len(liste), 100)]
    
    p_bar = st.progress(0)
    for idx, paket in enumerate(paketler):
        symbols = [f"BIST:{h}" for h in paket]
        try:
            a1s = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_1_HOUR, symbols=symbols)
            a4s = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_4_HOURS, symbols=symbols)
            a1g = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_1_DAY, symbols=symbols)
            
            for s in symbols:
                r1 = a1s[s].indicators.get("RSI", 100) if a1s[s] else 100
                r4 = a4s[s].indicators.get("RSI", 100) if a4s[s] else 100
                rg = a1g[s].indicators.get("RSI", 100) if a1g[s] else 100
                
                if r1 < rsi_esik and r4 < rsi_esik and rg < rsi_esik:
                    veriler.append({
                        "Hisse": s.split(":")[1],
                        "Fiyat": round(a1s[s].indicators.get("close", 0), 2),
                        "RSI (1S)": round(r1, 2),
                        "RSI (4S)": round(r4, 2),
                        "RSI (1G)": round(rg, 2)
                    })
        except: continue
        p_bar.progress((idx + 1) / len(paketler))
        time.sleep(0.5)
    return veriler

# --- ANA EKRAN ---
if baslat:
    secili_liste = BIST_30 if hisse_grubu == "BIST 30" else BIST_TUM
    
    if tarama_modu == "Normal Tarama":
        sonuclar = normal_tarama(secili_liste, secili_periyot)
    else:
        sonuclar = altin_vurus_tarama(secili_liste)

    if sonuclar:
        df = pd.DataFrame(sonuclar)
        st.success(f"Analiz tamamlandı! {len(df)} hisse kriterlere uyuyor.")
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Listeyi İndir (CSV)", csv, "bist_tarama.csv", "text/csv")
    else:
        st.warning(f"RSI < {rsi_esik} kriterine uygun hisse bulunamadı.")
else:
    st.info("Sol menüden ayarları yapıp 'Analizi Başlat'a tıklayın.")
