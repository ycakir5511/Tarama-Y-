import sys
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QPushButton, QLabel, QHeaderView, 
                             QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QBrush
from tradingview_ta import get_multiple_analysis, Interval

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
                            "rsi": round(rsi, 2)
                        })
                        toplam += 1
                time.sleep(0.4) 
            except: continue
        self.islem_tamam.emit(toplam)

class BorsaUygulamasi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BIST RSI Tarayıcı - Hızlı Filtre")
        self.resize(1000, 750)
        
        self.bist30 = ["AKBNK", "ALARK", "ARCLK", "ASELS", "ASTOR", "BIMAS", "EKGYO", "ENKAI", "EREGL", "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KOZAA", "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TAVHL", "TCELL", "THYAO", "TOASO", "TUPRS"]
        self.bist_tum = sorted(list(set(self.bist30 + [
            "A1CAP", "ACSEL", "ADEL", "ADESE", "ADGYO", "AEFES", "AFYON", "AGESA", "AGHOL", "AGROT", "AHGAZ", "AKCNS", "AKENR", "AKFGY", "AKFYE", "AKGRT", "AKMGY", "AKSA", "AKSEN", "AKSGY", "AKSUE", "AKTVY", "ALBRK", "ALCAR", "ALCTL", "ALFAS", "ALKA", "ALKIM", "ALMAD", "ALTNY", "ALVES", "ANELE", "ANGEN", "ANHYT", "ANSGR", "ANTEK", "ARASE", "ARCLK", "ARDYZ", "ARENA", "ARSAN", "ARTMS", "ASGYO", "ASHOL", "ASURA", "ASUZU", "ATAGY", "ATAKP", "ATATP", "ATEKS", "ATLAS", "ATSYH", "AVGYO", "AVHOL", "AVOD", "AVTUR", "AYDEM", "AYEN", "AYES", "AYGAZ", "AZTEK", "BAGFS", "BAKAB", "BALAT", "BANVT", "BARMA", "BASCM", "BASGZ", "BAYRK", "BEBEK", "BEGYO", "BERA", "BEYAZ", "BFREN", "BIENP", "BIGCH", "BIPAN", "BIZIM", "BJKAS", "BLCYT", "BMSCH", "BMSTL", "BNASL", "BOBET", "BORLS", "BORSK", "BOSSA", "BRISA", "BRKO", "BRKSN", "BRMEN", "BRKVY", "BRLSM", "BRYAT", "BSOKE", "BTCIM", "BUCIM", "BURCE", "BURVA", "BVSAN", "BYDNR", "CANTE", "CASA", "CATES", "CCOLA", "CELHA", "CEMAS", "CEMTS", "CENIT", "CEOEM", "CIMSA", "CLEBI", "CONSE", "COSMO", "CRDFA", "CRFSA", "CUSAN", "CVKMD", "CWENE", "DAGHL", "DAGI", "DAPGM", "DARDL", "DGATE", "DGGYO", "DGNMO", "DIRIT", "DITAS", "DMSAS", "DNISI", "DOAS", "DOCO", "DOGUB", "DOHOL", "DOKTA", "DURDO", "DYOBY", "DZGYO", "EBEBK", "ECILC", "ECZYT", "EDATA", "EDIP", "EGEEN", "EGEPO", "EGGUB", "EGPRO", "EGSER", "EKGYO", "EKIZ", "EKSUN", "ELITE", "EMKEL", "ENERY", "ENJSA", "ENKAI", "ENTRA", "ERBOS", "ERCB", "EREGL", "ERSU", "ESCOM", "ESEN", "ETILR", "EUPWR", "EUREN", "EUHOL", "EUYO", "EYGYO", "FADE", "FENER", "FLAP", "FMIZP", "FONET", "FORMT", "FORTE", "FRIGO", "FROTO", "FZLGY", "GARFA", "GEDIK", "GEDZA", "GENIL", "GENTS", "GEREL", "GESAN", "GIPTA", "GLBMD", "GLCVY", "GLRYH", "GLYHO", "GMTAS", "GOKNR", "GOLTS", "GOODY", "GOZDE", "GRNYO", "GRSEL", "GSDDE", "GSDHO", "GSRAY", "GUBRF", "GWIND", "GZNMI", "HALKB", "HATEK", "HDFGS", "HEDEF", "HEKTS", "HKTM", "HLGYO", "HTTBT", "HUBVC", "HUNER", "HURGZ", "ICBCT", "IDGYO", "IEYHO", "IHEVA", "IHGZT", "IHLAS", "IHLGM", "IHYAY", "IMASM", "INDES", "INFO", "INGRM", "INTEM", "IPEKE", "ISATR", "ISBTR", "ISCTR", "ISFIN", "ISGSY", "ISGYO", "ISMEN", "ISSEN", "ISYAT", "IZENR", "IZFAS", "IZMDC", "JANTS", "KAPLM", "KAREL", "KARSN", "KARTN", "KARYE", "KATMR", "KAYSE", "KCAER", "KCHOL", "KFEIN", "KGYO", "KIMMR", "KLGYO", "KLMSN", "KLNMA", "KLRMP", "KLSYN", "KLYAS", "KMEPU", "KNFRT", "KOCAER", "KOCMT", "KONKA", "KONTR", "KONYA", "KORDS", "KOTON", "KOZAA", "KOZAL", "KPOWR", "KRGYO", "KRONT", "KRPLS", "KRSTL", "KRTEK", "KSTUR", "KTSKR", "KUTPO", "KUVVA", "KUYAS", "KZBGY", "KZGYO", "LIDER", "LIDFA", "LINK", "LMKDC", "LOGO", "LRSHO", "LUKSK", "MAALT", "MAGEN", "MAKIM", "MAKTK", "MANAS", "MARKA", "MARTI", "MAVI", "MEDTR", "MEGAP", "MEGMT", "MEPET", "MERCN", "MERIT", "MERKO", "METRO", "METUR", "MHRGY", "MIATK", "MIPAZ", "MMCAS", "MNDRS", "MNDTR", "MOBTL", "MPARK", "MRGYO", "MRSHL", "MSGYO", "MTRKS", "MTRYO", "MZHLD", "NATEN", "NETAS", "NIBAS", "NTGAZ", "NUGYO", "NUHCM", "OBAMS", "OBASE", "ODAS", "ONCSM", "ORCAY", "ORGE", "OTKAR", "OYAKC", "OYAYO", "OYLUM", "OYYAT", "OZGYO", "OZKGY", "OZRDN", "OZSUB", "PAGYO", "PAMEL", "PAPIL", "PARSN", "PASEU", "PATEK", "PCILT", "PEGYO", "PEKGY", "PENTA", "PETKM", "PETUN", "PGSUS", "PINSU", "PKART", "PKENT", "PLTUR", "PNLSN", "PNSUT", "POLHO", "POLTK", "PRKAB", "PRKME", "PRZMA", "PSDTC", "PSGYO", "QUAGR", "RALYH", "RAYSG", "REEDR", "RNPOL", "RODRG", "RTALB", "RUBNS", "RYGYO", "RYSAS", "SAFKR", "SAHOL", "SAMAT", "SANEL", "SANFO", "SANKO", "SARKY", "SARTN", "SASA", "SAYAS", "SDTTR", "SEGYO", "SEKFK", "SEKUR", "SELGD", "SELVA", "SEYKM", "SILVR", "SISE", "SKBNK", "SKTAS", "SMART", "SMRTG", "SNGYO", "SNICA", "SNKPA", "SOKM", "SONME", "SRVGY", "SUMAS", "SUNTK", "SURGY", "TABGD", "TARKM", "TATEN", "TATGD", "TAVHL", "TBORG", "TCELL", "TDGYO", "TEKTU", "TERA", "TETMT", "TEZOL", "TGSAS", "THYAO", "TKFEN", "TKNSA", "TLMAN", "TMPOL", "TMSN", "TOASO", "TRCAS", "TRGYO", "TRILC", "TSKB", "TSPOR", "TTKOM", "TTRAK", "TUCLK", "TUKAS", "TUPRS", "TUREX", "TURSG", "UFUK", "ULAS", "ULKER", "ULLY", "ULUFA", "ULUSE", "ULUUN", "UMPAS", "UNMAŞ", "USAK", "VAKBN", "VAKFN", "VAKKO", "VANGD", "VBTYZ", "VERTU", "VERUS", "VESBE", "VESTL", "VKGYO", "VKING", "YAPRK", "YATAS", "YAYLA", "YEOTK", "YESIL", "YGGYO", "YGYO", "YKBNK", "YKSLN", "YONGA", "YOTAS", "YUNSA", "YYLGD", "ZEDUR", "ZOREN", "ZRGYO"
        ])))

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
        
        # YENİ: RSI FİLTRE BUTONU
        self.btn_rsi_filter = QPushButton("📉 RSI < 35 Filtrele")
        self.btn_rsi_filter.setCheckable(True) # Basılı kalma özelliği
        self.btn_rsi_filter.clicked.connect(self.apply_rsi_filter)
        self.btn_rsi_filter.setStyleSheet("QPushButton:checked { background-color: #c8e6c9; font-weight: bold; }")

        self.search = QLineEdit(); self.search.setPlaceholderText("Hisse Ara...")
        self.search.textChanged.connect(self.apply_text_filter)
        
        nav.addWidget(self.e_sel)
        nav.addWidget(self.p_sel)
        nav.addWidget(self.btn_run)
        nav.addWidget(self.btn_rsi_filter) # Navigasyona eklendi
        nav.addStretch()
        nav.addWidget(self.search)
        layout.addLayout(nav)

        self.table = QTableWidget(); self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Hisse", "Fiyat", "Değişim %", "RSI"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        self.status = QLabel("Hazır.")
        layout.addWidget(self.status)

    def apply_text_filter(self):
        # Arama kutusu değiştiğinde filtreyi güncelle
        self.run_all_filters()

    def apply_rsi_filter(self):
        # Butona basıldığında filtreyi güncelle
        self.run_all_filters()

    def run_all_filters(self):
        """Metin araması ve RSI filtresini aynı anda uygular."""
        search_txt = self.search.text().upper()
        rsi_only = self.btn_rsi_filter.isChecked()

        for i in range(self.table.rowCount()):
            hisse_adi = self.table.item(i, 0).text()
            try:
                rsi_val = float(self.table.item(i, 3).text())
            except:
                rsi_val = 100

            # Filtreleme mantığı
            match_text = search_txt in hisse_adi
            match_rsi = (rsi_val < 35) if rsi_only else True

            self.table.setRowHidden(i, not (match_text and match_rsi))

    def start_scan(self):
        self.table.setRowCount(0); self.table.setSortingEnabled(False)
        self.btn_run.setEnabled(False)
        self.btn_rsi_filter.setChecked(False) # Tarama başında filtreyi sıfırla
        
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

    def finish_scan(self, count):
        self.table.setSortingEnabled(True)
        self.btn_run.setEnabled(True)
        self.status.setText(f"Tarama Bitti: {count} hisse listelendi.")

    def add_row(self, d):
        r = self.table.rowCount(); self.table.insertRow(r)
        mapping = ["hisse", "fiyat", "degisim", "rsi"]
        
        for i, k in enumerate(mapping):
            item = QTableWidgetItem()
            val = d[k]
            
            if isinstance(val, (int, float)):
                item.setData(Qt.ItemDataRole.DisplayRole, val)
            else:
                item.setData(Qt.ItemDataRole.DisplayRole, str(val))

            if k == "degisim":
                if val > 0: item.setForeground(QBrush(QColor("#2e7d32")))
                elif val < 0: item.setForeground(QBrush(QColor("#c62828")))
            
            if k == "rsi":
                if val > 70: item.setBackground(QBrush(QColor("#ffcdd2")))
                elif val < 30: item.setBackground(QBrush(QColor("#c8e6c9")))

            self.table.setItem(r, i, item)

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion")
    win = BorsaUygulamasi(); win.show(); sys.exit(app.exec())
