import displayio
from .base_transition import BaseTransition

class FadeTransition(BaseTransition):
    def __init__(self, duration=1.0, steps=60):
        super().__init__(duration, steps)
        self.from_group = None
        self.to_group = None

    def apply_transition(self, from_screen, to_screen, progress):
        if self.from_group is None:
            self.from_group = from_screen.create_display_group()
        if self.to_group is None:
            self.to_group = to_screen.create_display_group()

        if progress < 0.7:
            return self.from_group
        else:
            return self.to_group

    def cleanup(self):
        self.from_group = None
        self.to_group = None


class SlideTransition(BaseTransition):
    
    def __init__(self, duration=1.0, steps=30, direction="left"):
        super().__init__(duration, steps)
        self.direction = direction
        self.from_group = None
        self.to_group = None
        self.transition_group = None
    
    def apply_transition(self, from_screen, to_screen, progress):
        display_width = 64
        display_height = 32

        if self.from_group is None:
            self.from_group = from_screen.create_display_group()
        if self.to_group is None:
            self.to_group = to_screen.create_display_group()
        if self.transition_group is None:
            self.transition_group = displayio.Group()
            self.transition_group.append(self.from_group)
            self.transition_group.append(self.to_group)
        
        if self.direction == "left":
            from_x = int(-progress * display_width)
            to_x = int((1 - progress) * display_width)
        elif self.direction == "right":
            from_x = int(progress * display_width)
            to_x = int(-(1 - progress) * display_width)
        elif self.direction == "up":
            from_x, to_x = 0, 0
            from_y = int(-progress * display_height)
            to_y = int((1 - progress) * display_height)
        elif self.direction == "down":
            from_x, to_x = 0, 0
            from_y = int(progress * display_height)
            to_y = int(-(1 - progress) * display_height)
        else:
            from_x = int(-progress * display_width)
            to_x = int((1 - progress) * display_width)
        
        self.from_group.x = from_x
        self.to_group.x = to_x
        
        if self.direction in ["up", "down"]:
            self.from_group.y = from_y
            self.to_group.y = to_y
        
        return self.transition_group

    def cleanup(self):
        self.from_group = None
        self.to_group = None
        self.transition_group = None


class InstantTransition(BaseTransition):

    def __init__(self):
        super().__init__(duration=0.0, steps=1)
    
    def apply_transition(self, from_screen, to_screen, progress):
        return to_screen.create_display_group()


class BlinkTransition(BaseTransition):

    def __init__(self, duration=0.5, blink_count=3):
        super().__init__(duration, steps=blink_count * 2)
        self.blink_count = blink_count
        self.from_group = None
        self.to_group = None
        self.empty_group = None
    
    def apply_transition(self, from_screen, to_screen, progress):
        if self.from_group is None:
            self.from_group = from_screen.create_display_group()
        if self.to_group is None:
            self.to_group = to_screen.create_display_group()
        if self.empty_group is None:
            self.empty_group = displayio.Group()

        step = int(progress * self.steps)
        
        if step % 2 == 0:
            if step < self.steps:
                return self.from_group
            else:
                return self.to_group
        else:
            return self.empty_group

    def cleanup(self):
        self.from_group = None
        self.to_group = None
        self.empty_group = None
