import displayio
import time
from Screens.base_screen import BaseScreen

class PlayGIFScreen(BaseScreen):
    def __init__(self, matrixportal_instance, gif_path, frame_delay=0.1):
        super().__init__(matrixportal_instance, None, update_when_hidden=False)
        self.gif_path = gif_path
        self.frame_delay = frame_delay
        self.gif = None
        self.frame_count = 0
        self.current_frame = 0
        self.last_frame_time = time.monotonic()
        self._load_gif()

    def _load_gif(self):
        try:
            self.gif = displayio.OnDiskBitmap(open(self.gif_path, "rb"))
            self.frame_count = getattr(self.gif, "frame_count", 1)
        except Exception as e:
            self.gif = None
            self.frame_count = 0

    def create_display_group(self):
        group = displayio.Group()
        if self.gif:
            try:
                tile_grid = displayio.TileGrid(self.gif, pixel_shader=self.gif.pixel_shader)
                group.append(tile_grid)
            except Exception:
                pass
        return group

    def update(self):
        now = time.monotonic()
        if self.gif and (now - self.last_frame_time) >= self.frame_delay:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            try:
                self.gif.seek(self.current_frame)
            except Exception:
                pass
            self.last_frame_time = now
            group = self.create_display_group()
            self.display.root_group = group
            return True
        return False
