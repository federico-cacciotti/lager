from DataLoader import DataLoader
import argparse
import parameters as params
import os

parser = argparse.ArgumentParser(description='Decode telemetry data')
parser.add_argument('--data-folder', 
                    default=os.path.join(params.DATA_PATH, params.CURRENT_DATA_FOLDER), 
                    help='Folder containing the data')

def main():
    args = parser.parse_args()
    data_folder = args.data_folder
    loader = DataLoader(data_folder)
    data = loader.get_data()

    # get the drone and gimbal data from the loaded data as pandas dataframes
    drone_data = data['drone']
    gimbal_data = data['gimbal']
    
    print("Drone data:")
    print(drone_data)
    print("Gimbal data:")
    print(gimbal_data)

    loader.save_data(data)

if __name__ == "__main__":
    main()