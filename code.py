import time
import displayio
import gc
from adafruit_matrixportal.matrixportal import MatrixPortal

from Screens.teamLogo import TeamLogoScreen
from Screens.pitDisplay import PitDisplayScreen
from Screens.sponsorScreen import SponsorScreen #type:ignore

from Transitions.base_transition import ScreenManager
from Transitions.transitions import SlideTransition

matrixportal = MatrixPortal()

def main():
    # while not matrixportal.network.is_connected:
    #     try:
    #         matrixportal.network.connect()
    #     except Exception:
    #         time.sleep(5)

    screen_manager = ScreenManager(matrixportal)

    team_logo_screen = TeamLogoScreen(matrixportal, "/Images/frc5181BMP.bmp")
    sponsor_texts = ["Aegis Industrial Software", "La Salle College High School", "5181 Families", "Hillcrest Plaza", "Vino's Pizza", "Mass, LLC", "TDS Networks"]
    sponsor_screen = SponsorScreen(matrixportal, sponsor_texts, scroll_speed=1.2)

    screen_manager.register_screen("logo", team_logo_screen)
    screen_manager.register_screen("sponsor", sponsor_screen)

    screens = ["logo", "sponsor", ]
    idx = 0

    while True:
        screen_name = screens[idx]
        transition = SlideTransition(duration=1.5, direction="left")
        screen_manager.set_default_transition(transition)
        screen_manager.show_screen(screen_name, transition)
        if hasattr(transition, 'cleanup'):
            transition.cleanup()
        gc.collect()

        display_time = 8 if screen_name == "sponsor" else 3
        start_time = time.monotonic()
        if screen_name == "sponsor":
            while time.monotonic() - start_time < display_time:
                print("Available Memory:", gc.mem_free())
                sponsor_screen.smooth_scroll_update()
                time.sleep(0.02)

        else:
            while time.monotonic() - start_time < display_time:
                print("Available Memory:", gc.mem_free())
                screen_manager.update_all_screens()
                time.sleep(1)

        idx = (idx + 1) % len(screens)


if __name__ == "__main__":
    main()

