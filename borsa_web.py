import streamlit as st
import pandas as pd
import time
from tradingview_ta import get_multiple_analysis, Interval

# Sayfa Ayarları
st.set_page_config(page_title="BIST RSI Tarayıcı", layout="wide")

# Hisse Listeleri
BIST30 = ["AKBNK", "ALARK", "ARCLK", "ASELS", "ASTOR", "BIMAS", "EKGYO", "ENKAI", "EREGL", "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KOZAA", "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TAVHL", "TCELL", "THYAO", "TOASO", "TUPRS"]
# Not: Hız için buraya sadece örnek ekledim, sizin tam listenizi buraya yapıştırabilirsiniz
BIST_TUM = sorted(list(set(BIST30 + ["THYAO", "SISE", "EREGL", "KCHOL"]))) 

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
