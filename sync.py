import os 
import json 
import PolarFlowAPI
import VeloheroAPI
from datetime import datetime, timezone, timedelta


def load_config(configFile):
    with open(configFile) as f:
        config = json.loads(f.read())
        try:
            config = config
        except:
            print(f"Can't load config {configFile}")
    return config


def simpleLog(username, message):
    data_dir = os.environ.get("DATA_DIR", "./data")
    with open(f"{data_dir}/{username}/{username}.log", 'a') as f:
        f.write(f"{datetime.now(timezone(timedelta(hours=2)))} - {message}\n")
    print(f"LOG: {datetime.now(timezone(timedelta(hours=2)))} - {message}")


if __name__ == "__main__":
    data_dir = os.environ.get("DATA_DIR", "./data")

    config = load_config(f"{data_dir}/users.json")

    for username in config.keys():
        ## Create user_data_dir if not existing already
        user_data_dir = f"{data_dir}/{username}"
        os.makedirs(user_data_dir, exist_ok=True)
        os.makedirs(f"{user_data_dir}/archive", exist_ok=True)

        ## Collect Workouts from Polar
        polar_access_token = config[username]["polar_access_token"]
        polar_user_id = config[username]["polar_user_id"]

        PFC = PolarFlowAPI.Client(polar_access_token, polar_user_id, user_data_dir)
        PFC.collectWorkouts()

        ## Upload Workouts Velohero 
        velohero_sso = config[username]["velohero_sso"]
        mapping = config[username]["mapping"]

        VHC = VeloheroAPI.Client(velohero_sso)

        for fname in os.listdir(user_data_dir):
            if ".tcx" not in fname:
                continue
            else: 
                # timestamp = fname[0:19]
                activityType = fname[20:-4]
                if activityType in mapping.keys():
                    map = mapping[activityType]
                else:
                    map = None

                vhID = VHC.CreateWorkout(f"{user_data_dir}/{fname}", map)

                os.rename(f"{user_data_dir}/{fname}", f"{user_data_dir}/archive/{fname}")
                # alternatively: delete .tcx

                log = f"vh_id: {vhID} - fname: \"{fname[:-4]}\" - Mapping: [{map}]"
                simpleLog(username, log)
