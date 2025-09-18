import displayio
import terminalio
import time
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from Screens.base_screen import BaseScreen
import gc


class SponsorScreen(BaseScreen):
    def __init__(self, matrixportal_instance, text_list, scroll_speed=0.5):
        super().__init__(matrixportal_instance, None, update_when_hidden=False)
        self.font = bitmap_font.load_font("/fonts/4x6.bdf")
        self.display_height = self.display.height
        self.display_width = self.display.width
        self.font_height = 6
        self.line_height = 12
        self.char_width = 4
        self.blue_color = 0x0000FF
        self.gold_color = 0xFFD700
        self.max_chars_per_line = (self.display_width - 4) // self.char_width
        self.y_offset = 0.0  
        self.scroll_speed = scroll_speed 
        self.text_list = text_list
        self.sponsor_indices = []
        self.wrapped_lines = self._wrap_text_list()
        self.recalculate_total_height()
        gc.collect()
        
    def recalculate_total_height(self):
        sponsor_gap = self.line_height + 1
        line_gap = 8
        
        total_height = 0
        current_sponsor = -1
        
        for sponsor_index in self.sponsor_indices:
            if sponsor_index != current_sponsor:
                total_height += sponsor_gap
                current_sponsor = sponsor_index
            else:
                total_height += line_gap
                
        self.total_height = total_height
        
    def _wrap_text(self, text):
        if len(text) <= self.max_chars_per_line:
            return [text]
            
        lines = []
        words = text.split()
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 > self.max_chars_per_line:
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                
                if len(word) > self.max_chars_per_line:
                    while word:
                        lines.append(word[:self.max_chars_per_line])
                        word = word[self.max_chars_per_line:]
                else:
                    current_line = word
            else:
                if current_line:
                    current_line += " "
                current_line += word
        
        if current_line:
            lines.append(current_line)
            
        return lines
        
    def _wrap_text_list(self):
        wrapped_lines = []
        self.sponsor_indices = []
        
        for i, text in enumerate(self.text_list):
            wrapped_text = self._wrap_text(text)
            wrapped_lines.extend(wrapped_text)
            
            for _ in wrapped_text:
                self.sponsor_indices.append(i)
                
        return wrapped_lines

    def create_display_group(self):
        group = displayio.Group()
        
        screen_buffer = self.line_height
        
        current_sponsor = -1
        sponsor_gap = self.line_height + 1
        line_gap = 8
        current_y = int(self.y_offset)
        
        for i, text in enumerate(self.wrapped_lines):
            sponsor_index = self.sponsor_indices[i]
            
            color = self.blue_color if (sponsor_index % 2 == 0) else self.gold_color
            
            if sponsor_index != current_sponsor:
                current_y += sponsor_gap
                current_sponsor = sponsor_index
            else:
                current_y += line_gap
            
            if -screen_buffer <= current_y <= self.display_height + screen_buffer:
                lbl = label.Label(self.font, text=text, color=color, x=2, y=current_y)
                group.append(lbl)
                del lbl
            
            if current_y > self.display_height:
                wrapped_y = current_y - self.total_height
                if -screen_buffer <= wrapped_y <= self.display_height + screen_buffer:
                    lbl = label.Label(self.font, text=text, color=color, x=2, y=wrapped_y)
                    group.append(lbl)
                    del lbl
            
            if i % 3 == 0:
                gc.collect()
                
        gc.collect()
        return group

    def smooth_scroll_update(self):
        self.y_offset += self.scroll_speed
        if self.y_offset >= self.total_height:
            self.y_offset = 0.0
        gc.collect()
        group = self.create_display_group()
        self.matrixportal.display.root_group = group
        try:
            self.display.refresh(minimum_frames_per_second=0)
        except Exception:
            pass
        del group
        gc.collect()
