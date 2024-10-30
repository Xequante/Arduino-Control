from src.calibration.calibrate_leds import calibrate_leds
from src.experiment.run_experiment import run_experiment


def main():
    run_experiment(recalibrate=False)
    # calibrate_leds(N=101)


if __name__ == '__main__':
    main()
    