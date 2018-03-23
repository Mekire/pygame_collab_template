"""
The main function is defined here. It creates an instance of
Control and autodetects both core and game states.
"""

import cProfile
import pstats
import data.core.control

from data.core import prepare, tools


def main():
    args = (prepare.CAPTION, prepare.RENDER_SIZE, prepare.RESOLUTIONS)
    app = data.core.control.Control(*args)
    app.show_fps = prepare.ARGS["FPS"]
    default_state = "snake_splash"
    straight = prepare.ARGS['straight']
    state = straight or default_state
    app.auto_discovery("states")
    app.auto_discovery("games")
    app.start_state(state)
    # Start the main state
    if not prepare.ARGS['profile']:
        app.main()
    else:
        # Run with profiling turned on - produces a 'profile' file
        # with stats and then dumps this to the screen
        cProfile.runctx('app.main()', globals(), locals(), 'profile')
        p = pstats.Stats('profile')
        print(p.sort_stats('cumulative').print_stats(100))
