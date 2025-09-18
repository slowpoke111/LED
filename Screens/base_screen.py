import displayio
import time

class BaseScreen:    
    def __init__(self, matrixportal_instance, periodic_interval=None, update_when_hidden=False):
        self.matrixportal = matrixportal_instance
        self.display = self.matrixportal.display
        self.periodic_interval = periodic_interval
        self.last_periodic_update = 0
        self.update_when_hidden = update_when_hidden
        
        if self.periodic_interval is not None:
            self.last_periodic_update = time.monotonic()
    
    def create_display_group(self):
        raise NotImplementedError("Subclasses must implement create_display_group")
    
    def _periodic(self):
        pass
    
    def _check_and_run_periodic(self):
        if (self.periodic_interval is not None and 
            (time.monotonic() - self.last_periodic_update) >= self.periodic_interval):
            self._periodic()
            self.last_periodic_update = time.monotonic()
            return True
        return False
    
    def show(self):
        self._check_and_run_periodic()
        group = self.create_display_group()
        self.display.root_group = group
        return group
        
    def update(self):
        """Call this method periodically to refresh screens that need periodic updates"""
        if self._check_and_run_periodic():
            group = self.create_display_group()
            self.display.root_group = group
            return True
        return False
