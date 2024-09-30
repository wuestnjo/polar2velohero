import requests
import difflib
from datetime import datetime
from datetime import timedelta

def getSportID(name):
    sportIDs = {
        "Radsport": 1,
        "Cycling": 1,
        "Mountainbike": 6,
        "Pedelec": 12,
        "Velomobil": 9,
        "Laufsport": 2,
        "Running": 2,
        "Schwimmsport": 3,
        "Swimming": 3,
        "Fitness": 4,
        "Ballsport": 10,
        "Krafttraining": 5,
        "Wandern": 7,
        "Hiking": 7,
        "Wintersport": 8,
        "Wassersport": 11
    }

    if name in sportIDs.keys():
        return sportIDs[name]
    else:
        print(f"{name} not found in mapping (Defaulting to misc category Pedelec!")
        return 12



class Client():

    def __init__(self, sso):
        self.sso = sso
        self.cachedVHpages = {}

    def uploadFile(self, filePath):
        r = requests.post('http://app.velohero.com/upload/file/',
        params={'view': 'json', 'sso': self.sso, 'submit': '1'},
        files={'file': open(filePath, 'rb')}, timeout=10)

        if (r.status_code == 200) and ("id" in r.json().keys()):
            # Parse Workout ID from JSON
            veloheroID = r.json()["id"]
            print(f"Uploaded activity: {veloheroID}")
            return int(veloheroID)
        else:
            Exception("Upload failed")
            # print(r.content)


    def CreateWorkout(self, filePath, mapping):

        sport_id = type_id = ''
        equipment_ids = '[]'

        if mapping is not None:
            sport_id = getSportID(mapping["Sport"])
            if "type_id" in mapping.keys():
                type_id = mapping["type_id"]
            if "equipment_ids" in mapping.keys():
                equipment_ids = mapping["equipment_ids"]

            print(f'Mapping applied: {mapping["Sport"]}->{sport_id}|{type_id}|{equipment_ids}')

        ID = self.uploadFile(filePath)
        self.editWorkoutType(ID, sport_id, type_id, equipment_ids)

        self._addWeather(ID)


        return ID



    def editWorkoutType(self, ID, sport_id, type_id, equipment_ids):
        if not 'equipment_ids':
            equipment_ids = []

        params = {
                'sso': self.sso,
                'view': 'json',
                'sport_id': sport_id,
                'type_id': type_id,
                'equipment_ids': equipment_ids
        }

        velohero_edit = requests.get('http://app.velohero.com/workouts/change/' + str(ID), 
                                     params=params, timeout=10)



    def updateWorkout(self, ID, **kwargs):
        '''
        replace content of closest matching field from workout JSON
        e.g. updateWorkout(ID, temp_c = 5, wind_bft = 1)
        '''
        
        workout = requests.get('http://app.velohero.com/export/workouts/json?workout_id=' + str(ID-1),
                           params={'sso': self.sso}, timeout=10).json()['workouts'][0]
        updatedFields = dict(kwargs.items())

        print(f'Updated fields: {updatedFields}')

        for arg in updatedFields.keys():
            workout_field = difflib.get_close_matches(arg, workout.keys(), n=1, cutoff=0.6)[0]
            print(f"Field {arg} match: {workout_field}")
            workout[workout_field] = updatedFields[arg]

        params = {
        "workout_date": workout["date_ymd"],
        "workout_start_time": workout["start_time"], 
        "workout_dur_time": workout["dur_time"], 
        "workout_dist_km": workout["dist_km"], 
        "workout_asc_m": workout["asc_m"], 
        "workout_dsc_m": workout["dsc_m"], 
        "workout_alt_min_m": workout["alt_min_m"], 
        "workout_alt_max_m": workout["alt_max_m"], 
        "workout_spd_avg_kph": workout["spd_avg_kph"], 
        "workout_spd_max_kph": workout["spd_max_kph"], 
        "workout_hr_avg_bpm": workout["hr_avg_bpm"], 
        "workout_hr_max_bpm": workout["hr_max_bpm"], 
        "workout_cad_avg_rpm": workout["cad_avg_rpm"], 
        "workout_cad_max_rpm": workout["cad_max_rpm"], 
        "workout_pwr_avg_w": workout["pwr_avg_w"], 
        "workout_pwr_max_w": workout["pwr_max_w"], 
        "workout_borg_rpe": workout["borg_rpe"], 
        "sport_id": workout["sport_id"], 
        "type_id": workout["type_id"], 
        "route_id": workout["route_id"], 
        "workout_kcal": workout["kcal"], 
        "workout_weather": workout["weather_id"],
        "workout_temp_c": workout["temp_c"],
        "workout_wind_bft": workout["wind_bft"],
        "workout_comment": workout["workout_comment"]}

        if "equipment_ids" in workout.keys():
            params['equipment_ids'] = workout['equipment_ids']

        params['sso'] = self.sso
        params['submit'] = 1
        editData = requests.get('http://app.velohero.com/workouts/edit/' + str(ID), 
                                params=params, timeout=10)
        content = editData.content


        return


    def _addWeather(self, ID):
        workout = requests.get('http://app.velohero.com/export/workouts/json?workout_id=' + str(ID-1),
                           params={'sso': self.sso}, timeout=10).json()['workouts'][0]

        duration = datetime.strptime(workout['dur_time'], "%H:%M:%S")
        delta = timedelta(hours=duration.hour, minutes=duration.minute)

        middleTimestamp = datetime.strptime(f"{workout['date_ymd']} {workout['start_time']}", 
                                            "%Y-%m-%d %H:%M:%S")+delta/2

        if datetime.now()-middleTimestamp > timedelta(hours=3):
            return


        weatherdata = requests.get('http://app.velohero.com/openweathermap/' + str(ID), 
                                   params={'sso': self.sso}, timeout=10)

        self.updateWorkout(ID,
            weather_id = weatherdata.json()['weather'],
            temp_c = weatherdata.json()['temp_c'],
            wind_bft = weatherdata.json()['wind_bft'])


    # def fixAltitude(self, ID, ascent, descent):
    #     self.updateWorkout(ID, asc_m = ascent, dsc_m = descent)
