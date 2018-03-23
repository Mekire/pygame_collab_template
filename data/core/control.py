import os
import json
import pygame as pg

from collections import OrderedDict
from importlib import import_module

from data.core import prepare


class Control(object):
    """
    Control class for entire project. Contains the game loop, and contains
    the event_loop which passes events to States as needed. Logic for flipping
    states is also found here.
    """
    def __init__(self, caption, render_size, resolutions):
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.render_size = render_size
        self.render_surf = pg.Surface(self.render_size).convert()
        self.resolutions = resolutions
        self.set_scale()
        self.caption = caption
        self.done = False
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.show_fps = False
        self.now = 0.0
        self.keys = pg.key.get_pressed()
        self.state_dict = OrderedDict()
        self.game_thumbs = OrderedDict()
        self.state_name = None
        self.state = None

    def auto_discovery(self, scene_folder):
        """
        Scan a folder, load states found in it, and register them
        """
        scene_folder_path = os.path.join(".", "data", scene_folder)
        scene_package = "data.{}.".format(scene_folder)
        exclude_endings = (".py", ".pyc", "__pycache__")
        for folder in os.listdir(scene_folder_path):
            if any(folder.endswith(end) for end in exclude_endings):
                continue
            state = self.load_state_from_path(folder, scene_package)
            self.state_dict[folder] = state
            if scene_folder == "games":
                path = os.path.join(scene_folder_path, folder, "lobby_thumb.png")
                thumb = pg.image.load(path).convert()
                self.game_thumbs[folder] = thumb

    @staticmethod
    def load_state_from_path(folder, package="data.states."):
        """
        Load a state from disk, but do not register it
        """
        try:
            scene_module = import_module(package + folder)
            state = scene_module.Scene
            return state
        except Exception as e:
            template = "{} failed to load or is not a valid game package"
            print(e)
            print(template.format(folder))
            raise

    def start_state(self, state_name, persist=None):
        """
        Start a state.
        """
        if persist is None:
            persist = {}
        try:
            state = self.state_dict[state_name]
        except KeyError:
            print('Cannot find state: {}'.format(state_name))
            raise RuntimeError
        instance = state(self)
        instance.startup(self.now, persist)
        self.state = instance
        self.state_name = state_name

    def update(self, dt):
        """
        Checks if a state is done or has called for a game quit.
        State is flipped if neccessary and State.update is called.
        """
        self.screen = pg.display.get_surface()
        self.now = pg.time.get_ticks()
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(self.render_surf, self.keys, self.now, dt, self.scale)

    def render(self):
        """
        Scale the render surface if not the same size as the display surface.
        The render surface is then drawn to the screen.
        """
        if self.render_size != self.screen_rect.size:
            scale_args = (self.render_surf, self.screen_rect.size, self.screen)
            pg.transform.smoothscale(*scale_args)
        else:
            self.screen.blit(self.render_surf, (0, 0))

    def flip_state(self):
        """
        When a State changes to done necessary startup and cleanup functions
        are called and the current State is changed.
        """
        previous, self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()
        self.start_state(self.state_name, persist)
        self.state.previous = previous

    def event_loop(self):
        """
        Process all events and pass them down to current State.
        The f5 key globally turns on/off the display of FPS in the caption
        """
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
                self.toggle_show_fps(event.key)
                if event.key == pg.K_PRINT:
                    # Print screen for full render-sized screencaps.
                    pg.image.save(self.render_surf, "screenshot.png")
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
            elif event.type == pg.VIDEORESIZE:
                self.on_resize(event.size)
                pg.event.clear(pg.VIDEORESIZE)
            self.state.get_event(event, self.scale)

    def on_resize(self, size):
        """
        If the user resized the window, change to the next available
        resolution depending on if scaled up or scaled down.
        """
        if size == self.screen_rect.size:
            return
        res_index = self.resolutions.index(self.screen_rect.size)
        adjust = 1 if size > self.screen_rect.size else -1
        if 0 <= res_index+adjust < len(self.resolutions):
            new_size = self.resolutions[res_index+adjust]
        else:
            new_size = self.screen_rect.size
        self.screen = pg.display.set_mode(new_size, pg.RESIZABLE)
        self.screen_rect.size = new_size
        self.set_scale()

    def set_scale(self):
        """
        Reset the ratio of render size to window size.
        Used to make sure that mouse clicks are accurate on all resolutions.
        """
        w_ratio = self.render_size[0]/float(self.screen_rect.w)
        h_ratio = self.render_size[1]/float(self.screen_rect.h)
        self.scale = (w_ratio, h_ratio)

    def toggle_show_fps(self, key):
        """
        Press f5 to turn on/off displaying the framerate in the caption.
        """
        if key == pg.K_F5:
            self.show_fps = not self.show_fps
            if not self.show_fps:
                pg.display.set_caption(self.caption)

    def main(self):
        """
        Main loop for entire program.
        """
        while not self.done:
            time_delta = self.clock.tick(self.fps)
            self.event_loop()
            self.update(time_delta)
            self.render()
            pg.display.update()
            if self.show_fps:
                fps = self.clock.get_fps()
                with_fps = "{} - {:.2f} FPS".format(self.caption, fps)
                pg.display.set_caption(with_fps)
