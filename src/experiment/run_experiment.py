from src.experiment.upload_vector import upload_vector
from src.calibration.calibrate_leds import calibrate_leds
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
from thorlabs_tsi_sdk.tl_camera_enums import OPERATION_MODE
import matplotlib.pyplot as plt
import pyfirmata
import numpy as np
import time


def run_experiment(recalibrate=False):

    # Connect to the Arduino Uno:
    board = pyfirmata.Arduino('COM3')
    it = pyfirmata.util.Iterator(board)
    it.start()

    # Specify the pins we will be using for the LEDs
    led_pins = [
        board.get_pin('d:3:p'),
        board.get_pin('d:6:p'),
        board.get_pin('d:9:p'),
        board.get_pin('d:11:p')
    ]

    # Clear the board, then pause
    upload_vector(led_pins, np.zeros(4))
    time.sleep(5)

    # Alignment
    # alignment(led_pins, alternating=False)
    alignment(led_pins, alternating=True)

    # Recalibrate if asked
    if recalibrate:
        calibrate_leds(show_selection=False, board=board)

    # Initialize the SDK and get a list of available cameras
    sdk = TLCameraSDK()
    serials = sdk.discover_available_cameras()    

    # Connect to the camera
    with sdk.open_camera(camera_serial_number=serials[0]) as cam:
        pass

        # Line cut experiment
        line_cut_experiment(led_pins, cam)


def alignment(led_pins, alternating=False):
    while True:
        if alternating:
            for i in range(4):
                vector = np.zeros(4)
                vector[i] = 1
                upload_vector(led_pins, vector)
                time.sleep(10)
        else:
            upload_vector(led_pins, np.ones(4))
            time.sleep(10)


def ratio_experiment(led_pins, cam):

    # Set properties
    cam.exposure_time_us = 10000000
    cam.frames_per_trigger_zero_for_unlimited = 4
    cam.operation_mode = OPERATION_MODE.SOFTWARE_TRIGGERED

    # Arm the camera
    cam.arm(frames_to_buffer=2)

    # Collect data and plot
    fig, axs = plt.subplots(1, 4)
    for i in range(4):
        vector = np.zeros(4)
        vector[i] = 1
        upload_vector(led_pins, vector)
        capture = take_capture(cam)
        axs[i].plot(capture[600, :])

    # Clear the board
    upload_vector(led_pins, np.zeros(4))

    # Show the plot
    plt.show()


def line_cut_experiment(led_pins, cam):

    # Set properties
    cam.exposure_time_us = int(10e6)
    cam.frames_per_trigger_zero_for_unlimited = 4
    cam.operation_mode = OPERATION_MODE.SOFTWARE_TRIGGERED

    # Arm the camera
    cam.arm(frames_to_buffer=2)

    # Collect data and plot
    fig, axs = plt.subplots(1, 4)
    fig2, axs2 = plt.subplots(2, 2)
    ax2rav = axs2.ravel()
    r = 5
    for i in range(4):
        vector = np.zeros(4)
        vector[i] = 1
        upload_vector(led_pins, vector)
        capture = take_capture(cam)
        data = np.average(capture[600-r:600+r, :], axis=0)
        axs[i].plot(data)
        ax2rav[i].imshow(capture)
        

    # Clear the board
    upload_vector(led_pins, np.zeros(4))

    # Show the plot
    plt.show()


def take_capture(cam):
    # # Take two captures
    for k in range(2):
        cam.issue_software_trigger()
        frame = cam.get_pending_frame_or_null()

        # Settings for the camera
        frame_attempts = 0
        max_attempts = 100

        # if frame is null, try to get a frame until successful or until max_attempts is reached
        if frame is None:
            while frame is None:
                frame = cam.get_pending_frame_or_null()
                frame_attempts += 1

                if frame_attempts == max_attempts:
                    raise TimeoutError("Timeout was reached while polling for a frame, program will now exit")

    # Take the capture
    return frame.image_buffer