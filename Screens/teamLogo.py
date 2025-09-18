import time
import displayio
from adafruit_matrixportal.matrixportal import MatrixPortal

try:
    from .base_screen import BaseScreen #type:ignore
except ImportError:
    try:
        from base_screen import BaseScreen #type:ignore
    except ImportError:
        exec(open('Screens/base_screen.py').read())

class TeamLogoScreen(BaseScreen):
    def __init__(self, matrixportal_instance, image_path="/Images/frc5181BMP.bmp"):
        super().__init__(matrixportal_instance, periodic_interval=None) 
        self.image_path = image_path
    
    def create_display_group(self):
        bitmap = displayio.OnDiskBitmap(self.image_path)
        tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
        main_group = displayio.Group()
        main_group.append(tile_grid)
        return main_group

_team_logo_screen = None

def show_team_logo(matrixportal_instance=None, image_path="/Images/frc5181BMP.bmp"):
    global _team_logo_screen
    
    if matrixportal_instance is None:
        matrixportal = MatrixPortal()
    else:
        matrixportal = matrixportal_instance
    
    if _team_logo_screen is None:
        _team_logo_screen = TeamLogoScreen(matrixportal, image_path)
    
    group = _team_logo_screen.show()
    return matrixportal, group

def run_team_logo_screen():
    matrixportal, _ = show_team_logo()
    
    while True:
        time.sleep(1)

if __name__ == "__main__":
    run_team_logo_screen()
