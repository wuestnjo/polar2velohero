# PolarSync 

Sync activities from flow.polar.com to velohero.com

12/2019 - v2 - C.W.   
09/2024 - v3 - wuestnjo


## Configure

```
## Get Polar Flow User Token

# Login at https://admin.polaraccesslink.com/#/clients 
# ... and create PolarAcessLink client 
#  --> Client ID
#  --> Client Secret

git clone https://github.com/polarofficial/accesslink-example-python.git

cd accesslink-example-python

python3 -m venv ./venv.

venv./bin/pip install -r requirements.txt

venv./bin/python example_web_app.py

# Navigate to localhost in browser
# Sign in with your polar user 
# Link account 
# Token will be located under usertokens.yml
```

```
## Get Velohero Token

# --> https://app.velohero.com/sso
```

```
## Register User and configure users.json

# adjust users-example.json and then rename to users.json 
#
# currently, the example mapping is to a german velohero account. 
# not ideal but "Sport" descriptors must be in account language. 
#
# type_id
# --> https://app.velohero.com/types/list 
#
# equipment_ids
# --> https://app.velohero.com/equipment/list
#
# --> hover over respective workout type (or click)
# --> copy ID from URL
```

## Run 
```
## Run once
python sync.py


## Run with docker compose
docker compose up


## add to crontab - requires docker compose 
# (python sync.py stores to ./data)

crontab -e
*/10 * * * * docker compose -f /opt/containers/polar-sync/docker-compose.yml up -d
```
