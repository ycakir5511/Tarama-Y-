# bist_analiz_streamlit.py
# Gereksinimler: 
# pip install streamlit tradingview-ta pandas

import streamlit as st
import pandas as pd
import time
from tradingview_ta import get_multiple_analysis, Interval
from datetime import datetime

# ────────────────────────────────────────────────
#               CACHE FONKSİYONLARI
# ────────────────────────────────────────────────

@st.cache_data(ttl=900)  # 15 dk cache (TradingView verisi çok sık değişmez)
def getir_normal_analiz(periyot: str, sembol_list: list) -> pd.DataFrame:
    """Normal tarama (tek periyot)"""
    if not sembol_list:
        return pd.DataFrame()

    limit = 100
    paketler = [sembol_list[i:i + limit] for i in range(0, len(sembol_list), limit)]
    satirlar = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    toplam_paket = len(paketler)
    
    for idx, paket in enumerate(paketler, 1):
        tv_semboller = [f"BIST:{h}" for h in paket]
        status_text.text(f"Normal tarama: {idx}/{toplam_paket} paket çekiliyor...")

        try:
            analizler = get_multiple_analysis(
                screener="turkey",
                interval=periyot,
                symbols=tv_semboller
            )

            for sembol, analiz in analizler.items():
                if analiz is None:
                    continue
                ind = analiz.indicators
                fiyat = ind.get("close", 0) or 0
                degisim = ind.get("change", 0) or 0
                rsi = ind.get("RSI", 0) or 0

                satirlar.append({
                    "Hisse": sembol.split(":")[1],
                    "Fiyat": round(fiyat, 2),
                    "Değişim %": round(degisim, 2),
                    "RSI": round(rsi, 2)
                })

            time.sleep(0.45)  # rate limit

        except Exception as e:
            st.warning(f"Paket hatası: {e}")
            continue

        progress_bar.progress(idx / toplam_paket)

    status_text.text("")
    progress_bar.empty()

    df = pd.DataFrame(satirlar)
    if not df.empty:
        df = df.sort_values("RSI", ascending=True)
    return df


@st.cache_data(ttl=900)
def getir_altin_vurus(sembol_list: list) -> pd.DataFrame:
    """3 periyotta RSI < 40 olanlar (Altın Vuruş)"""
    if not sembol_list:
        return pd.DataFrame()

    limit = 100
    paketler = [sembol_list[i:i + limit] for i in range(0, len(sembol_list), limit)]
    satirlar = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    toplam_paket = len(paketler)

    for idx, paket in enumerate(paketler, 1):
        tv_semboller = [f"BIST:{h}" for h in paket]
        status_text.text(f"Altın Vuruş tarama: {idx}/{toplam_paket} paket...")

        try:
            a1s = get_multiple_analysis("turkey", Interval.INTERVAL_1_HOUR,   tv_semboller)
            a4s = get_multiple_analysis("turkey", Interval.INTERVAL_4_HOURS,  tv_semboller)
            a1g = get_multiple_analysis("turkey", Interval.INTERVAL_1_DAY,    tv_semboller)

            for sembol in tv_semboller:
                ana1 = a1s.get(sembol)
                ana4 = a4s.get(sembol)
                anag = a1g.get(sembol)

                if not (ana1 and ana4 and anag):
                    continue

                rsi1 = ana1.indicators.get("RSI", 100)
                rsi4 = ana4.indicators.get("RSI", 100)
                rsig = anag.indicators.get("RSI", 100)
                fiyat = ana1.indicators.get("close", 0)

                if rsi1 < 40 and rsi4 < 40 and rsig < 40:
                    satirlar.append({
                        "Hisse": sembol.split(":")[1],
                        "Fiyat": round(fiyat, 2),
                        "RSI 1S": round(rsi1, 2),
                        "RSI 4S": round(rsi4, 2),
                        "RSI 1G": round(rsig, 2)
                    })

            time.sleep(0.6)

        except Exception as e:
            st.warning(f"Altın paket hatası: {e}")
            continue

        progress_bar.progress(idx / toplam_paket)

    status_text.text("")
    progress_bar.empty()

    df = pd.DataFrame(satirlar)
    if not df.empty:
        df = df.sort_values("RSI 1S", ascending=True)
    return df


# ────────────────────────────────────────────────
#                   UYGULAMA
# ────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="BIST Analiz - Altın Vuruş v2.0 (Streamlit)",
        layout="wide",
        page_icon="📈"
    )

    st.title("BIST Hisse Tarama · Altın Vuruş v2.0")
    st.markdown("**tradingview_ta** kütüphanesi ile RSI temelli tarama • Streamlit arayüz")

    # ── Hisse Listeleri ───────────────────────────────────────
    bist30 = [
        "AKBNK", "ALARK", "ARCLK", "ASELS", "ASTOR", "BIMAS", "EKGYO", "ENKAI", "EREGL",
        "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KOZAA",
        "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TAVHL", "TCELL",
        "THYAO", "TOASO", "TUPRS"
    ]

    # bist_tum listesi (senin kodundaki haliyle - çok uzun, burada kısaltılmış hali var)
    bist_tum = bist30 + [
        "A1CAP", "ACSEL", "ADEL", "ADESE", "AEFES", "AFYON", "AGHOL", "AGROT", "AHGAZ",
        "AKCNS", "AKENR", "AKFGY", "AKSA", "AKSEN", "ALBRK", "ALFAS", "ALKA", "ALKIM",
        # ... kalanını senin orijinal listeden ekleyebilirsin
        "ZOREN", "YKBNK", "YYLGD"   # son birkaç tane örnek
    ]
    bist_tum = sorted(list(set(bist_tum)))   # temizleme

    # ── Sidebar Kontroller ────────────────────────────────────
    with st.sidebar:
        st.header("Tarama Ayarları")
        
        veri_kaynagi = st.radio(
            "Hangi liste?",
            options=["BIST 30", "BIST TÜM"],
            index=0
        )

        tarama_tipi = st.radio(
            "Tarama Türü",
            options=["Normal (Tek Periyot)", "Altın Vuruş (3× RSI < 40)"],
            index=0
        )

        if tarama_tipi == "Normal (Tek Periyot)":
            periyot_sec = st.selectbox(
                "Periyot",
                ["1 Saat", "4 Saat", "1 Gün", "1 Hafta", "1 Ay"],
                index=2
            )
            periyot_map = {
                "1 Saat": Interval.INTERVAL_1_HOUR,
                "4 Saat": Interval.INTERVAL_4_HOURS,
                "1 Gün": Interval.INTERVAL_1_DAY,
                "1 Hafta": Interval.INTERVAL_1_WEEK,
                "1 Ay": Interval.INTERVAL_1_MONTH
            }
            secili_periyot = periyot_map[periyot_sec]
        else:
            secili_periyot = None   # Altın vuruşta kullanılmıyor

        baslat = st.button("🚀 Taramayı Başlat", type="primary", use_container_width=True)

        st.markdown("---")
        st.caption(f"Son güncelleme: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

    # ── Ana Alan ──────────────────────────────────────────────
    col1, col2 = st.columns([3,1])

    with col1:
        arama = st.text_input("Hisse Kodu Ara (ör: SASA, THYAO)", "").strip().upper()

    with col2:
        rsi_filter = st.toggle("Sadece **RSI < 35** göster", value=False)

    if baslat:
        with st.spinner("Veriler TradingView'dan çekiliyor... (biraz zaman alabilir)"):
            if veri_kaynagi == "BIST 30":
                kullanilacak_liste = bist30
            else:
                kullanilacak_liste = bist_tum

            if tarama_tipi == "Normal (Tek Periyot)":
                df = getir_normal_analiz(secili_periyot, kullanilacak_liste)
                mod = "normal"
            else:
                df = getir_altin_vurus(kullanilacak_liste)
                mod = "altin"

            # Cache'i temizlemek istersen: getir_normal_analiz.clear() vb.

            st.session_state["son_df"] = df
            st.session_state["son_mod"] = mod
            st.success(f"Tarama tamamlandı → {len(df)} adet sonuç bulundu")

    # Önceki tarama sonucu varsa onu göster
    if "son_df" in st.session_state:
        df = st.session_state["son_df"].copy()
        mod = st.session_state["son_mod"]

        # Filtreleme
        if arama:
            df = df[df["Hisse"].str.contains(arama, case=False)]

        if rsi_filter:
            if mod == "normal":
                df = df[df["RSI"] < 35]
            else:
                # Altın vuruş zaten <40 → belki <35 istiyorsan ek filtre
                df = df[df["RSI 1S"] < 35]

        if df.empty:
            st.info("Filtrelere uyan hisse bulunamadı.")
        else:
            if mod == "normal":
                sty = df.style.format({
                    "Fiyat": "{:.2f}",
                    "Değişim %": "{:.2f}",
                    "RSI": "{:.1f}"
                }).background_gradient(
                    subset=["Değişim %"], cmap="RdYlGn"
                ).background_gradient(
                    subset=["RSI"], cmap="YlGn_r", vmin=0, vmax=100
                )
                st.dataframe(sty, use_container_width=True, hide_index=True)

            else:  # altin
                sty = df.style.format(precision=2).background_gradient(
                    subset=["RSI 1S", "RSI 4S", "RSI 1G"],
                    cmap="YlOrBr",
                    vmin=10, vmax=50
                )
                st.dataframe(sty, use_container_width=True, hide_index=True)

    else:
        st.info("Henüz tarama yapılmadı. Yan panelden ayarları yapıp **Taramayı Başlat** butonuna basın.")


if __name__ == "__main__":
    main()
