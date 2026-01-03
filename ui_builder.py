"""
BPJS AUTOMATION - UI BUILDER
Builds the complete user interface
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.metrics import dp, sp

from ui_components import (
    HeaderLabel, StatusLabel, KPJInput,
    PrimaryButton, SuccessButton, WarningButton, ErrorButton,
    CustomProgressBar, StatsPanel, LogPanel,
    SettingsPopup, ConfirmationPopup
)
from config import APP_NAME, MESSAGES, COLOR_PRIMARY

class UIBuilder:
    """Builds the application UI"""
    
    @staticmethod
    def build_main_ui(app_instance):
        """Build the main application UI"""
        
        # Main container
        main_layout = BoxLayout(
            orientation='vertical',
            padding=[dp(20), dp(20), dp(20), dp(20)],
            spacing=dp(15)
        )
        
        # Header Section
        header = UIBuilder._build_header()
        main_layout.add_widget(header)
        
        # Input Section
        input_section = UIBuilder._build_input_section(app_instance)
        main_layout.add_widget(input_section)
        
        # Status Section
        status_section = UIBuilder._build_status_section(app_instance)
        main_layout.add_widget(status_section)
        
        # Progress Section
        progress_section = UIBuilder._build_progress_section(app_instance)
        main_layout.add_widget(progress_section)
        
        # Control Buttons
        control_section = UIBuilder._build_control_section(app_instance)
        main_layout.add_widget(control_section)
        
        # Statistics Panel
        stats_panel = UIBuilder._build_stats_panel(app_instance)
        main_layout.add_widget(stats_panel)
        
        # Log Panel
        log_panel = UIBuilder._build_log_panel(app_instance)
        main_layout.add_widget(log_panel)
        
        return main_layout
    
    @staticmethod
    def _build_header():
        """Build header section"""
        header_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(60)
        )
        
        header_label = HeaderLabel(
            text=f"[b]{APP_NAME}[/b]",
            size_hint_y=None,
            height=dp(50)
        )
        
        header_layout.add_widget(header_label)
        
        return header_layout
    
    @staticmethod
    def _build_input_section(app_instance):
        """Build input section"""
        input_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(220),
            spacing=dp(10)
        )
        
        # Input label
        input_label = HeaderLabel(
            text="Input KPJ List",
            font_size=sp(18),
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        
        # KPJ input field
        app_instance.kpj_input = KPJInput()
        
        input_layout.add_widget(input_label)
        input_layout.add_widget(app_instance.kpj_input)
        
        return input_layout
    
    @staticmethod
    def _build_status_section(app_instance):
        """Build status display section"""
        status_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120)
        )
        
        app_instance.status_label = StatusLabel(
            text=MESSAGES.get("ready", "Ready to process"),
            size_hint_y=None,
            height=dp(110)
        )
        
        status_layout.add_widget(app_instance.status_label)
        
        return status_layout
    
    @staticmethod
    def _build_progress_section(app_instance):
        """Build progress display section"""
        progress_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80),
            spacing=dp(5)
        )
        
        # Progress bar
        app_instance.progress_bar = CustomProgressBar(
            size_hint_y=None,
            height=dp(30)
        )
        
        # Progress label
        app_instance.progress_label = HeaderLabel(
            text="Progress: 0/0 (0%)",
            font_size=sp(16),
            size_hint_y=None,
            height=dp(30)
        )
        
        progress_layout.add_widget(app_instance.progress_bar)
        progress_layout.add_widget(app_instance.progress_label)
        
        return progress_layout
    
    @staticmethod
    def _build_control_section(app_instance):
        """Build control buttons section"""
        control_layout = GridLayout(
            cols=4,
            rows=1,
            size_hint_y=None,
            height=dp(60),
            spacing=dp(10)
        )
        
        # Start button
        app_instance.start_button = SuccessButton(
            text="🚀 START",
            size_hint_x=0.25
        )
        app_instance.start_button.bind(on_press=app_instance.start_processing)
        
        # Stop button
        app_instance.stop_button = ErrorButton(
            text="⏹️ STOP",
            size_hint_x=0.25,
            disabled=True
        )
        app_instance.stop_button.bind(on_press=app_instance.stop_processing)
        
        # Export button
        app_instance.export_button = PrimaryButton(
            text="💾 EXPORT",
            size_hint_x=0.25
        )
        app_instance.export_button.bind(on_press=app_instance.export_results)
        
        # Settings button
        settings_button = WarningButton(
            text="⚙️ SETTINGS",
            size_hint_x=0.25
        )
        settings_button.bind(on_press=app_instance.open_settings)
        
        control_layout.add_widget(app_instance.start_button)
        control_layout.add_widget(app_instance.stop_button)
        control_layout.add_widget(app_instance.export_button)
        control_layout.add_widget(settings_button)
        
        return control_layout
    
    @staticmethod
    def _build_stats_panel(app_instance):
        """Build statistics panel"""
        app_instance.stats_panel = StatsPanel()
        return app_instance.stats_panel
    
    @staticmethod
    def _build_log_panel(app_instance):
        """Build log panel"""
        log_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(200)
        )
        
        # Log header
        log_header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30)
        )
        
        log_title = HeaderLabel(
            text="Processing Logs",
            font_size=sp(16),
            halign='left',
            size_hint_x=0.7
        )
        
        clear_button = ErrorButton(
            text="Clear Logs",
            size_hint_x=0.3
        )
        clear_button.bind(on_press=app_instance.clear_logs)
        
        log_header.add_widget(log_title)
        log_header.add_widget(clear_button)
        
        # Log display
        app_instance.log_panel = LogPanel()
        
        log_layout.add_widget(log_header)
        log_layout.add_widget(app_instance.log_panel)
        
        return log_layout
    
    @staticmethod
    def create_popup(title, message, buttons=None):
        """Create a popup dialog"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Message
        content.add_widget(Label(
            text=message,
            halign='center',
            valign='middle',
            text_size=(dp(300), None)
        ))
        
        # Buttons
        if buttons:
            button_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))
            for btn_text, btn_callback in buttons:
                btn = PrimaryButton(text=btn_text)
                btn.bind(on_press=btn_callback)
                button_layout.add_widget(btn)
            content.add_widget(button_layout)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.7, 0.5),
            auto_dismiss=False
        )
        
        # Add dismiss button if no buttons provided
        if not buttons:
            dismiss_btn = ErrorButton(text="Close", size_hint_y=None, height=dp(50))
            dismiss_btn.bind(on_press=popup.dismiss)
            content.add_widget(dismiss_btn)
        
        return popup
    
    @staticmethod
    def update_progress_ui(app_instance, current, total, kpj=None):
        """Update progress UI elements"""
        if total > 0:
            percent = (current / total) * 100
            app_instance.progress_bar.value = percent
            app_instance.progress_label.text = f"Progress: {current}/{total} ({percent:.1f}%)"
            
            if kpj:
                app_instance.status_label.text = (
                    f"[b]Processing:[/b]\n"
                    f"KPJ: {kpj}\n"
                    f"Progress: {current}/{total} ({percent:.1f}%)"
                )
    
    @staticmethod
    def update_stats_panel(app_instance, stats):
        """Update statistics panel"""
        if hasattr(app_instance, 'stats_panel'):
            for key, value in stats.items():
                app_instance.stats_panel.update_stat(key, value)
    
    @staticmethod
    def add_log_entry(app_instance, message, level="INFO"):
        """Add entry to log panel"""
        if hasattr(app_instance, 'log_panel'):
            app_instance.log_panel.add_log(message, level)
    
    @staticmethod
    def show_settings_dialog(app_instance):
        """Show settings dialog"""
        settings_popup = SettingsPopup()
        settings_popup.open()
    
    @staticmethod
    def show_confirmation_dialog(title, message, callback):
        """Show confirmation dialog"""
        confirm_popup = ConfirmationPopup(
            title=title,
            message=message,
            confirm_text="Yes",
            cancel_text="No"
        )
        confirm_popup.set_callback(callback)
        confirm_popup.open()
        return confirm_popup
    
    @staticmethod
    def show_message_dialog(title, message):
        """Show message dialog"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical', padding=dp(20))
        content.add_widget(Label(text=message, halign='center'))
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.7, 0.4)
        )
        
        # Add close button
        from ui_components import PrimaryButton
        close_btn = PrimaryButton(text="OK", size_hint_y=None, height=dp(50))
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()
        return popup
    
    @staticmethod
    def disable_controls(app_instance, disable=True):
        """Enable/disable UI controls"""
        if hasattr(app_instance, 'start_button'):
            app_instance.start_button.disabled = disable
        
        if hasattr(app_instance, 'stop_button'):
            app_instance.stop_button.disabled = not disable
        
        if hasattr(app_instance, 'export_button'):
            app_instance.export_button.disabled = disable
        
        if hasattr(app_instance, 'kpj_input'):
            app_instance.kpj_input.disabled = disable
    
    @staticmethod
    def reset_ui(app_instance):
        """Reset UI to initial state"""
        app_instance.progress_bar.value = 0
        app_instance.progress_label.text = "Progress: 0/0 (0%)"
        app_instance.status_label.text = MESSAGES.get("ready", "Ready to process")
        UIBuilder.disable_controls(app_instance, False)
        
        # Reset stats panel
        if hasattr(app_instance, 'stats_panel'):
            default_stats = {
                "total_processed": 0,
                "successful": 0,
                "skipped": 0,
                "failed": 0,
                "success_rate": "0%",
                "current_kpj": "None",
                "status": "Idle",
                "time": "00:00:00"
            }
            UIBuilder.update_stats_panel(app_instance, default_stats)