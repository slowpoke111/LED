import time
import gc

class BaseTransition:

    
    def __init__(self, duration=1.0, steps=30):

        self.duration = duration
        self.steps = steps
        self.step_time = duration / steps
        
    def apply_transition(self, from_screen, to_screen, progress):

        raise NotImplementedError("Subclasses must implement apply_transition")
    
    def execute(self, from_screen, to_screen, display):

        start_time = time.monotonic()
        
        for step in range(self.steps + 1):
            current_time = time.monotonic()
            elapsed = current_time - start_time
            progress = min(elapsed / self.duration, 1.0)
            
            eased_progress = self.ease(progress)
            
            transition_group = self.apply_transition(from_screen, to_screen, eased_progress)
            display.root_group = transition_group
            
            if progress >= 1.0:
                break
                
            time.sleep(self.step_time)
            gc.collect()
        
        self.cleanup()
        
        final_group = to_screen.show()
        display.root_group = final_group
        gc.collect() 
    
    def cleanup(self):
        pass 
    
    def ease(self, t):
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2


class ScreenManager:
    def __init__(self, matrixportal):
        self.matrixportal = matrixportal
        self.display = matrixportal.display
        self.current_screen = None
        self.screens = {}
        self.default_transition = None
    
    def register_screen(self, name, screen):
        self.screens[name] = screen
    
    def set_default_transition(self, transition):
        self.default_transition = transition
    
    def show_screen(self, screen_name, transition=None):

        if screen_name not in self.screens:
            raise ValueError(f"Screen '{screen_name}' not registered")
        
        new_screen = self.screens[screen_name]
        
        if self.current_screen is None:
            new_screen.show()
            self.current_screen = new_screen
        else:
            active_transition = transition or self.default_transition
            
            if active_transition is None:
                new_screen.show()
            else:
                if hasattr(active_transition, 'cleanup'):
                    active_transition.cleanup()
                active_transition.execute(self.current_screen, new_screen, self.display)
            
            self.current_screen = new_screen
    
    def get_current_screen(self):
        return self.current_screen
        
    def update_current_screen(self):
        """Update the current screen if it needs periodic updates"""
        if self.current_screen is not None and hasattr(self.current_screen, "update"):
            return self.current_screen.update()
        return False
        
    def update_all_screens(self):
        """Update all screens that need updates when hidden"""
        for name, screen in self.screens.items():
            if screen != self.current_screen and hasattr(screen, "update_when_hidden") and screen.update_when_hidden:
                # For screens that should update when hidden, run their periodic check
                if hasattr(screen, "_check_and_run_periodic"):
                    screen._check_and_run_periodic()
        
        # Also update the current screen
        self.update_current_screen()
