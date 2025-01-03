from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from os import access, getenv
from dotenv import load_dotenv
import iot_api_client as iot
from iot_api_client.configuration import Configuration
from iot_api_client.api import PropertiesV2Api
from iot_api_client.models import *
from iot_api_client.exceptions import ApiException

load_dotenv()

client_i = getenv('CLIENT_ID')
client_s = getenv('CLIENT_SECRET')

def get_access_token():
    #generate token
    oauth_client = BackendApplicationClient(client_id=client_i)
    token_url = "https://api2.arduino.cc/iot/v1/clients/token"

    oauth = OAuth2Session(client=oauth_client)

    token = oauth.fetch_token(
        token_url=token_url,
        client_id=client_i,
        client_secret=client_s,
        include_client_id=True,
        audience="https://api2.arduino.cc/iot",
        method='POST'
    )

    return token.get("access_token")

def get_properties_api():
    client_config = Configuration(host="https://api2.arduino.cc")
    client_config.access_token = get_access_token()
    client = iot.ApiClient(client_config)
    api = iot.PropertiesV2Api(client) 
    return api

def get_soil_moisture_data(device_list):
    data = {}

    api = get_properties_api()

    for hub in device_list:
        data[hub] = {1: {}, 2: {}}
        # Handle Zone 1
        for sensor in device_list[hub][1]:
            try:
                api_response = api.properties_v2_list(sensor.device_id)
                data[hub][1][sensor.id] = (api_response[0].last_value)
            except ApiException as e:
                data[hub][1][sensor.id] = -1
        
        # Handle Zone 2
        for sensor in device_list[hub][2]:
            try:
                api_response = api.properties_v2_list(sensor.device_id)
                data[hub][2][sensor.id] = api_response[0].last_value
            except ApiException as e:
                data[hub][2][sensor.id] = -1
        # for sensor in device_list[hub]:
        #     try:
        #         # list properties_v2
        #         api_response = api.properties_v2_list(sensor.device_id)
        #         # print(f'Soil Moisture Value {idx+1}: {api_response[0].last_value}')
        #         if data.get(hub) == None:
        #             data[hub] = [api_response[0].last_value]
        #         else:
        #             data[hub].append(api_response[0].last_value)
        #     except ApiException as e:
        #         print("Exception when calling PropertiesV2Api->propertiesV2List: %s\n" % e)
        #         data[sensor.id] = -1

    return data

def get_valve_data(device_list):
    data = {}

    api = get_properties_api()

    for device in device_list:
        try:
            # list properties_v2
            api_response = api.properties_v2_list(device.device_id)
            valves = [variable for variable in api_response if 'valve' in variable.name]
            data[device.id] = [valves[0].last_value, valves[1].last_value]
            #     print(f'Valve Status: {valves[0].last_value} {valves[1].last_value}')
        except ApiException as e:
            print("Exception when calling PropertiesV2Api->propertiesV2List: %s\n" % e)
            data[device.id] = [False, False]

    return data

def get_flow_data(device_list):
    data = {}

    api = get_properties_api()

    for device in device_list:
        try:
            # list properties_v2
            api_response = api.properties_v2_list(device.device_id)
            flows = [variable for variable in api_response if 'Flow' in variable.name]
            data[device.id] = [flows[0].last_value, flows[1].last_value]
        except ApiException as e:
            print("Exception when calling PropertiesV2Api->propertiesV2List: %s\n" % e)
            data[device.id] = [-1, -1]

    return data

def update_valve_data(device, valve_bit, value):
    api = get_properties_api()

    # Get valve variable
    try:
        api_response = api.properties_v2_list(device.device_id)
        mode = next(variable for variable in api_response
                    if variable.name == 'mode')
        mode_value = f'{valve_bit+1} {1 if value else 3}' if valve_bit != -1 else '+'
        res = api.properties_v2_publish(device.device_id, mode.id, {"value": mode_value})
        print(res)
    except ApiException as e:
        # Do nothing, as valve isn't updated
        print('valve not updated')

def update_cloud_threshold(device, threshold, value):
    api = get_properties_api() 

    try:
        api_response = api.properties_v2_list(device.device_id)
        cloud_thres = next(variable for variable in api_response
                    if variable.name == f'threshold{threshold}')
        res = api.properties_v2_publish(device.device_id, cloud_thres.id, {"value": value})
        print(res)
    except ApiException as e:
        # Do nothing, as valve isn't updated
        print('valve not updated') 