import sys
import time
sys.path.append('..')

from Controller import Controller

def main():
    config_file = '../config/lab_test.yaml'
    controller = Controller(config_file)
    
    # connect to the drone and gimbal (if configured)
    controller.connect()


    # start telemetry logging (if configured)
    controller.start_telemetry()


    # stop telemetry logging after 5 seconds (for testing purposes)
    time.sleep(5)
    controller.stop_telemetry()


    # disconnect from the drone and gimbal
    controller.disconnect()


if __name__ == "__main__":
    main()