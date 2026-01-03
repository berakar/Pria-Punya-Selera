"""
BPJS REAL AUTOMATION - APLIKASI UTAMA
Aplikasi utama untuk otomatisasi REAL setelah login manual
"""

import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.metrics import dp
import csv
import os
import traceback
from datetime import datetime

# Impor modul kita
from config import APP_NAME, SIPP_URL, DPT_URL, LAPAK_URL, CSV_FOLDER
from logger import log_info, log_error, log_warning
from validator import validate_kpj_list
from csv_handler import csv_handler
from automation import process_kpj_list, get_engine_stats, reset_engine

# Impor UI builder
try:
    from ui_builder import UIBuilder
    HAS_UI_BUILDER = True
except:
    HAS_UI_BUILDER = False

class BPJSRealAutomationApp(App):
    """Aplikasi Otomatisasi REAL"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = APP_NAME + " - MODE REAL"
        
        # Status pemrosesan
        self.is_processing = False
        self.current_batch = []
        self.results = []
        self.current_index = 0
        self.total_kpj = 0
        
        # Referensi UI
        self.kpj_input = None
        self.status_label = None
        self.progress_bar = None
        self.progress_label = None
        self.start_button = None
        self.stop_button = None
        self.export_button = None
        self.log_panel = None
        
        # Untuk debouncing progress update
        self._progress_update_scheduled = None
        
        # Batas maksimum baris log
        self.MAX_LOG_LINES = 1000
    
    def build(self):
        """Bangun UI"""
        Window.size = (dp(400), dp(800))
        Window.minimum_width = dp(350)
        Window.minimum_height = dp(600)
        
        # Buat UI sederhana jika ui_builder tidak ada
        if not HAS_UI_BUILDER:
            return self.build_simple_ui()
        
        # Bangun dengan UIBuilder
        return UIBuilder.build_main_ui(self)
    
    def build_simple_ui(self):
        """Bangun UI sederhana manual"""
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.textinput import TextInput
        from kivy.uix.progressbar import ProgressBar
        from kivy.uix.scrollview import ScrollView
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Judul
        title = Label(
            text='[b]🚀 OTOMATISASI BPJS REAL[/b]',
            markup=True,
            font_size='24sp',
            size_hint_y=0.1
        )
        layout.add_widget(title)
        
        # Info URL - DIEDIT ANDA
        url_info = Label(
            text=f'URL Target: {SIPP_URL}',
            font_size='12sp',
            size_hint_y=0.05
        )
        layout.add_widget(url_info)
        
        # Instruksi
        instructions = Label(
            text='[b]INSTRUKSI:[/b]\n1. Buka browser di HP\n2. Login ke BPJS manual\n3. Kembali ke aplikasi ini\n4. Masukkan KPJ di bawah',
            markup=True,
            size_hint_y=0.15
        )
        layout.add_widget(instructions)
        
        # Input KPJ
        self.kpj_input = TextInput(
            hint_text='Masukkan KPJ (satu per baris)\nContoh:\n12033062238\n12033062246\n12033062253',
            multiline=True,
            size_hint_y=0.25
        )
        layout.add_widget(self.kpj_input)
        
        # Status
        self.status_label = Label(
            text='Status: Siap\nPastikan sudah login manual di browser',
            size_hint_y=0.15
        )
        layout.add_widget(self.status_label)
        
        # Progress
        self.progress_bar = ProgressBar(max=100, size_hint_y=0.05)
        layout.add_widget(self.progress_bar)
        
        self.progress_label = Label(
            text='Progress: 0/0',
            size_hint_y=0.05
        )
        layout.add_widget(self.progress_label)
        
        # Tombol
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        
        self.start_button = Button(
            text='🚀 MULAI OTOMATISASI REAL',
            background_color=(0, 0.7, 0, 1)
        )
        self.start_button.bind(on_press=self.start_real_processing)
        
        self.stop_button = Button(
            text='⏹️ BERHENTI',
            background_color=(0.9, 0.2, 0.2, 1),
            disabled=True
        )
        self.stop_button.bind(on_press=self.stop_processing)
        
        self.export_button = Button(
            text='💾 EKSPOR CSV',
            background_color=(0.2, 0.5, 0.8, 1)
        )
        self.export_button.bind(on_press=self.export_results)
        
        btn_layout.add_widget(self.start_button)
        btn_layout.add_widget(self.stop_button)
        btn_layout.add_widget(self.export_button)
        
        layout.add_widget(btn_layout)
        
        # Area log
        scroll = ScrollView(size_hint_y=0.2)
        self.log_panel = Label(
            text='Log akan muncul di sini...',
            size_hint_y=None,
            height=dp(200)
        )
        self.log_panel.bind(size=self.log_panel.setter('text_size'))
        scroll.add_widget(self.log_panel)
        layout.add_widget(scroll)
        
        return layout
    
    def add_log(self, message):
        """Tambahkan pesan log dengan batas maksimum baris"""
        if hasattr(self, 'log_panel'):
            current = self.log_panel.text
            
            # Batasi jumlah baris log
            lines = current.split('\n')
            if len(lines) > self.MAX_LOG_LINES:
                # Simpan 500 baris terakhir
                lines = lines[-500:]
                current = '\n'.join(lines)
                self.add_log("⚠️ Log dipotong untuk menghemat memori...")
            
            self.log_panel.text = f"{message}\n{current}"
        print(f"[APLIKASI] {message}")
    
    @mainthread
    def update_status(self, message):
        """Perbarui label status (thread-safe)"""
        if hasattr(self, 'status_label'):
            self.status_label.text = f"Status: {message}"
        self.add_log(message)
    
    def update_progress(self, current, total, kpj=None):
        """Perbarui progress dengan debouncing"""
        # Batalkan update sebelumnya jika belum dieksekusi
        if self._progress_update_scheduled:
            self._progress_update_scheduled.cancel()
        
        # Jadwalkan update baru dengan debouncing
        self._progress_update_scheduled = Clock.schedule_once(
            lambda dt: self._do_progress_update(current, total, kpj), 0.1
        )
    
    @mainthread
    def _do_progress_update(self, current, total, kpj=None):
        """Eksekusi pembaruan progress (thread-safe)"""
        if hasattr(self, 'progress_bar'):
            progress = (current / total * 100) if total > 0 else 0
            self.progress_bar.value = progress
            self.progress_label.text = f"Progress: {current}/{total}"
        
        if kpj:
            self.update_status(f"Memproses: {kpj} ({current}/{total})")
    
    def start_real_processing(self, instance):
        """Mulai pemrosesan otomatisasi REAL"""
        if self.is_processing:
            self.add_log("⚠️ Pemrosesan sudah berjalan")
            return
        
        # Dapatkan daftar KPJ dengan validasi lebih ketat
        input_text = self.kpj_input.text.strip()
        
        # Validasi input lebih detail
        lines = [line.strip() for line in input_text.split('\n')]
        valid_lines = [line for line in lines if line and not line.isspace()]
        
        if not valid_lines:
            self.update_status("❌ Error: Input KPJ kosong atau hanya berisi spasi!")
            return
        
        # Parsing dan validasi
        raw_kpjs = [k for k in valid_lines if k]
        valid_kpjs, invalid_kpjs = validate_kpj_list(raw_kpjs)
        
        if invalid_kpjs:
            self.add_log(f"⚠️ {len(invalid_kpjs)} KPJ tidak valid")
            for inv in invalid_kpjs[:5]:  # Tampilkan maksimal 5 error
                self.add_log(f"  - {inv['kpj']}: {inv['error']}")
            if len(invalid_kpjs) > 5:
                self.add_log(f"  ... dan {len(invalid_kpjs) - 5} error lainnya")
        
        if not valid_kpjs:
            self.update_status("❌ Error: Tidak ada KPJ yang valid")
            return
        
        # Perbarui UI
        self.is_processing = True
        self.current_batch = valid_kpjs
        self.total_kpj = len(valid_kpjs)
        self.current_index = 0
        self.results = []
        
        self.start_button.disabled = True
        self.stop_button.disabled = False
        self.export_button.disabled = True
        
        self.update_status(f"🚀 Memulai otomatisasi REAL: {self.total_kpj} KPJ")
        self.add_log(f"✅ KPJ Valid: {len(valid_kpjs)}, Tidak Valid: {len(invalid_kpjs)}")
        
        # Mulai pemrosesan dengan callback
        Clock.schedule_once(lambda dt: self._process_batch_with_callback(), 0.5)
    
    def _process_batch_with_callback(self):
        """Proses batch dengan callback progress"""
        def progress_callback(progress):
            # Kirim update progress ke main thread
            Clock.schedule_once(lambda dt: self._handle_progress(progress), 0)
        
        # Jalankan batch processing
        try:
            batch_results = process_kpj_list(self.current_batch, progress_callback)
            
            # Tambahkan ke CSV handler
            csv_handler.add_batch(batch_results)
            self.results = batch_results
            
            # Kosongkan batch untuk menghemat memori
            self.current_batch = []
            
            # Perbarui UI setelah selesai
            Clock.schedule_once(lambda dt: self._processing_complete(), 0)
            
        except Exception as e:
            # Tangkap error detail untuk debugging
            error_detail = traceback.format_exc()
            Clock.schedule_once(
                lambda dt: self._processing_error(f"{str(e)}\n\nDetail:\n{error_detail}"), 
                0
            )
    
    @mainthread
    def _handle_progress(self, progress):
        """Tangani pembaruan progress (thread-safe)"""
        current = progress.get("current", 0)
        total = progress.get("total", self.total_kpj)
        kpj = progress.get("kpj", "")
        status = progress.get("status", "")
        
        if status == "processing":
            self.current_index = current
            self.update_progress(current, total, kpj)
            self.add_log(f"Memproses: {kpj}")
        elif status == "completed":
            result = progress.get("result", {})
            if result.get("status") in ["success", "completed"]:
                self.add_log(f"✅ {kpj}: Berhasil")
            else:
                error_msg = result.get('error', 'Tidak diketahui')
                self.add_log(f"❌ {kpj}: Gagal - {error_msg}")
    
    @mainthread
    def _processing_complete(self):
        """Tangani penyelesaian pemrosesan (thread-safe)"""
        self.is_processing = False
        
        # Hitung hasil
        success_count = len([r for r in self.results if r.get("status") in ["success", "completed"]])
        failed_count = len(self.results) - success_count
        
        # Perbarui UI
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.export_button.disabled = False
        
        self.update_status(f"✅ Pemrosesan selesai! Berhasil: {success_count}, Gagal: {failed_count}")
        self.add_log(f"=== SELESAI ===")
        self.add_log(f"Total diproses: {len(self.results)}")
        self.add_log(f"Berhasil: {success_count}")
        self.add_log(f"Gagal: {failed_count}")
        
        # Ekspor otomatis hasil
        Clock.schedule_once(lambda dt: self.export_results(auto=True), 1)
    
    @mainthread
    def _processing_error(self, error_message):
        """Tangani error pemrosesan (thread-safe)"""
        self.is_processing = False
        
        # Perbarui UI
        self.start_button.disabled = False
        self.stop_button.disabled = True
        
        # Tampilkan error yang lebih informatif
        self.update_status("❌ Error pemrosesan (lihat log)")
        self.add_log("❌❌❌ ERROR PEMROSESAN ❌❌❌")
        self.add_log(error_message)
        self.add_log("❌❌❌===================❌❌❌")
    
    def stop_processing(self, instance):
        """Hentikan pemrosesan"""
        if not self.is_processing:
            return
        
        self.is_processing = False
        
        # Reset engine
        try:
            reset_engine()
        except Exception as e:
            self.add_log(f"⚠️ Gagal reset engine: {e}")
        
        # Perbarui UI
        self.start_button.disabled = False
        self.stop_button.disabled = True
        
        self.update_status("⏹️ Pemrosesan dihentikan")
        self.add_log("Pemrosesan dihentikan manual")
    
    def export_results(self, instance=None, auto=False):
        """Ekspor hasil ke CSV dengan robust file handling"""
        try:
            if not csv_handler.has_data():
                if not auto:
                    self.update_status("❌ Tidak ada data untuk diekspor")
                return
            
            # Pastikan folder exist
            if not os.path.exists(CSV_FOLDER):
                os.makedirs(CSV_FOLDER)
                self.add_log(f"📁 Folder dibuat: {CSV_FOLDER}")
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            counter = 1
            base_filename = f"hasil_real_{timestamp}"
            filename = f"{base_filename}.csv"
            filepath = os.path.join(CSV_FOLDER, filename)
            
            # Hindari overwrite file yang sudah ada
            while os.path.exists(filepath):
                filename = f"{base_filename}_{counter}.csv"
                filepath = os.path.join(CSV_FOLDER, filename)
                counter += 1
                if counter > 100:
                    # Fallback: tambah timestamp lebih detail
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                    filename = f"hasil_real_{timestamp}.csv"
                    filepath = os.path.join(CSV_FOLDER, filename)
                    break
            
            # Ekspor data
            export_count = csv_handler.export_to_csv(filepath)
            
            # Perbarui UI
            self.update_status(f"💾 Data berhasil diekspor: {export_count} records")
            self.add_log(f"📄 File: {filename}")
            self.add_log(f"📁 Lokasi: {CSV_FOLDER}")
            
            if auto:
                self.add_log("(Ekspor otomatis setelah pemrosesan selesai)")
            
            # Bersihkan data setelah diekspor (optional)
            # csv_handler.clear_data()
            
        except PermissionError:
            error_msg = "❌ Gagal menulis file: Akses ditolak. Tutup file Excel jika terbuka."
            self.update_status(error_msg)
            self.add_log(error_msg)
        except Exception as e:
            error_msg = f"❌ Error ekspor: {str(e)}"
            self.update_status(error_msg)
            self.add_log(error_msg)
            self.add_log(f"Detail: {traceback.format_exc()}")
    
    def on_stop(self):
        """Aplikasi ditutup - cleanup resources"""
        if self.is_processing:
            self.stop_processing(None)
        
        # Simpan data yang tersisa
        if csv_handler.has_data():
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"hasil_real_autosave_{timestamp}.csv"
                filepath = os.path.join(CSV_FOLDER, filename)
                
                # Pastikan folder ada
                if not os.path.exists(CSV_FOLDER):
                    os.makedirs(CSV_FOLDER)
                
                export_count = csv_handler.export_to_csv(filepath)
                print(f"[APLIKASI] Data tersimpan otomatis: {export_count} records ke {filename}")
                
                # Clear data setelah disimpan
                csv_handler.clear_data()
                
            except Exception as e:
                print(f"[APLIKASI] Gagal simpan otomatis: {e}")
        
        # Reset engine jika ada
        try:
            reset_engine()
        except Exception as e:
            print(f"[APLIKASI] Gagal reset engine saat exit: {e}")
        
        # Tutup window
        try:
            Window.close()
        except:
            pass
        
        # Clear cache UI
        self.kpj_input = None
        self.status_label = None
        self.progress_bar = None
        self.log_panel = None

def main():
    """Titik masuk utama"""
    try:
        log_info(f"Memulai {APP_NAME} - MODE REAL")
        
        # Buat folder CSV jika tidak ada
        if not os.path.exists(CSV_FOLDER):
            os.makedirs(CSV_FOLDER)
            log_info(f"Folder CSV dibuat: {CSV_FOLDER}")
        
        # Validasi folder writable
        try:
            test_file = os.path.join(CSV_FOLDER, "test_write.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            log_info(f"Folder {CSV_FOLDER} writable")
        except Exception as e:
            log_error(f"Folder {CSV_FOLDER} tidak writable: {e}")
            raise
        
        # Mulai aplikasi
        app = BPJSRealAutomationApp()
        app.run()
        
    except Exception as e:
        log_error(f"Error fatal: {e}")
        log_error(traceback.format_exc())
        raise

if __name__ == '__main__':
    main()