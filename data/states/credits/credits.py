import pygame as pg

from data.core import prepare
from data.components.labels import FlashingText, Label
from data.components.state_machine import _State


class Credits(_State):
    """
    Shown by clicking the credits button in the lobby page.
    """
    def __init__(self, controller):
        super(Credits, self).__init__(controller)
        self.next = None
        self.screen_rect = pg.Rect((0, 0), prepare.RENDER_SIZE)
        cent_x = self.screen_rect.centerx
        self.anykey = FlashingText((cent_x, 650), "[Press Any Key]",
                                   "Fixedsys500c", pg.Color("gold"), 30, 350)
        self.titles = []
        names = ["/u/mekire", "/u/bitcraft", "/u/iminurnamez"]
        
        for i,name in enumerate(names, start=-1):
            text = "Some stuff by {}".format(name)
            self.titles.append(Label(prepare.FONTS["Fixedsys500c"], 48, text,
                               pg.Color("white"),
                               {"centerx" : self.screen_rect.centerx,
                                "centery" : self.screen_rect.centery + i*80}))
        self.titles.append(Label(prepare.FONTS["Fixedsys500c"], 48,
                           "Your Name Here",
                           pg.Color("white"),
                           {"centerx" : self.screen_rect.centerx,
                            "centery" : self.screen_rect.centery + (i+1)*80}))

    def startup(self, current_time, persistent):
        """
        This method will be called each time the state resumes.
        """
        self.start_time = current_time
        self.persist = persistent

    def update(self, surface, keys, current_time, dt, scale):
        """
        Updates the credit screen.
        """
        self.anykey.update(current_time)
        self.draw(surface)

    def draw(self, surface):
        surface.fill(prepare.BACKGROUND_BASE)
        for title in self.titles:
            title.draw(surface)
        surface.blit(self.anykey.image, self.anykey.rect)

    def get_event(self, event, scale):
        if event.type == pg.QUIT:
            self.done = True
            self.quit = True
        elif event.type == pg.KEYUP:
            self.done  = True
            self.next = "lobby"
