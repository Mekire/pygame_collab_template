"""
A generalized state machine.  Most notably used for general program flow.
"""


class StateMachine(object):
    """
    A generic state machine.
    """
    def __init__(self):
        self.done = False
        self.state_dict = {}
        self.state_name = None
        self.state = None

    def setup_states(self, state_dict, start_state):
        """
        Given a dictionary of states and a state to start in,
        creates the self.state_dict.
        """
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

    def update(self, surface, keys, now, dt, scale):
        """
        Checks if a state is done or has called for a game quit.
        State is flipped if neccessary and State.update is called.
        """
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(surface, keys, now, dt, scale)

    def start_state(self, state_name, now, persist=None):
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
        instance.startup(now, persist)
        self.state = instance
        self.state_name = state_name

    def flip_state(self):
        """
        When a State changes to done necessary startup and cleanup functions
        are called and the current State is changed.
        """
        previous, self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()
        self.start_state(self.state_name, persist)
        self.state.previous = previous

    def get_event(self, event, scale=(1,1)):
        """
        Pass events down to current State.
        """
        self.state.get_event(event, scale)


class _State(object):
    """
    This is a prototype class for States.  All states should inherit from it.
    No direct instances of this class should be created. get_event and update
    must be overloaded in the childclass.  The startup and cleanup methods
    need to be overloaded when there is data that must persist between States.
    """
    def __init__(self, controller, persistant={}):
        self.controller = controller
        self.start_time = 0.0
        self.now = 0.0
        self.done = False
        self.quit = False
        self.next = None
        self.previous = None
        self.persist = persistant

    def get_event(self, event, scale=(1,1)):
        """
        Processes events that were passed from the main event loop.
        Must be overloaded in children.
        """
        pass

    def startup(self, now, persistant):
        """
        Add variables passed in persistant to the proper attributes and
        set the start time of the State to the current time.
        """
        self.persist = persistant
        self.start_time = now

    def cleanup(self):
        """
        Add variables that should persist to the self.persist dictionary.
        Then reset State.done to False.
        """
        self.done = False
        return self.persist

    def update(self, surface, keys, now, dt, scale):
        """
        Update function for state.  Must be overloaded in children.
        """
        self.draw(surface)

    def draw(self, surface):
        """
        Put all drawing logic here.  Called at the end of the update method.
        """
        pass

    # Should probably go elsewhere or just be removed.
    def render_font(self, font, msg, color, center):
        """
        Return the rendered font surface and its rect centered on center.
        """
        msg = font.render(msg, 1, color)
        rect = msg.get_rect(center=center)
        return msg, rect
