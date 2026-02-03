import numpy as np

from metavision_sdk_core import BaseFrameGenerationAlgorithm
from metavision_sdk_stream import Camera, CameraStreamSlicer
from metavision_sdk_ui import MTWindow, BaseWindow, EventLoop, UIKeyEvent


def parse_args():
    import argparse
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Metavision SDK Get Started sample.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-i', '--input-event-file',
        help="Path to input event file (RAW or HDF5). If not specified, the camera live stream is used.")
    args = parser.parse_args()
    return args


def get_the_events_example():
    args = parse_args()

    if args.input_event_file:
        camera = Camera.from_file(args.input_event_file)
    else:
        camera = Camera.from_first_available()

    global_counter = 0  # This will track how many events we processed
    global_max_t = 0  # This will track the highest timestamp we processed

    slicer = CameraStreamSlicer(camera.move())
    for slice in slicer:
        print("----- New event slice! -----")
        if slice.events.size == 0:
            print("The current event slice is empty.")
        else:
            min_t = slice.events['t'][0]   # Get the timestamp of the first event of this slice
            max_t = slice.events['t'][-1]  # Get the timestamp of the last event of this callback
            global_max_t = max_t  # Events are ordered by timestamp, so the current last event has the highest timestamp

            counter = slice.events.size  # Local counter
            global_counter += counter  # Increase global counter

            print(f"There were {counter} events in this event slice.")
            print(f"There were {global_counter} total events up to now.")
            print(f"The current event slice included events from {min_t} to {max_t} microseconds.")
            print("----- End of the event slice! -----")


    # Print the global statistics
    duration_seconds = global_max_t / 1.0e6
    print(f"There were {global_counter} events in total.")
    print(f"The total duration was {duration_seconds:.2f} seconds.")
    if duration_seconds >= 1:  # No need to print this statistics if the total duration was too short
        print(f"There were {global_counter / duration_seconds :.2f} events per second on average.")

def add_a_display_example():
    args = parse_args()

    if args.input_event_file:
        camera = Camera.from_file(args.input_event_file)
    else:
        camera = Camera.from_first_available()

    slicer = CameraStreamSlicer(camera.move())
    width = slicer.camera().width()
    height = slicer.camera().height()
    frame = np.zeros((height, width, 3), np.uint8)

    with MTWindow(title="Metavision SDK Get Started", width=width, height=height,
                  mode=BaseWindow.RenderMode.BGR) as window:
        def keyboard_cb(key, scancode, action, mods):
            if key == UIKeyEvent.KEY_ESCAPE or key == UIKeyEvent.KEY_Q:
                window.set_close_flag()

        window.set_keyboard_callback(keyboard_cb)

        for slice in slicer:
            EventLoop.poll_and_dispatch()
            BaseFrameGenerationAlgorithm.generate_frame(slice.events, frame)
            window.show_async(frame)

            if window.should_close():
                break

if __name__ == "__main__":
    # get_the_events_example()
    add_a_display_example()