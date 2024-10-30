"""
Uploads a vector to the Arduino depending on the power data
"""


from nptyping import NDArray
import numpy as np


def upload_vector(pins, vector: NDArray, maximize=True):
    # Make sure the vector is real valued
    print(vector)
    if np.min(vector) < 0:
        raise SyntaxError
    
    # Import the intensity data for the LEDs
    filename = 'resources/LED_data/led_powers.npy'
    data = np.load(filename)

    # Evaluate the max values of intensity for each LED
    max_vals = np.max(data, axis=1)
    ratios = vector / max_vals

    # If any of the ratios are above 1, or we wish to maximize the vector, quotient the vector by the maximum ratio
    if np.any(vector) and (np.any(ratios > 1) or maximize):
        vector /= np.max(ratios)

    # Find the Arduino settings vector
    samples = data.shape[1]
    setting_vals = np.linspace(0, 1, samples)

    # Compute the setting for each pin
    settings = np.zeros(4)
    for i in range(4):
        if vector[i] == 0:
            setting = 0
        else:
            setting = setting_vals[np.argmin(np.abs(data[i] - vector[i]))]
        pins[i].write(setting)
        settings[i] = setting

    # # Checking
    # print(vector)
    # print(settings)

    # Return the vector that was actually uploaded
    return vector
