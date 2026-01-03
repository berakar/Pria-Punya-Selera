"""
BPJS AUTOMATION - REAL AUTOMATION ENGINE
Untuk automate browser setelah login manual ke BPJS
"""

import time
import json
from datetime import datetime
from config import (
    SIPP_URL, DPT_URL, LAPAK_URL,
    MAX_RETRIES, RETRY_DELAY
)
from logger import log_info, log_warning, log_error
from validator import validate_kpj

try:
    from web_automator import web_automator
    HAS_WEB_AUTOMATOR = True
except ImportError:
    HAS_WEB_AUTOMATOR = False
    log_error("❌ web_automator.py tidak ditemukan!")

class RealAutomationEngine:
    """Engine untuk REAL automation setelah login manual"""
    
    def __init__(self):
        self.current_state = "IDLE"
        self.stats = {
            "total_processed": 0,
            "successful": 0,
            "skipped": 0,
            "failed": 0,
            "start_time": None,
            "end_time": None
        }
        self.current_kpj = None
        
        # Initialize web automator
        if HAS_WEB_AUTOMATOR:
            try:
                web_automator.init_webview()
                log_info("✅ Web automator siap untuk REAL automation")
            except Exception as e:
                log_error(f"❌ Gagal init web automator: {str(e)}")
    
    def _change_state(self, new_state):
        """Update state mesin"""
        self.current_state = new_state
        log_info(f"Status: {new_state}")
    
    def validate_and_prepare(self, kpj):
        """Validasi KPJ dan siapkan proses"""
        is_valid, message = validate_kpj(kpj)
        if not is_valid:
            return False, message
        
        if not HAS_WEB_AUTOMATOR:
            return False, "Web automator tidak tersedia"
        
        return True, "KPJ valid"
    
    def process_sipp_real(self, kpj):
        """Proses REAL automation untuk SIPP"""
        log_info(f"🔧 Memulai REAL automation untuk KPJ: {kpj}")
        
        result = {
            "kpj": kpj,
            "status": "processing",
            "tab": "SIPP",
            "start_time": datetime.now().strftime('%H:%M:%S')
        }
        
        def automation_callback(success, data):
            if success:
                result.update({
                    "status": "success",
                    "data": data,
                    "end_time": datetime.now().strftime('%H:%M:%S'),
                    "message": "Data berhasil diambil dari SIPP"
                })
                log_info(f"✅ Berhasil ambil data untuk KPJ: {kpj}")
            else:
                result.update({
                    "status": "failed",
                    "error": data,
                    "end_time": datetime.now().strftime('%H:%M:%S'),
                    "message": f"Gagal: {data}"
                })
                log_error(f"❌ Gagal untuk KPJ {kpj}: {data}")
        
        # Jalankan REAL automation
        try:
            web_automator.simulate_sipp_automation(kpj, automation_callback)
            
            # Tunggu hasil maksimal 45 detik
            timeout = 45
            start_wait = time.time()
            
            while result["status"] == "processing" and (time.time() - start_wait) < timeout:
                time.sleep(0.5)
            
            if result["status"] == "processing":
                result.update({
                    "status": "timeout",
                    "error": f"Timeout {timeout} detik",
                    "end_time": datetime.now().strftime('%H:%M:%S')
                })
                log_warning(f"⏱️ Timeout untuk KPJ: {kpj}")
            
        except Exception as e:
            result.update({
                "status": "error",
                "error": str(e),
                "end_time": datetime.now().strftime('%H:%M:%S')
            })
            log_error(f"🔥 Error processing KPJ {kpj}: {str(e)}")
        
        return result
    
    def process_single_kpj(self, kpj):
        """Process satu KPJ dengan REAL automation"""
        self.current_kpj = kpj
        self._change_state(f"PROCESSING_{kpj}")
        
        start_time = datetime.now()
        self.stats["start_time"] = start_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Validasi KPJ
        is_valid, message = self.validate_and_prepare(kpj)
        if not is_valid:
            error_result = {
                "kpj": kpj,
                "error": message,
                "status": "invalid",
                "processing_time": "0s",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.stats["failed"] += 1
            return error_result
        
        # Proses dengan retry logic
        final_result = None
        for attempt in range(MAX_RETRIES):
            try:
                log_info(f"Attempt {attempt + 1}/{MAX_RETRIES} untuk KPJ: {kpj}")
                
                # REAL automation untuk SIPP
                sipp_result = self.process_sipp_real(kpj)
                
                if sipp_result["status"] not in ["success", "completed"]:
                    if attempt < MAX_RETRIES - 1:
                        log_info(f"Retry {attempt + 1} dalam {RETRY_DELAY} detik...")
                        time.sleep(RETRY_DELAY)
                        continue
                    else:
                        final_result = sipp_result
                        self.stats["failed"] += 1
                        break
                
                # Jika berhasil
                final_result = sipp_result
                final_result["overall_status"] = "completed"
                final_result["process_attempt"] = attempt + 1
                
                self.stats["successful"] += 1
                break
                
            except Exception as e:
                log_error(f"Attempt {attempt + 1} error: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    final_result = {
                        "kpj": kpj,
                        "error": str(e),
                        "status": "failed",
                        "retry_attempts": attempt + 1
                    }
                    self.stats["failed"] += 1
        
        # Hitung waktu proses
        end_time = datetime.now()
        processing_duration = (end_time - start_time).total_seconds()
        
        if final_result:
            final_result.update({
                "processing_start": start_time.strftime('%H:%M:%S'),
                "processing_end": end_time.strftime('%H:%M:%S'),
                "processing_duration_seconds": round(processing_duration, 2),
                "batch_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        self.stats["total_processed"] += 1
        self.stats["end_time"] = end_time.strftime('%Y-%m-%d %H:%M:%S')
        
        log_info(f"✅ Selesai KPJ {kpj} dalam {processing_duration:.1f} detik")
        self._change_state("IDLE")
        
        return final_result if final_result else {
            "kpj": kpj,
            "error": "Unknown error",
            "status": "unknown_error"
        }
    
    def process_batch(self, kpj_list, progress_callback=None):
        """Process batch KPJ"""
        total = len(kpj_list)
        results = []
        
        log_info(f"🚀 Memulai REAL batch processing: {total} KPJ")
        self._change_state("BATCH_PROCESSING")
        
        # Reset stats untuk batch baru
        self.stats = {
            "total_processed": 0,
            "successful": 0,
            "skipped": 0,
            "failed": 0,
            "start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": None,
            "total_kpj": total
        }
        
        for index, kpj in enumerate(kpj_list, 1):
            # Update progress
            progress = (index / total) * 100
            
            if progress_callback:
                progress_callback({
                    "current": index,
                    "total": total,
                    "percent": progress,
                    "kpj": kpj,
                    "status": "processing"
                })
            
            log_info(f"📊 Progress: {index}/{total} ({progress:.1f}%) - KPJ: {kpj}")
            
            # Process KPJ
            result = self.process_single_kpj(kpj)
            result["sequence"] = index
            result["total_in_batch"] = total
            
            results.append(result)
            
            if progress_callback:
                progress_callback({
                    "current": index,
                    "total": total,
                    "percent": progress,
                    "kpj": kpj,
                    "status": "completed",
                    "result": result
                })
            
            # Delay antar KPJ
            if index < total:
                time.sleep(1.0)
        
        # Batch selesai
        self._change_state("BATCH_COMPLETED")
        self.stats["end_time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        success_count = len([r for r in results if r.get("status") in ["success", "completed"]])
        success_rate = (success_count / total * 100) if total > 0 else 0
        
        batch_summary = {
            "total_kpj": total,
            "successful": success_count,
            "failed": total - success_count,
            "success_rate": f"{success_rate:.1f}%",
            "start_time": self.stats["start_time"],
            "end_time": self.stats["end_time"],
            "duration": f"{(datetime.strptime(self.stats['end_time'], '%Y-%m-%d %H:%M:%S') - datetime.strptime(self.stats['start_time'], '%Y-%m-%d %H:%M:%S')).total_seconds():.1f}s"
        }
        
        log_info(f"🎉 Batch selesai! Summary: {batch_summary}")
        
        # Tambah summary ke setiap result
        for result in results:
            result["batch_summary"] = batch_summary
        
        return results
    
    def get_stats(self):
        """Get statistics"""
        return self.stats.copy()

# Global instance
real_engine = RealAutomationEngine()

# Convenience functions
def process_kpj(kpj):
    return real_engine.process_single_kpj(kpj)

def process_kpj_list(kpj_list, callback=None):
    return real_engine.process_batch(kpj_list, callback)

def get_engine_stats():
    return real_engine.get_stats()

def reset_engine():
    global real_engine
    real_engine = RealAutomationEngine()
    return "Engine direset"