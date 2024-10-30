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