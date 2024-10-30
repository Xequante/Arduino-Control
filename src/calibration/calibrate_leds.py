from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
from thorlabs_tsi_sdk.tl_camera_enums import OPERATION_MODE
import matplotlib.pyplot as plt
import numpy as np
import pyfirmata
import time


def calibrate_leds(N=1001, show_selection=False, board=None):
    
    # Connect to the Arduino Uno:
    if board is None:
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
    
    # Initialize the data we plan to store
    vals = np.linspace(0, 1, N)
    data = np.zeros((4, N))

    # Initialize the SDK and get a list of available cameras
    sdk = TLCameraSDK()
    serials = sdk.discover_available_cameras()    

    # Connect to the camera
    with sdk.open_camera(camera_serial_number=serials[0]) as cam:

        # Set properties
        cam.exposure_time_us = 200000
        cam.frames_per_trigger_zero_for_unlimited = 4
        cam.operation_mode = OPERATION_MODE.SOFTWARE_TRIGGERED

        # Specify the selection of the camera we will be sampling from
        width = cam.sensor_width_pixels
        height = cam.sensor_height_pixels
        X, Y = np.meshgrid(np.arange(width) - (width / 2), np.arange(height) - (height / 2))
        selection = X**2 + Y**2 < (height / 4)**2
        if show_selection:
            plt.imshow(selection)
            plt.show()

        # Arm the camera
        cam.arm(frames_to_buffer=2)

        # Iterate over each LED
        time.sleep(10)
        print('Collecting Data')
        for i in range(4):

            board.pass_time(0.4)

            # Reset all pins to zero
            for j in range(4):
                led_pins[j].write(0)

            # Select the relevant pin
            pin = led_pins[i]

            # Pause for a moment to make sure all LEDs are off
            time.sleep(1)
            
            # Iterate over each data value
            for j in range(N):

                # Set the power of the given LED
                pin.write(vals[j])

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
                capture = frame.image_buffer

                # Measure the average power at the center of the image
                data[i, j] = np.average(capture[selection])

    # Reset all pins to zero
    for j in range(4):
        led_pins[j].write(0)
    
    # Save the resulting data to resources
    file_name = 'resources.led_data'
    np.save('resources/LED_data/led_powers.npy', data)

    # Plot the results
    view_calibrated_data(filename='resources/LED_data/led_powers.npy')
    

def view_calibrated_data(filename=None, data=None):
    if data is None:
        if filename is None:
            raise SyntaxError('No data provided')
        else:
            data = np.load(filename)

    # Compute the x data
    x_data = np.linspace(0, 1, data.shape[1]) 

    # Generate the plots for each LED
    fig, ax = plt.subplots(1)
    for i in range(4):
        ax.plot(x_data, data[i])

    # Create legend
    fig.legend(["680 nm", "630 nm", "610 nm", "545 nm"])
    
    # Display the plot
    plt.show()
