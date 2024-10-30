from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, TLCameraError
from ctypes import cdll, create_string_buffer, POINTER, CFUNCTYPE, \
    c_int, c_ushort, c_void_p, c_char_p, c_uint, \
    c_char, c_double, c_bool, c_longlong
from traceback import format_exception
import platform


class MyTLCameraSDK(TLCameraSDK):
    """
    Repairs DDL issue with standard TLCameraSDK
    """

    def __init__(self):

        self._disposed = True

        if TLCameraSDK._is_sdk_open:
            raise TLCameraError("TLCameraSDK is already in use. Please dispose of the current instance before"
                                " trying to create another")

        try:
            if platform.system() == 'Windows':
                # ddl_file_name = '/resources/CS235MU_dll_files/thorlabs_tsi_camera_sdk.dll'
                self._sdk = cdll.LoadLibrary('C:/Users/Mohamed ElKabbash/Arduino Control/resources/CS235MU_dll_files/thorlabs_tsi_camera_sdk.dll')
            elif platform.system() == 'Linux':
                try:
                    self._sdk = cdll.LoadLibrary(r"./libthorlabs_tsi_camera_sdk.so")
                except OSError:
                    self._sdk = cdll.LoadLibrary(r"libthorlabs_tsi_camera_sdk.so")
            else:
                raise TLCameraError("{system} is not a supported platform.".format(system=platform.system()))
            self._disposed = False
        except OSError as os_error:
            raise TLCameraError(str(os_error) +
                                "\nUnable to load library - are the thorlabs tsi camera sdk libraries "
                                "discoverable from the application directory? Try placing them in the same "
                                "directory as your program, or adding the directory with the libraries to the "
                                "PATH. Make sure to use 32-bit libraries when using a 32-bit python interpreter "
                                "and 64-bit libraries when using a 64-bit interpreter.\n")

        error_code = self._sdk.tl_camera_open_sdk()
        if error_code != 0:
            raise TLCameraError("tl_camera_open_sdk() returned error code: {error_code}\n"
                                .format(error_code=error_code))
        TLCameraSDK._is_sdk_open = True
        self._current_camera_connect_callback = None
        self._current_camera_disconnect_callback = None

        try:
            """ set C function argument types """
            self._sdk.tl_camera_discover_available_cameras.argtypes = [c_char_p, c_int]
            self._sdk.tl_camera_open_camera.argtypes = [c_char_p, POINTER(c_void_p)]
            self._sdk.tl_camera_set_camera_connect_callback.argtypes = [_camera_connect_callback_type, c_void_p]
            self._sdk.tl_camera_set_camera_disconnect_callback.argtypes = [_camera_disconnect_callback_type, c_void_p]
            self._sdk.tl_camera_close_camera.argtypes = [c_void_p]
            self._sdk.tl_camera_set_frame_available_callback.argtypes = [c_void_p, _frame_available_callback_type,
                                                                         c_void_p]
            self._sdk.tl_camera_get_pending_frame_or_null.argtypes = [c_void_p, POINTER(POINTER(c_ushort)),
                                                                      POINTER(c_int), POINTER(POINTER(c_char)),
                                                                      POINTER(c_int)]
            self._sdk.tl_camera_get_measured_frame_rate.argtypes = [c_void_p, POINTER(c_double)]
            self._sdk.tl_camera_get_is_data_rate_supported.argtypes = [c_void_p, c_int, POINTER(c_bool)]
            self._sdk.tl_camera_get_is_taps_supported.argtypes = [c_void_p, POINTER(c_bool), c_int]
            self._sdk.tl_camera_get_color_correction_matrix.argtypes = [c_void_p, POINTER(_3x3Matrix_float)]
            self._sdk.tl_camera_get_default_white_balance_matrix.argtypes = [c_void_p, POINTER(_3x3Matrix_float)]
            self._sdk.tl_camera_arm.argtypes = [c_void_p, c_int]
            self._sdk.tl_camera_issue_software_trigger.argtypes = [c_void_p]
            self._sdk.tl_camera_disarm.argtypes = [c_void_p]
            self._sdk.tl_camera_get_exposure_time.argtypes = [c_void_p, POINTER(c_longlong)]
            self._sdk.tl_camera_set_exposure_time.argtypes = [c_void_p, c_longlong]
            self._sdk.tl_camera_get_image_poll_timeout.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_set_image_poll_timeout.argtypes = [c_void_p, c_int]
            self._sdk.tl_camera_get_exposure_time_range.argtypes = [c_void_p, POINTER(c_longlong), POINTER(c_longlong)]
            self._sdk.tl_camera_get_firmware_version.argtypes = [c_void_p, c_char_p, c_int]
            self._sdk.tl_camera_get_frame_time.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_get_trigger_polarity.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_set_trigger_polarity.argtypes = [c_void_p, c_int]
            self._sdk.tl_camera_get_binx.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_set_binx.argtypes = [c_void_p, c_int]
            self._sdk.tl_camera_get_sensor_readout_time.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_get_binx_range.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
            self._sdk.tl_camera_get_is_hot_pixel_correction_enabled.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_set_is_hot_pixel_correction_enabled.argtypes = [c_void_p, c_int]
            self._sdk.tl_camera_get_hot_pixel_correction_threshold.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_set_hot_pixel_correction_threshold.argtypes = [c_void_p, c_int]
            self._sdk.tl_camera_get_hot_pixel_correction_threshold_range.argtypes = [c_void_p, POINTER(c_int),
                                                                                     POINTER(c_int)]
            self._sdk.tl_camera_get_sensor_width.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_get_gain_range.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
            self._sdk.tl_camera_get_image_width_range.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
            self._sdk.tl_camera_get_sensor_height.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_get_image_height_range.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
            self._sdk.tl_camera_get_model.argtypes = [c_void_p, c_char_p, c_int]
            self._sdk.tl_camera_get_name.argtypes = [c_void_p, c_char_p, c_int]
            self._sdk.tl_camera_set_name.argtypes = [c_void_p, c_char_p]
            self._sdk.tl_camera_get_name_string_length_range.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
            self._sdk.tl_camera_get_frames_per_trigger_zero_for_unlimited.argtypes = [c_void_p, POINTER(c_uint)]
            self._sdk.tl_camera_set_frames_per_trigger_zero_for_unlimited.argtypes = [c_void_p, c_uint]
            self._sdk.tl_camera_get_frames_per_trigger_range.argtypes = [c_void_p, POINTER(c_uint), POINTER(c_uint)]
            self._sdk.tl_camera_get_usb_port_type.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_get_communication_interface.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_get_operation_mode.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_set_operation_mode.argtypes = [c_void_p, c_int]
            self._sdk.tl_camera_get_is_armed.argtypes = [c_void_p, POINTER(c_bool)]
            self._sdk.tl_camera_get_is_eep_supported.argtypes = [c_void_p, POINTER(c_bool)]
            self._sdk.tl_camera_get_is_led_supported.argtypes = [c_void_p, POINTER(c_bool)]
            self._sdk.tl_camera_get_is_cooling_supported.argtypes = [c_void_p, POINTER(c_bool)]
            self._sdk.tl_camera_get_is_cooling_enabled.argtypes = [c_void_p, POINTER(c_bool)]
            self._sdk.tl_camera_get_is_nir_boost_supported.argtypes = [c_void_p, POINTER(c_bool)]
            self._sdk.tl_camera_get_camera_sensor_type.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_get_color_filter_array_phase.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_get_camera_color_correction_matrix_output_color_space.argtypes = [c_void_p, c_char_p]
            self._sdk.tl_camera_get_data_rate.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_set_data_rate.argtypes = [c_void_p, c_int]
            self._sdk.tl_camera_get_sensor_pixel_size_bytes.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_get_sensor_pixel_width.argtypes = [c_void_p, POINTER(c_double)]
            self._sdk.tl_camera_get_sensor_pixel_height.argtypes = [c_void_p, POINTER(c_double)]
            self._sdk.tl_camera_get_bit_depth.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_get_roi.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int), POINTER(c_int),
                                                    POINTER(c_int)]
            self._sdk.tl_camera_set_roi.argtypes = [c_void_p, c_int, c_int, c_int, c_int]
            self._sdk.tl_camera_get_roi_range.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int), POINTER(c_int),
                                                          POINTER(c_int), POINTER(c_int), POINTER(c_int),
                                                          POINTER(c_int), POINTER(c_int)]
            self._sdk.tl_camera_get_serial_number.argtypes = [c_void_p, c_char_p, c_int]
            self._sdk.tl_camera_get_serial_number_string_length_range.argtypes = [c_void_p, POINTER(c_int),
                                                                                  POINTER(c_int)]
            self._sdk.tl_camera_get_is_led_on.argtypes = [c_void_p, POINTER(c_bool)]
            self._sdk.tl_camera_set_is_led_on.argtypes = [c_void_p, c_bool]
            self._sdk.tl_camera_get_eep_status.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_set_is_eep_enabled.argtypes = [c_void_p, c_bool]
            self._sdk.tl_camera_get_biny.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_set_biny.argtypes = [c_void_p, c_int]
            self._sdk.tl_camera_get_biny_range.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
            self._sdk.tl_camera_get_gain.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_set_gain.argtypes = [c_void_p, c_int]
            self._sdk.tl_camera_get_black_level.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_set_black_level.argtypes = [c_void_p, c_int]
            self._sdk.tl_camera_get_black_level_range.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
            self._sdk.tl_camera_get_frames_per_trigger_zero_for_unlimited.argtypes = [c_void_p, POINTER(c_uint)]
            self._sdk.tl_camera_set_frames_per_trigger_zero_for_unlimited.argtypes = [c_void_p, c_uint]
            self._sdk.tl_camera_get_frames_per_trigger_range.argtypes = [c_void_p, POINTER(c_uint), POINTER(c_uint)]
            self._sdk.tl_camera_get_image_width.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_get_image_height.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_get_polar_phase.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_get_frame_rate_control_value_range.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double)]
            self._sdk.tl_camera_get_is_frame_rate_control_enabled.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_set_is_frame_rate_control_enabled.argtypes = [c_void_p, c_int]
            self._sdk.tl_camera_get_frame_rate_control_value.argtypes = [c_void_p, POINTER(c_double)]
            self._sdk.tl_camera_set_frame_rate_control_value.argtypes = [c_void_p, c_double]
            self._sdk.tl_camera_get_timestamp_clock_frequency.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_camera_convert_gain_to_decibels.argtypes = [c_void_p, c_int, POINTER(c_double)]
            self._sdk.tl_camera_convert_decibels_to_gain.argtypes = [c_void_p, c_double, POINTER(c_int)]
            self._sdk.tl_camera_get_is_operation_mode_supported.argtypes = [c_void_p, c_int, POINTER(c_bool)]

            self._sdk.tl_camera_get_last_error.restype = c_char_p
            # noinspection PyProtectedMember
            self._sdk._internal_command.argtypes = [c_void_p, c_char_p, c_uint, c_char_p, c_uint]
        except Exception as exception:
            _logger.error("SDK initialization failed; " + str(exception))
            raise exception


