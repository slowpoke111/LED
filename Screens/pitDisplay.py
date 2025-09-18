import time
import displayio
from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

try:
    from .base_screen import BaseScreen #type:ignore
except ImportError:
    try:
        from base_screen import BaseScreen #type:ignore
    except ImportError:
        exec(open('Screens/base_screen.py').read())

class PitDisplayScreen(BaseScreen):
    def __init__(self, matrixportal_instance, team_number=5181, event_key="2025paphi", update_interval=300):
        super().__init__(matrixportal_instance, periodic_interval=update_interval, update_when_hidden=True)
        self.team_number = team_number
        self.event_key = event_key
        self.event_data = {}
        self.matches_data = []
        self.data_loaded = False
        self.rankings_loaded = False
        self.matches_loaded = False
        self.last_status = ""
        self.bigFont = bitmap_font.load_font("/fonts/5x7.bdf")
        self.smallFont = bitmap_font.load_font("/fonts/4x6.bdf")
        self.big_font_width, self.big_font_height, _, _ = self.bigFont.get_bounding_box()
        self.small_font_width, self.small_font_height, _, _ = self.smallFont.get_bounding_box()
        self.epa_data = None
        self.fetch_and_update()

    def fetch_and_update(self):
        import gc, time, json
        try:
            rankings_url = f"http://leddisplayapi82317ahd.duckdns.org:51811/rankings/{self.event_key}/{self.team_number}"
            headers = {"X-API-KEY": "wsdbji87t7gb878tuvjbkjut8ujbknjuy9t8fasdu0y8tug"}
            response = self.matrixportal.network.fetch(rankings_url, headers=headers)
            if response.status_code == 401:
                self.last_status = "Unauthorized: Check API key"
                self.rankings_loaded = False
                response.close()
                return
            rankings_data = json.loads(response.text)
            response.close()
            self.event_data = {
                "record": {
                    "total": {
                        "wins": rankings_data.get("wins", 0),
                        "losses": rankings_data.get("losses", 0)
                    },
                    "qual": {
                        "rank": rankings_data.get("rank", "N/A"),
                        "num_teams": rankings_data.get("num_teams", 0)
                    }
                }
            }
            self.rankings_loaded = True
        except Exception as e:
            self.last_status = f"Rankings error: {e}"
            self.rankings_loaded = False
            return
        gc.collect()
        time.sleep(0.2)
        try:
            matches_url = f"http://leddisplayapi82317ahd.duckdns.org:51811/next_match/{self.event_key}/{self.team_number}"
            response = self.matrixportal.network.fetch(matches_url, headers=headers)
            if response.status_code == 401:
                self.last_status = "Unauthorized: Check API key"
                self.matches_loaded = False
                response.close()
                return
            match_data = json.loads(response.text)
            response.close()
            self.matches_data = []
            if match_data and "message" not in match_data:
                self.matches_data.append(match_data)
                self.matches_loaded = True
            else:
                self.matches_loaded = False
        except Exception as e:
            import sys
            print(f"[PitDisplayScreen] Match fetch error: {e}", file=sys.stderr)
            self.last_status = "Match error"
            self.matches_loaded = False
            return
        gc.collect()
        time.sleep(0.2)

        try:
            epa_url = f"http://leddisplayapi82317ahd.duckdns.org:51811/getEPA/{self.event_key}/{self.team_number}"
            response = self.matrixportal.network.fetch(epa_url, headers=headers)
            if response.status_code == 401:
                self.last_status = "Unauthorized: Check API key"
                response.close()
                self.epa_data = None
                return
            epa_data = json.loads(response.text)
            response.close()
            if "mean" in epa_data and "sd" in epa_data:
                self.epa_data = epa_data
            else:
                self.epa_data = None
        except Exception as e:
            self.last_status = f"EPA error: {e}"
            self.epa_data = None
            return
        gc.collect()
        time.sleep(0.2)
        self.data_loaded = self.rankings_loaded and self.matches_loaded
        if not self.data_loaded and not self.last_status:
            self.last_status = "Data not loaded"
        else:
            self.last_status = ""

    def create_display_group(self):
        if not self.data_loaded:
            main_group = displayio.Group()
            loading_label = label.Label(
                self.smallFont,
                text=self.last_status or "Loading...",
                color=0xFFFFFF,
                x=(self.display.width - self.small_font_width * 10) // 2,
                y=self.small_font_height * 2
            )
            main_group.append(loading_label)
            return main_group
        
        record = self.event_data.get("record", {})
        total_record = record.get("total", {})
        qual_record = record.get("qual", {})
        winCount = total_record.get("wins", 0)
        lossCount = total_record.get("losses", 0)
        rank = qual_record.get("rank", "N/A")
        num_teams = qual_record.get("num_teams", 0)

        next_match = None
        for match in self.matches_data:
            if match.get("status") != "Completed":
                next_match = match
                break

        if not next_match and self.matches_data:
            next_match = self.matches_data[-1]

        main_group = displayio.Group()

        labels = []
        rank_text = f"Rank: {rank}/{num_teams}"
        labels.append((rank_text, self.smallFont, 0x00FF00))

        if next_match:
            match_time = next_match.get("time", 0)
            alliance_color = next_match.get("alliance", "").upper()
            match_time_struct = time.localtime(match_time)
            hour = match_time_struct[3]
            minute = match_time_struct[4]
            time_text = f"{hour:02d}:{minute:02d}"
            match_text = f"{time_text} {alliance_color}"
            labels.append((match_text, self.bigFont, 0x0000FF if alliance_color == "BLUE" else 0xFF0000))

        wl_text = f"W/L: {winCount}-{lossCount}"
        labels.append((wl_text, self.bigFont, 0xFFFFFF))

        if self.epa_data:
            epa_text = f"EPA: {self.epa_data['mean']:.1f}"
            labels.append((epa_text, self.smallFont, 0xFFFF00))

        total_height = 0
        heights = []
        for text, font, color in labels:
            _, h, _, _ = font.get_bounding_box()
            heights.append(h)
            total_height += h
        spacing = (self.display.height - total_height) // (len(labels) + 1)

        y = spacing + heights[0] // 2
        for i, (text, font, color) in enumerate(labels):
            label_width = font.get_bounding_box()[0] * len(text)
            lbl = label.Label(
                font,
                text=text,
                color=color,
                x=(self.display.width - label_width) // 2,
                y=y
            )
            main_group.append(lbl)
            y += heights[i] + spacing

        return main_group

    def _periodic(self):
        self.fetch_and_update()

_pit_display_screen = None

def show_pit_display(matrixportal_instance=None, team_number=5181, event_key="2025paphi", update_interval=300):
    global _pit_display_screen
    
    if matrixportal_instance is None:
        matrixportal = MatrixPortal()
    else:
        matrixportal = matrixportal_instance
    
    if (_pit_display_screen is None or 
        _pit_display_screen.team_number != team_number or 
        _pit_display_screen.event_key != event_key):
        _pit_display_screen = PitDisplayScreen(matrixportal, team_number, event_key, update_interval)
    
    main_group = _pit_display_screen.show() 
    
    return matrixportal, main_group, _pit_display_screen

def run_pit_display_screen(team_number=5181, event_key="2025paphi"):
    matrixportal = MatrixPortal()
    screen = PitDisplayScreen(matrixportal, team_number, event_key, update_interval=60)
    
    while True:
        screen.show()
        time.sleep(1)
    
if __name__ == "__main__":
    teamNumber = 5181
    eventKey = "2025paphi"
    run_pit_display_screen(teamNumber, eventKey)
