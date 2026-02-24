import streamlit as st
import pandas as pd
import time
from tradingview_ta import get_multiple_analysis, Interval

# Sayfa Genişliği ve Başlık
st.set_page_config(page_title="BIST Altın Vuruş", layout="wide")

st.title("🎯 BIST Altın Vuruş Tarayıcı")
st.markdown("1 Saatlik, 4 Saatlik ve Günlük periyotlarda RSI değerine göre aşırı satım bölgesindeki hisseleri bulur.")

# --- LİSTELER ---
BIST_30 = ["AKBNK", "ALARK", "ARCLK", "ASELS", "ASTOR", "BIMAS", "EKGYO", "ENKAI", "EREGL", "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KOZAA", "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TAVHL", "TCELL", "THYAO", "TOASO", "TUPRS"]

# Örnek BIST Tüm Listesi (Kısaltılmıştır, buraya listenizi ekleyebilirsiniz)
BIST_TUM = sorted(list(set(BIST_30 + ["A1CAP", "ACSEL", "ADEL", "ADESE", "AEFES", "AFYON", "AGHOL", "AGROT", "AHGAZ", "AKCNS", "AKENR", "AKFGY", "AKSA", "AKSEN", "ALBRK", "ALFAS", "ALKA", "ALKIM", "ALVES", "ANELE", "ANGEN", "ANHYT", "ANSGR", "ARCLK", "ARDYZ", "ARENA", "ARSAN", "ASGYO", "ASUZU", "ATATP", "AYDEM", "AYGAZ", "BAGFS", "BANVT", "BARMA", "BERA", "BEYAZ", "BFREN", "BIENP", "BIGCH", "BJKAS", "BLCYT", "BOBET", "BORLS", "BRISA", "BRYAT", "BSOKE", "BTCIM", "BUCIM", "CANTE", "CATES", "CCOLA", "CIMSA", "CLEBI", "CONSE", "CVKMD", "CWENE", "DOAS", "DOHOL", "EBEBK", "ECILC", "ECZYT", "EGEEN", "EGGUB", "EGPRO", "EKGYO", "ENJSA", "ENKAI", "EREGL", "EUPWR", "EUREN", "FENER", "FROTO", "GARFA", "GEDIK", "GENIL", "GESAN", "GLYHO", "GOODY", "GOZDE", "GSRAY", "GUBRF", "GWIND", "HALKB", "HEKTS", "HLGYO", "HTTBT", "HUNER", "IHEVA", "IHLAS", "IMASM", "INDES", "INFO", "IPEKE", "ISCTR", "ISFIN", "ISGYO", "ISMEN", "IZENR", "KAREL", "KARSN", "KAYSE", "KCAER", "KCHOL", "KFEIN", "KLGYO", "KLRMP", "KLSYN", "KOCAER", "KONTR", "KONYA", "KORDS", "KOZAA", "KOZAL", "KUTPO", "KUYAS", "KZBGY", "LIDER", "LOGO", "MAVI", "MEGMT", "MIATK", "MPARK", "MSGYO", "MTRKS", "NATEN", "NETAS", "NTGAZ", "NUHCM", "ODAS", "ONCSM", "ORGE", "OTKAR", "OYAKC", "OZKGY", "PAGYO", "PASEU", "PATEK", "PENTA", "PETKM", "PGSUS", "PNLSN", "POLHO", "QUAGR", "REEDR", "RYGYO", "RYSAS", "SAHOL", "SASA", "SAYAS", "SDTTR", "SISE", "SKBNK", "SMART", "SMRTG", "SNGYO", "SOKM", "TABGD", "TARKM", "TATEN", "TAVHL", "TCELL", "THYAO", "TKFEN", "TKNSA", "TMSN", "TOASO", "TRGYO", "TSKB", "TTKOM", "TTRAK", "TUKAS", "TUPRS", "TURSG", "ULKER", "ULUUN", "VAKBN", "VESBE", "VESTL", "YEOTK", "YKBNK", "YYLGD", "ZOREN"])))

# --- KENAR ÇUBUĞU (AYARLAR) ---
st.sidebar.header("⚙️ Tarama Ayarları")
liste_secimi = st.sidebar.selectbox("Hisse Grubu", ["BIST 30", "BIST TÜM"])
rsi_esik = st.sidebar.slider("RSI Altın Vuruş Eşiği", 10, 50, 40) # 40 varsayılan yapıldı
baslat = st.sidebar.button("🚀 Taramayı Başlat")

# --- ANALİZ FONKSİYONU ---
def analiz_yap(liste):
    bulunanlar = []
    limit = 100
    paketler = [liste[i:i + limit] for i in range(0, len(liste), limit)]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, paket in enumerate(paketler):
        status_text.text(f"Paket {idx+1}/{len(paketler)} analiz ediliyor...")
        tv_hisseler = [f"BIST:{h}" for h in paket]
        
        try:
            # 3 Farklı Periyot Sorgusu
            a1s = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_1_HOUR, symbols=tv_hisseler)
            a4s = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_4_HOURS, symbols=tv_hisseler)
            a1g = get_multiple_analysis(screener="turkey", interval=Interval.INTERVAL_1_DAY, symbols=tv_hisseler)
            
            for symbol in tv_hisseler:
                try:
                    res1 = a1s.get(symbol)
                    res4 = a4s.get(symbol)
                    resg = a1g.get(symbol)
                    
                    if res1 and res4 and resg:
                        r1 = res1.indicators.get("RSI")
                        r4 = res4.indicators.get("RSI")
                        rg = resg.indicators.get("RSI")
                        fiyat = res1.indicators.get("close")
                        
                        # KRİTER: 3 periyotta da RSI < Eşik (40)
                        if r1 < rsi_esik and r4 < rsi_esik and rg < rsi_esik:
                            bulunanlar.append({
                                "Hisse": symbol.split(":")[1],
                                "Fiyat": round(fiyat, 2),
                                "RSI (1S)": round(r1, 2),
                                "RSI (4S)": round(r4, 2),
                                "RSI (1G)": round(rg, 2)
                            })
                except: continue
        except: continue
        
        progress_bar.progress((idx + 1) / len(paketler))
        time.sleep(0.5) # API limit koruması

    status_text.success("Tarama tamamlandı!")
    return bulunanlar

# --- ANA EKRAN MANTIĞI ---
if baslat:
    secili_liste = BIST_30 if liste_secimi == "BIST 30" else BIST_TUM
    sonuclar = analiz_yap(secili_liste)
    
    if sonuclar:
        df = pd.DataFrame(sonuclar)
        
        # Tabloyu özelleştirme
        st.subheader(f"✅ Kriterlere Uyan {len(df)} Hisse Bulundu")
        
        # Renklendirme fonksiyonu
        def color_rsi(val):
            color = 'background-color: #c8e6c9' if val < 30 else 'background-color: #fff9c4'
            return color

        st.dataframe(df.style.applymap(color_rsi, subset=['RSI (1S)', 'RSI (4S)', 'RSI (1G)']))
        
        # CSV İndirme Butonu
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Listeyi CSV olarak indir", csv, "altin_vurus_listesi.csv", "text/csv")
    else:
        st.warning("Maalesef hiçbir hisse her üç periyotta da belirlenen RSI eşiğinin altında değil.")

else:
    st.info("Taramayı başlatmak için sol taraftaki butona tıklayın.")
