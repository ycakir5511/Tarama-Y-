import sys
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QPushButton, QLabel, QHeaderView, 
                             QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QBrush, QFont
from tradingview_ta import get_multiple_analysis, Interval

# --- YENİ: Altın Vuruş İçin Özel İşleyici ---
class AltinVurusWorker(QThread):
    tek_hisse_bitti = pyqtSignal(dict)
    islem_tamam = pyqtSignal(int)

    def __init__(self, hisse_listesi):
        super().__init__()
        self.hisse_listesi = hisse_listesi

    def run(self):
        limit = 100 
        paketler = [self.hisse_listesi[i:i + limit] for i in range(0, len(self.hisse_listesi), limit)]
        toplam_bulunan = 0

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

                        # KRİTER: 3 periyotta da RSI < 35
                        if rsi1 < 40 and rsi4 < 40 and rsig < 40:
                            self.tek_hisse_bitti.emit({
                                "hisse": symbol.split(":")[1],
                                "fiyat": round(fiyat, 2),
                                "rsi1": round(rsi1, 2),
                                "rsi4": round(rsi4, 2),
                                "rsig": round(rsig, 2),
                                "mod": "altin"
                            })
                            toplam_bulunan += 1
                    except: continue
                
                time.sleep(0.5) # API limitlerine takılmamak için
            except: continue
            
        self.islem_tamam.emit(toplam_bulunan)

class VeriCekici(QThread):
    tek_hisse_bitti = pyqtSignal(dict)
    islem_tamam = pyqtSignal(int)

    def __init__(self, periyot, hisse_listesi):
        super().__init__()
        self.periyot = periyot
        self.hisse_listesi = hisse_listesi

    def run(self):
        limit = 100 
        paketler = [self.hisse_listesi[i:i + limit] for i in range(0, len(self.hisse_listesi), limit)]
        toplam = 0

        for paket in paketler:
            tv_hisseler = [f"BIST:{h}" for h in paket]
            try:
                analizler = get_multiple_analysis(screener="turkey", interval=self.periyot, symbols=tv_hisseler)
                if analizler:
                    for symbol, analiz in analizler.items():
                        if analiz is None: continue
                        ind = analiz.indicators
                        
                        fiyat = ind.get("close", 0) or 0
                        degisim = ind.get("change", 0) or 0
                        rsi = ind.get("RSI", 0) or 0

                        self.tek_hisse_bitti.emit({
                            "hisse": symbol.split(":")[1],
                            "fiyat": round(fiyat, 2),
                            "degisim": round(degisim, 2),
                            "rsi": round(rsi, 2),
                            "mod": "normal"
                        })
                        toplam += 1
                time.sleep(0.4) 
            except: continue
        self.islem_tamam.emit(toplam)

class BorsaUygulamasi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BIST Analiz - Altın Vuruş v2.0")
        self.resize(1100, 800)
        
        self.bist30 = ["AKBNK", "ALARK", "ARCLK", "ASELS", "ASTOR", "BIMAS", "EKGYO", "ENKAI", "EREGL", "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KOZAA", "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TAVHL", "TCELL", "THYAO", "TOASO", "TUPRS"]
        # (Listeniz aynı kalacak şekilde kısaltılmıştır, sizdeki tam listeyi kullanmaya devam edin)
        self.bist_tum = sorted(list(set(self.bist30 + ["A1CAP", "ACSEL", "ADEL", "ADESE", "AEFES", "AFYON", "AGHOL", "AGROT", "AHGAZ", "AKCNS", "AKENR", "AKFGY", "AKSA", "AKSEN", "ALBRK", "ALFAS", "ALKA", "ALKIM", "ALVES", "ANELE", "ANGEN", "ANHYT", "ANSGR", "ARCLK", "ARDYZ", "ARENA", "ARSAN", "ASGYO", "ASUZU", "ATATP", "AYDEM", "AYGAZ", "BAGFS", "BANVT", "BARMA", "BERA", "BEYAZ", "BFREN", "BIENP", "BIGCH", "BJKAS", "BLCYT", "BOBET", "BORLS", "BRISA", "BRYAT", "BSOKE", "BTCIM", "BUCIM", "CANTE", "CATES", "CCOLA", "CIMSA", "CLEBI", "CONSE", "CVKMD", "CWENE", "DOAS", "DOHOL", "EBEBK", "ECILC", "ECZYT", "EGEEN", "EGGUB", "EGPRO", "EKGYO", "ENJSA", "ENKAI", "EREGL", "EUPWR", "EUREN", "FENER", "FROTO", "GARFA", "GEDIK", "GENIL", "GESAN", "GLYHO", "GOODY", "GOZDE", "GSRAY", "GUBRF", "GWIND", "HALKB", "HEKTS", "HLGYO", "HTTBT", "HUNER", "IHEVA", "IHLAS", "IMASM", "INDES", "INFO", "IPEKE", "ISCTR", "ISFIN", "ISGYO", "ISMEN", "IZENR", "KAREL", "KARSN", "KAYSE", "KCAER", "KCHOL", "KFEIN", "KLGYO", "KLRMP", "KLSYN", "KOCAER", "KONTR", "KONYA", "KORDS", "KOZAA", "KOZAL", "KRYPT", "KUTPO", "KUYAS", "KZBGY", "LIDER", "LOGO", "MAVI", "MEGMT", "MIATK", "MPARK", "MSGYO", "MTRKS", "NATEN", "NETAS", "NTGAZ", "NUHCM", "ODAS", "ONCSM", "ORGE", "OTKAR", "OYAKC", "OZKGY", "PAGYO", "PASEU", "PATEK", "PENTA", "PETKM", "PGSUS", "PNLSN", "POLHO", "QUAGR", "REEDR", "RYGYO", "RYSAS", "SAHOL", "SASA", "SAYAS", "SDTTR", "SISE", "SKBNK", "SMART", "SMRTG", "SNGYO", "SOKM", "TABGD", "TARKM", "TATEN", "TAVHL", "TCELL", "THYAO", "TKFEN", "TKNSA", "TMSN", "TOASO", "TRGYO", "TSKB", "TTKOM", "TTRAK", "TUKAS", "TUPRS", "TURSG", "ULKER", "ULUUN", "VAKBN", "VESBE", "VESTL", "YEOTK", "YKBNK", "YYLGD", "ZOREN"])))

        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        nav = QHBoxLayout()
        self.e_sel = QComboBox(); self.e_sel.addItems(["BIST 30", "BIST TÜM"])
        self.p_sel = QComboBox(); self.p_sel.addItems(["1 Saat", "4 Saat", "1 Gün", "1 Hafta", "1 Ay"])
        
        self.btn_run = QPushButton("🚀 Analizi Başlat")
        self.btn_run.clicked.connect(self.start_scan)
        
        # --- YENİ: ALTIN VURUŞ BUTONU ---
        self.btn_altin = QPushButton("🎯 ALTIN VURUŞ (3x RSI < 40)")
        self.btn_altin.setStyleSheet("background-color: #ffd700; color: black; font-weight: bold; border-radius: 5px;")
        self.btn_altin.clicked.connect(self.start_altin_vurus)

        self.btn_rsi_filter = QPushButton("📉 RSI < 35 Filtrele")
        self.btn_rsi_filter.setCheckable(True)
        self.btn_rsi_filter.clicked.connect(self.run_all_filters)
        self.btn_rsi_filter.setStyleSheet("QPushButton:checked { background-color: #c8e6c9; font-weight: bold; }")

        self.search = QLineEdit(); self.search.setPlaceholderText("Hisse Ara...")
        self.search.textChanged.connect(self.run_all_filters)
        
        nav.addWidget(self.e_sel)
        nav.addWidget(self.p_sel)
        nav.addWidget(self.btn_run)
        nav.addWidget(self.btn_altin) # Altın vuruş eklendi
        nav.addWidget(self.btn_rsi_filter)
        nav.addStretch()
        nav.addWidget(self.search)
        layout.addLayout(nav)

        self.table = QTableWidget()
        self.setup_table_headers("normal")
        layout.addWidget(self.table)

        self.status = QLabel("Hazır.")
        layout.addWidget(self.status)

    def setup_table_headers(self, mode):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        if mode == "normal":
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["Hisse", "Fiyat", "Değişim %", "RSI"])
        else:
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels(["Hisse", "Fiyat", "RSI (1S)", "RSI (4S)", "RSI (1G)"])
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def run_all_filters(self):
        search_txt = self.search.text().upper()
        rsi_only = self.btn_rsi_filter.isChecked()

        for i in range(self.table.rowCount()):
            hisse_item = self.table.item(i, 0)
            rsi_item = self.table.item(i, 3)
            if not hisse_item or not rsi_item: continue
            
            hisse_adi = hisse_item.text()
            try: rsi_val = float(rsi_item.text())
            except: rsi_val = 100

            match_text = search_txt in hisse_adi
            match_rsi = (rsi_val < 35) if rsi_only else True
            self.table.setRowHidden(i, not (match_text and match_rsi))

    def start_scan(self):
        self.setup_table_headers("normal")
        self.btn_run.setEnabled(False)
        self.btn_altin.setEnabled(False)
        self.status.setText("Tarama yapılıyor (Normal Mod)...")
        
        p_map = {
            "1 Saat": Interval.INTERVAL_1_HOUR, 
            "4 Saat": Interval.INTERVAL_4_HOURS, 
            "1 Gün": Interval.INTERVAL_1_DAY,
            "1 Hafta": Interval.INTERVAL_1_WEEK,
            "1 Ay": Interval.INTERVAL_1_MONTH
        }
        
        liste = self.bist30 if self.e_sel.currentText() == "BIST 30" else self.bist_tum
        self.worker = VeriCekici(p_map[self.p_sel.currentText()], liste)
        self.worker.tek_hisse_bitti.connect(self.add_row)
        self.worker.islem_tamam.connect(self.finish_scan)
        self.worker.start()

    def start_altin_vurus(self):
        self.setup_table_headers("altin")
        self.btn_run.setEnabled(False)
        self.btn_altin.setEnabled(False)
        self.status.setText("Altın Vuruş Taraması: BIST TÜM için 3 periyot kontrol ediliyor...")
        
        self.worker = AltinVurusWorker(self.bist_tum)
        self.worker.tek_hisse_bitti.connect(self.add_row)
        self.worker.islem_tamam.connect(self.finish_scan)
        self.worker.start()

    def finish_scan(self, count):
        self.table.setSortingEnabled(True)
        self.btn_run.setEnabled(True)
        self.btn_altin.setEnabled(True)
        self.status.setText(f"İşlem Tamamlandı: {count} hisse kriterlere uygun bulundu.")

    def add_row(self, d):
        r = self.table.rowCount(); self.table.insertRow(r)
        
        if d["mod"] == "normal":
            keys = ["hisse", "fiyat", "degisim", "rsi"]
        else:
            keys = ["hisse", "fiyat", "rsi1", "rsi4", "rsig"]

        for i, k in enumerate(keys):
            item = QTableWidgetItem()
            val = d[k]
            
            if isinstance(val, (int, float)):
                item.setData(Qt.ItemDataRole.DisplayRole, val)
            else:
                item.setData(Qt.ItemDataRole.DisplayRole, str(val))

            # Renklendirme
            if d["mod"] == "normal":
                if k == "degisim":
                    if val > 0: item.setForeground(QBrush(QColor("#2e7d32")))
                    elif val < 0: item.setForeground(QBrush(QColor("#c62828")))
                if k == "rsi":
                    if val < 30: item.setBackground(QBrush(QColor("#c8e6c9")))
                    elif val > 70: item.setBackground(QBrush(QColor("#ffcdd2")))
            else:
                # Altın Vuruş Renklendirmesi
                if i >= 2: # RSI sütunları
                    item.setBackground(QBrush(QColor("#fff9c4"))) # Açık sarı
                    item.setForeground(QBrush(QColor("#000000")))
                if k == "hisse":
                    font = QFont(); font.setBold(True)
                    item.setFont(font)
                    item.setBackground(QBrush(QColor("#ffd700"))) # Altın sarısı

            self.table.setItem(r, i, item)

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion")
    win = BorsaUygulamasi(); win.show(); sys.exit(app.exec())
