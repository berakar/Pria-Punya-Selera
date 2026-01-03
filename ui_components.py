"""
BPJS AUTOMATION - UI COMPONENTS
Custom UI components for the application
"""

import kivy
kivy.require('2.1.0')

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox
from kivy.uix.slider import Slider
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.properties import (
    StringProperty, NumericProperty, BooleanProperty,
    ListProperty, ObjectProperty
)

from config import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_ERROR,
    COLOR_DISABLED, MESSAGES
)

class CustomLabel(Label):
    """Custom label with better styling"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.halign = 'left'
        self.valign = 'middle'
        self.bind(size=self.update_text_size)
    
    def update_text_size(self, *args):
        self.text_size = (self.width, None)

class HeaderLabel(CustomLabel):
    """Header label for titles"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('font_size', sp(24))
        kwargs.setdefault('bold', True)
        kwargs.setdefault('color', COLOR_PRIMARY)
        kwargs.setdefault('halign', 'center')
        super().__init__(**kwargs)

class StatusLabel(CustomLabel):
    """Status display label"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('font_size', sp(16))
        kwargs.setdefault('halign', 'left')
        kwargs.setdefault('valign', 'top')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(100))
        super().__init__(**kwargs)
        
        with self.canvas.before:
            Color(*COLOR_PRIMARY[:3], 0.1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class CustomButton(Button):
    """Custom styled button"""
    
    button_color = ListProperty(COLOR_PRIMARY)
    
    def __init__(self, **kwargs):
        kwargs.setdefault('font_size', sp(18))
        kwargs.setdefault('bold', True)
        super().__init__(**kwargs)
        
        self.background_normal = ''
        self.background_color = self.button_color
        self.color = (1, 1, 1, 1)  # White text
        
        with self.canvas.before:
            Color(*self.button_color)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )
        
        self.bind(
            pos=self.update_rect,
            size=self.update_rect,
            button_color=self.update_color
        )
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def update_color(self, *args):
        self.background_color = self.button_color
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.button_color)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )

class PrimaryButton(CustomButton):
    """Primary action button"""
    button_color = ListProperty(COLOR_PRIMARY)

class SuccessButton(CustomButton):
    """Success action button"""
    button_color = ListProperty(COLOR_SUCCESS)

class WarningButton(CustomButton):
    """Warning action button"""
    button_color = ListProperty(COLOR_WARNING)

class ErrorButton(CustomButton):
    """Error action button"""
    button_color = ListProperty(COLOR_ERROR)

class CustomTextInput(TextInput):
    """Custom text input with better styling"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('multiline', True)
        kwargs.setdefault('font_size', sp(16))
        kwargs.setdefault('padding', [dp(15), dp(15), dp(15), dp(15)])
        kwargs.setdefault('background_color', (1, 1, 1, 1))
        kwargs.setdefault('foreground_color', (0.2, 0.2, 0.2, 1))
        kwargs.setdefault('write_tab', False)
        super().__init__(**kwargs)
        
        with self.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )
            Color(0.2, 0.6, 1, 0.3)
            self.border = RoundedRectangle(
                pos=(self.pos[0]-dp(2), self.pos[1]-dp(2)),
                size=(self.size[0]+dp(4), self.size[1]+dp(4)),
                radius=[dp(10)]
            )
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.bind(focus=self.on_focus)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border.pos = (self.pos[0]-dp(2), self.pos[1]-dp(2))
        self.border.size = (self.size[0]+dp(4), self.size[1]+dp(4))
    
    def on_focus(self, instance, value):
        if value:
            self.border_color = COLOR_PRIMARY
        else:
            self.border_color = (0.7, 0.7, 0.7, 0.3)

class KPJInput(CustomTextInput):
    """Specialized input for KPJ entry"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('hint_text', MESSAGES.get('ready', 'Enter KPJ list...'))
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(200))
        super().__init__(**kwargs)

class CustomProgressBar(ProgressBar):
    """Custom progress bar with better styling"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('max', 100)
        super().__init__(**kwargs)
        
        with self.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            self.background_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(5)]
            )
            Color(*COLOR_PRIMARY)
            self.progress_rect = RoundedRectangle(
                pos=self.pos,
                size=(0, self.height),
                radius=[dp(5)]
            )
        
        self.bind(
            pos=self.update_rect,
            size=self.update_rect,
            value=self.update_progress
        )
    
    def update_rect(self, *args):
        self.background_rect.pos = self.pos
        self.background_rect.size = self.size
    
    def update_progress(self, *args):
        progress_width = (self.value / self.max) * self.width
        self.progress_rect.size = (progress_width, self.height)

class StatsPanel(GridLayout):
    """Statistics display panel"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('cols', 2)
        kwargs.setdefault('rows', 4)
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(150))
        kwargs.setdefault('padding', dp(10))
        kwargs.setdefault('spacing', dp(5))
        super().__init__(**kwargs)
        
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Create stat items
        self.create_stat_items()
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def create_stat_items(self):
        """Create statistic display items"""
        stats = [
            ("Total Processed", "0"),
            ("Successful", "0"),
            ("Skipped", "0"),
            ("Failed", "0"),
            ("Success Rate", "0%"),
            ("Current KPJ", "None"),
            ("Status", "Idle"),
            ("Time", "00:00:00")
        ]
        
        for label, value in stats:
            # Label
            lbl = CustomLabel(
                text=f"[b]{label}:[/b]",
                markup=True,
                font_size=sp(14),
                halign='left',
                size_hint_x=0.6
            )
            self.add_widget(lbl)
            
            # Value
            val_lbl = CustomLabel(
                text=value,
                font_size=sp(14),
                halign='right',
                size_hint_x=0.4
            )
            val_lbl.id = f"stat_{label.lower().replace(' ', '_')}"
            self.add_widget(val_lbl)
    
    def update_stat(self, stat_name, value):
        """Update a specific statistic"""
        widget_id = f"stat_{stat_name.lower().replace(' ', '_')}"
        for child in self.children:
            if hasattr(child, 'id') and child.id == widget_id:
                child.text = str(value)
                break

class LogPanel(ScrollView):
    """Log display panel"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.layout = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=dp(5)
        )
        self.layout.bind(minimum_height=self.layout.setter('height'))
        
        self.add_widget(self.layout)
        
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def add_log(self, message, level="INFO"):
        """Add a log entry"""
        color_map = {
            "INFO": (0.8, 0.8, 0.8, 1),
            "WARNING": (1, 0.8, 0, 1),
            "ERROR": (1, 0.3, 0.3, 1),
            "SUCCESS": (0.3, 0.8, 0.3, 1)
        }
        
        log_label = CustomLabel(
            text=message,
            font_size=sp(12),
            halign='left',
            size_hint_y=None,
            height=dp(25),
            color=color_map.get(level, (0.8, 0.8, 0.8, 1))
        )
        
        self.layout.add_widget(log_label)
        
        # Scroll to bottom
        Clock.schedule_once(self.scroll_to_bottom, 0.1)
    
    def scroll_to_bottom(self, dt):
        """Scroll to the bottom of the log"""
        self.scroll_y = 0
    
    def clear_logs(self):
        """Clear all logs"""
        self.layout.clear_widgets()

class SettingsPopup(Popup):
    """Settings popup window"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('title', 'Settings')
        kwargs.setdefault('size_hint', (0.8, 0.7))
        super().__init__(**kwargs)
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # URL Settings
        url_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200))
        url_box.add_widget(CustomLabel(text='[b]URL Settings[/b]', markup=True))
        
        from config import SIPP_URL, DPT_URL, LAPAK_URL
        
        self.sipp_input = CustomTextInput(
            text=SIPP_URL,
            hint_text='SIPP URL',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        url_box.add_widget(self.sipp_input)
        
        self.dpt_input = CustomTextInput(
            text=DPT_URL,
            hint_text='DPT URL',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        url_box.add_widget(self.dpt_input)
        
        self.lapak_input = CustomTextInput(
            text=LAPAK_URL,
            hint_text='LAPAK URL',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        url_box.add_widget(self.lapak_input)
        
        content.add_widget(url_box)
        
        # Buttons
        button_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        btn_save = SuccessButton(text='Save Settings')
        btn_save.bind(on_press=self.save_settings)
        
        btn_cancel = ErrorButton(text='Cancel')
        btn_cancel.bind(on_press=self.dismiss)
        
        button_box.add_widget(btn_save)
        button_box.add_widget(btn_cancel)
        
        content.add_widget(button_box)
        
        self.content = content
    
    def save_settings(self, instance):
        """Save settings to config"""
        try:
            # In a real app, this would save to config file
            # For now, just show message
            from logger import log_info
            log_info(f"SIPP URL: {self.sipp_input.text}")
            log_info(f"DPT URL: {self.dpt_input.text}")
            log_info(f"LAPAK URL: {self.lapak_input.text}")
            
            self.dismiss()
        except Exception as e:
            from logger import log_error
            log_error(f"Error saving settings: {str(e)}")

class ConfirmationPopup(Popup):
    """Confirmation dialog popup"""
    
    def __init__(self, title="Confirm", message="Are you sure?", 
                 confirm_text="Yes", cancel_text="No", **kwargs):
        kwargs.setdefault('size_hint', (0.6, 0.4))
        super().__init__(title=title, **kwargs)
        
        self.callback = None
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Message
        content.add_widget(CustomLabel(
            text=message,
            halign='center',
            valign='middle'
        ))
        
        # Buttons
        button_box = BoxLayout(spacing=dp(10))
        
        btn_confirm = SuccessButton(text=confirm_text)
        btn_confirm.bind(on_press=self.on_confirm)
        
        btn_cancel = ErrorButton(text=cancel_text)
        btn_cancel.bind(on_press=self.dismiss)
        
        button_box.add_widget(btn_confirm)
        button_box.add_widget(btn_cancel)
        
        content.add_widget(button_box)
        
        self.content = content
    
    def on_confirm(self, instance):
        """Handle confirm button press"""
        if self.callback:
            self.callback(True)
        self.dismiss()
    
    def set_callback(self, callback):
        """Set confirmation callback"""
        self.callback = callback

# Export commonly used components
__all__ = [
    'CustomLabel', 'HeaderLabel', 'StatusLabel',
    'PrimaryButton', 'SuccessButton', 'WarningButton', 'ErrorButton',
    'CustomTextInput', 'KPJInput',
    'CustomProgressBar', 'StatsPanel', 'LogPanel',
    'SettingsPopup', 'ConfirmationPopup'
]