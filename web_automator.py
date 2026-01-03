"""
BPJS REAL AUTOMATION - Web Automator
Untuk automate browser setelah login manual
"""

import time
import json
from datetime import datetime
from android.runnable import run_on_ui_thread
from jnius import autoclass, PythonJavaClass, java_method
from logger import log_info, log_error, log_warning

# Android WebView classes
WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
WebSettings = autoclass('android.webkit.WebSettings')
LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
PythonActivity = autoclass('org.kivy.android.PythonActivity')

class WebAutomator:
    """Real web automation engine"""
    
    def __init__(self):
        self.webview = None
        self.callbacks = {}
        self.is_ready = False
        self.current_url = ""
        
    @run_on_ui_thread
    def init_webview(self):
        """Initialize hidden WebView"""
        try:
            activity = PythonActivity.mActivity
            
            # Create WebView
            self.webview = WebView(activity)
            
            # Configure WebView
            settings = self.webview.getSettings()
            settings.setJavaScriptEnabled(True)
            settings.setDomStorageEnabled(True)
            settings.setDatabaseEnabled(True)
            settings.setAllowFileAccess(True)
            settings.setAllowContentAccess(True)
            
            # Set WebViewClient
            self.webview.setWebViewClient(AutomatorWebViewClient(self))
            
            # Add JavaScript interface
            self.webview.addJavascriptInterface(
                JSCallbackInterface(self), 
                "BPJSBridge"
            )
            
            # Make it tiny and hidden (1x1 pixel)
            params = LayoutParams(1, 1)
            self.webview.setLayoutParams(params)
            self.webview.setVisibility(4)  # INVISIBLE
            
            # Add to activity
            activity.addContentView(self.webview, params)
            
            self.is_ready = True
            log_info("✅ WebView initialized (hidden)")
            return True
            
        except Exception as e:
            log_error(f"❌ Failed to init WebView: {str(e)}")
            return False
    
    @run_on_ui_thread
    def load_url(self, url):
        """Load URL ke WebView"""
        if self.webview and self.is_ready:
            self.webview.loadUrl(url)
            self.current_url = url
            log_info(f"🌐 Loading URL: {url}")
    
    @run_on_ui_thread
    def execute_javascript(self, js_code, callback=None):
        """Execute JavaScript di WebView"""
        if not self.webview or not self.is_ready:
            log_error("❌ WebView not ready")
            if callback:
                callback(False, "WebView not ready")
            return
        
        # Generate callback ID
        callback_id = None
        if callback:
            callback_id = str(int(time.time() * 1000))
            self.callbacks[callback_id] = callback
            
            # Wrap JS dengan callback handler
            wrapped_js = f"""
            (function() {{
                try {{
                    var result = ({js_code})();
                    BPJSBridge.jsResult('{callback_id}', 'success', JSON.stringify(result));
                }} catch(error) {{
                    BPJSBridge.jsResult('{callback_id}', 'error', error.toString());
                }}
            }})();
            """
            self.webview.evaluateJavascript(wrapped_js, None)
        else:
            # Execute tanpa callback
            self.webview.evaluateJavascript(f"({js_code})();", None)
    
    def handle_js_result(self, callback_id, status, result):
        """Handle JavaScript result dari WebView"""
        callback = self.callbacks.pop(callback_id, None)
        if callback:
            if status == 'success':
                try:
                    data = json.loads(result) if result else None
                    callback(True, data)
                except:
                    callback(True, result)
            else:
                callback(False, result)
    
    def simulate_sipp_automation(self, kpj, callback):
        """
        Automate SIPP setelah login manual
        KPJ: Nomor KPJ yang akan diproses
        callback: Fungsi yang dipanggil setelah selesai
        """
        log_info(f"🤖 Starting SIPP automation for KPJ: {kpj}")
        
        # Step 1: Cari input field untuk KPJ
        find_kpj_field_js = """
        function() {
            console.log('Mencari input field KPJ...');
            
            // Cari semua input fields
            var inputs = document.querySelectorAll('input[type="text"], input:not([type])');
            var kpjFields = [];
            
            for(var i = 0; i < inputs.length; i++) {
                var input = inputs[i];
                var placeholder = (input.placeholder || '').toLowerCase();
                var name = (input.name || '').toLowerCase();
                var id = (input.id || '').toLowerCase();
                var label = (input.parentElement.textContent || '').toLowerCase();
                
                // Cek apakah ini field KPJ
                if(placeholder.includes('kpj') || name.includes('kpj') || 
                   id.includes('kpj') || label.includes('kpj')) {
                    kpjFields.push({
                        element: input,
                        type: 'input',
                        id: input.id,
                        name: input.name,
                        placeholder: input.placeholder
                    });
                }
            }
            
            // Jika tidak ketemu, coba input pertama yang kosong
            if(kpjFields.length === 0) {
                for(var i = 0; i < inputs.length; i++) {
                    if(!inputs[i].value.trim()) {
                        kpjFields.push({
                            element: inputs[i],
                            type: 'input',
                            id: inputs[i].id,
                            name: inputs[i].name,
                            placeholder: inputs[i].placeholder,
                            reason: 'empty_field'
                        });
                        break;
                    }
                }
            }
            
            if(kpjFields.length > 0) {
                return {
                    success: true,
                    fields: kpjFields,
                    totalFields: inputs.length
                };
            }
            
            return {
                success: false,
                error: 'KPJ field not found',
                totalFields: inputs.length
            };
        }
        """
        
        def handle_field_found(success, data):
            if success and data.get('success'):
                fields = data.get('fields', [])
                if fields:
                    # Gunakan field pertama
                    field = fields[0]
                    
                    # Step 2: Isi KPJ ke field
                    fill_kpj_js = f"""
                    function() {{
                        try {{
                            var field = document.querySelector('{field.id ? '#' + field.id : 'input[name="' + field.name + '"]'}');
                            if(field) {{
                                // Isi value
                                field.value = '{kpj}';
                                
                                // Trigger events
                                field.dispatchEvent(new Event('input', {{bubbles: true}}));
                                field.dispatchEvent(new Event('change', {{bubbles: true}}));
                                field.dispatchEvent(new Event('blur', {{bubbles: true}}));
                                
                                console.log('KPJ filled:', field.value);
                                return {{
                                    success: true,
                                    value: field.value,
                                    fieldId: field.id,
                                    fieldName: field.name
                                }};
                            }}
                            return {{success: false, error: 'Field element not found'}};
                        }} catch(e) {{
                            return {{success: false, error: e.message}};
                        }}
                    }}
                    """
                    
                    self.execute_javascript(fill_kpj_js, 
                        lambda s, d: handle_kpj_filled(s, d, kpj, callback))
                else:
                    callback(False, "No KPJ fields found")
            else:
                callback(False, data.get('error', 'Field detection failed'))
        
        self.execute_javascript(find_kpj_field_js, handle_field_found)
    
    def handle_kpj_filled(self, success, data, kpj, callback):
        """Handle setelah KPJ diisi"""
        if success:
            log_info(f"✅ KPJ {kpj} berhasil diisi")
            
            # Tunggu sebentar
            time.sleep(1)
            
            # Step 3: Cari tombol search/cari
            find_search_btn_js = """
            function() {
                // Cari semua button dan submit inputs
                var buttons = document.querySelectorAll('button, input[type="submit"], input[type="button"]');
                var searchButtons = [];
                
                for(var i = 0; i < buttons.length; i++) {
                    var btn = buttons[i];
                    var text = (btn.textContent || btn.value || btn.innerText || '').toLowerCase();
                    var className = (btn.className || '').toLowerCase();
                    var id = (btn.id || '').toLowerCase();
                    
                    // Cek apakah ini tombol search
                    if(text.includes('cari') || text.includes('search') || 
                       text.includes('lihat') || text.includes('find') ||
                       className.includes('cari') || className.includes('search') ||
                       id.includes('cari') || id.includes('search')) {
                        searchButtons.push({
                            element: btn,
                            text: text,
                            id: btn.id,
                            className: btn.className
                        });
                    }
                }
                
                // Jika tidak ketemu, ambil tombol pertama
                if(searchButtons.length === 0 && buttons.length > 0) {
                    searchButtons.push({
                        element: buttons[0],
                        text: buttons[0].textContent || buttons[0].value,
                        id: buttons[0].id,
                        className: buttons[0].className,
                        reason: 'first_button'
                    });
                }
                
                if(searchButtons.length > 0) {
                    return {
                        success: true,
                        buttons: searchButtons,
                        totalButtons: buttons.length
                    };
                }
                
                return {
                    success: false,
                    error: 'Search button not found',
                    totalButtons: buttons.length
                };
            }
            """
            
            def handle_button_found(success, data):
                if success and data.get('success'):
                    buttons = data.get('buttons', [])
                    if buttons:
                        # Gunakan tombol pertama
                        btn = buttons[0]
                        
                        # Step 4: Klik tombol
                        click_button_js = """
                        function() {
                            try {
                                var button = arguments[0];
                                button.click();
                                return {
                                    success: true,
                                    clicked: true,
                                    buttonText: button.textContent || button.value
                                };
                            } catch(e) {
                                return {success: false, error: e.message};
                            }
                        }
                        """
                        
                        # Execute click
                        self.execute_javascript(
                            f"({click_button_js})(document.querySelector('{btn.id ? '#' + btn.id : 'button, input[type=\"submit\"]'}'))",
                            lambda s, d: handle_search_clicked(s, d, kpj, callback)
                        )
                    else:
                        callback(False, "No buttons to click")
                else:
                    callback(False, data.get('error', 'Button not found'))
            
            self.execute_javascript(find_search_btn_js, handle_button_found)
        else:
            callback(False, data.get('error', 'Failed to fill KPJ'))
    
    def handle_search_clicked(self, success, data, kpj, callback):
        """Handle setelah search diklik"""
        if success:
            log_info(f"🔍 Search clicked for KPJ: {kpj}")
            
            # Tunggu hasil loading (3-5 detik)
            time.sleep(3)
            
            # Step 5: Ambil data hasil
            extract_data_js = """
            function() {
                try {
                    // Cari semua tabel di halaman
                    var tables = document.querySelectorAll('table');
                    var allData = [];
                    
                    for(var t = 0; t < tables.length; t++) {
                        var table = tables[t];
                        var rows = table.querySelectorAll('tr');
                        var tableData = [];
                        
                        // Ambil data dari setiap row (maks 20 baris)
                        for(var r = 0; r < Math.min(rows.length, 20); r++) {
                            var cells = rows[r].querySelectorAll('td, th');
                            var rowData = [];
                            
                            for(var c = 0; c < cells.length; c++) {
                                rowData.push({
                                    text: cells[c].textContent.trim(),
                                    className: cells[c].className,
                                    colSpan: cells[c].colSpan,
                                    rowSpan: cells[c].rowSpan
                                });
                            }
                            
                            if(rowData.length > 0) {
                                tableData.push({
                                    rowIndex: r,
                                    cells: rowData,
                                    cellCount: rowData.length
                                });
                            }
                        }
                        
                        if(tableData.length > 0) {
                            allData.push({
                                tableIndex: t,
                                rows: tableData,
                                totalRows: tableData.length
                            });
                        }
                    }
                    
                    // Juga cari data di divs, spans, dll
                    var dataContainers = document.querySelectorAll('.data-table, .result-container, .search-result, [class*="result"], [class*="data"]');
                    var containerData = [];
                    
                    for(var i = 0; i < Math.min(dataContainers.length, 10); i++) {
                        var container = dataContainers[i];
                        containerData.push({
                            element: container.tagName,
                            className: container.className,
                            text: container.textContent.trim().substring(0, 200),
                            children: container.children.length
                        });
                    }
                    
                    // Ambil judul/h1 untuk konteks
                    var pageTitle = document.querySelector('h1, h2, .page-title, .title')?.textContent.trim() || '';
                    
                    return {
                        success: true,
                        tablesFound: allData.length,
                        containersFound: containerData.length,
                        pageTitle: pageTitle,
                        url: window.location.href,
                        timestamp: new Date().toISOString(),
                        tables: allData,
                        containers: containerData
                    };
                    
                } catch(error) {
                    return {
                        success: false,
                        error: error.toString(),
                        url: window.location.href
                    };
                }
            }
            """
            
            self.execute_javascript(extract_data_js, 
                lambda s, d: callback(s, d))
        else:
            callback(False, data.get('error', 'Button click failed'))

# JavaScript Interface untuk callback dari WebView
class JSCallbackInterface(PythonJavaClass):
    __javainterfaces__ = ['org/kivy/android/PythonActivity$JSCallbackInterface']
    
    def __init__(self, automator):
        super().__init__()
        self.automator = automator
    
    @java_method('(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V')
    def jsResult(self, callback_id, status, result):
        self.automator.handle_js_result(callback_id, status, result)

# Custom WebViewClient
class AutomatorWebViewClient(WebViewClient):
    def __init__(self, automator):
        super().__init__()
        self.automator = automator
    
    def onPageStarted(self, view, url, favicon):
        log_info(f"📄 Page loading: {url}")
    
    def onPageFinished(self, view, url):
        log_info(f"✅ Page loaded: {url}")
        self.automator.current_url = url
        
        # Inject monitoring script
        view.evaluateJavascript("""
            console.log('BPJS Automation: Page ready for automation');
            window.bpjsAutomationReady = true;
        """, None)

# Global instance
web_automator = WebAutomator()