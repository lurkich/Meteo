from django.shortcuts import render

from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt

from django.conf import settings

from django.db.models import Max
from django.db.models import Min

from django.utils.timezone import get_current_timezone


import requests
import django.db
import socket
import math
import locale
import json
import traceback


from app_meteo.models import Out_temp
from app_meteo.models import In_temp
from app_meteo.models import Serre_temp

from datetime import *





############## Define global CONSTANTS
##############

APP_ENVIRONMENT_TYPE = "prod"    # values can be "dev" or "prod" 
APP_FORCE_OWM_API_CALL = False  # !!!!!!!!!!!!! if set to True, the API will be called every minute !!!!!!!!!!!!!!!!  MUST be set to false in production.

PAGE_REFRESH_SECONDS = 60
OPENWEATHER_REFRESH_SECONDS = 600




############## Define global variables
##############

IsExceptionRaised = False
ErrorMessage = ""

OpenWeather_Trigger_Counter = 999        # Initializing with a high value will prevent the call the the OpenWeather API. Limitation of the number of calls per day

Curr_DateIime_Formatted = ""
Search_Reference_Datetime = ""

wifi_icon = "bi-wifi"

out_curr_icon = ""
out_curr_description = ""
out_curr_temp_min = 0
out_curr_temp_max = 0
out_curr_temp_morn = 0
out_curr_temp_day = 0
out_curr_temp_night = 0
out_curr_wind_speed = 0
out_curr_wind_deg = 0
out_curr_sunrise = ""
out_curr_sunset = ""

Forecasts = []

Sql_out_curr_temp = 99.9
Sql_out_curr_humidity = 99.9
Sql_out_max_value = 99.9
Sql_out_min_value = 99.9
Sql_out_battery_level = 99

Sql_in_curr_temp = 99.9
Sql_in_curr_humidity = 99.9
Sql_in_max_value = 99.9
Sql_in_min_value = 99.9
Sql_in_battery_level = 99

Sql_serre_curr_temp = 99.9
Sql_serre_curr_humidity = 99.9
Sql_serre_max_value = 99.9
Sql_serre_min_value = 99.9
Sql_serre_battery_level = 99


context = {}

@csrf_exempt

def dashboard(request):

    # global PAGE_REFRESH_SECONDS
    # global OPENWEATHER_REFRESH_SECONDS

    global IsExceptionRaised
    global ErrorMessage

    global OpenWeather_Trigger_Counter


    global Curr_DateIime_Formatted
    global Search_Reference_Datetime
    global context



    ############## set the refresh rate and the OpenWeather API call counter
    ##############

    IsExceptionRaised = False
    ErrorMessage = ""

    # monitor the number of OpenWeatherMap calls since midnight

    _minutes_from_midnight = ((datetime.now() - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() ) / 60


    # initialize session variable representing the number of calls to OpenWeatherMap

    if 'monitoring_OMW_calls' not in request.session or _minutes_from_midnight < 3 :
        request.session['monitoring_OMW_calls'] = 0


    if IsExceptionRaised is False: 
        Check_Internet_Access()


    if IsExceptionRaised is False: 
        OpenWeather_Trigger_Counter = Set_Screen_Refresh_Session_Values(request)
    
    if IsExceptionRaised is False:
        Curr_DateIime_Formatted, Search_Reference_Datetime = Calculate_Current_And_Search_Reference_Date()

    if IsExceptionRaised is False:
        Get_Outside_Temperature()

    if IsExceptionRaised is False:
        Get_Inside_Temperature()

    if IsExceptionRaised is False:
        Get_Serre_Temperature()








    if IsExceptionRaised is False:
        Get_Next_5_Days_Forecast(request)



    context = Prepare_Return_HTTP_Request_Values(request)

    return render(request,'dashboard.html', context=context)



###################################################### Set Refresh values

def Set_Screen_Refresh_Session_Values(request):



    global IsExceptionRaised
    global ErrorMessage

    try:
        _Trigger_Counter = math.ceil(OPENWEATHER_REFRESH_SECONDS / PAGE_REFRESH_SECONDS)

        if 'OpenWeather_Trigger_Counter' in request.session:                        # session variable already exist, retrieve it's value
            _Trigger_Counter = request.session['OpenWeather_Trigger_Counter'] - 1
        else:
            _Trigger_Counter = 999                                                  # will force call to openweather map

        request.session['OpenWeather_Trigger_Counter'] = _Trigger_Counter            # save the new session variable value
        
        return _Trigger_Counter



    except Exception as e:
        Message_To_Display = "Error : Set_Screen_Refresh_Session_Values"
        Build_ErrorMessage(Message_To_Display, e, traceback)
        IsExceptionRaised = True




####################################################### Check internet connection

def Check_Internet_Access():

    global IsExceptionRaised
    global ErrorMessage

    global wifi_icon
    
    wifi_icon = "bi-wifi"
   
    try:
#        socket.setdefaulttimeout(100)
#        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("192.168.178.1", 80)) The EERO router does not allow to check port 80 connection refused 111
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("google.com", 80))


    except Exception as e:
        wifi_icon = "bi-wifi-off"
        Message_To_Display = "Check_Internet_Access"
        Build_ErrorMessage(Message_To_Display, e, traceback)
        IsExceptionRaised = True



###################################################### Calculate the search reference for the MIN / MAX temperatures : current date - 24 Hours

def Calculate_Current_And_Search_Reference_Date():

    global IsExceptionRaised
    global ErrorMessage

    _Today = datetime.today()

    locale.setlocale(locale.LC_TIME, 'fr_BE.utf8')

    _Curr_DateIime_Formatted = _Today.strftime("%A %d %b - %Y %H:%M:%S")           # formatted local time


    # calculate the reference day for searching the MIN / MAX temperature of the past 24 Hours

    _delta = timedelta(hours=24)
    _Curr_Datetime = datetime.today()
    
    _Search_Reference_Datetime = _Curr_Datetime - _delta

    return _Curr_DateIime_Formatted, _Search_Reference_Datetime






###################################################### get the current Outside temperature, the last 24 hours minimum and maximum temperatures

def Get_Outside_Temperature():

    global IsExceptionRaised
    global ErrorMessage

    # global Search_Reference_Datetime
    global Sql_out_curr_temp
    global Sql_out_curr_humidity
    global Sql_out_max_value
    global Sql_out_min_value
    global Sql_out_battery_level


    try:

        _Sql_out_curr_values = Out_temp.objects.order_by('-collectdate').first()

        Sql_out_curr_temp = round(_Sql_out_curr_values.temperature, 2)
        Sql_out_curr_humidity = int(round(_Sql_out_curr_values.humidity, 0))

        Sql_out_max_value = Out_temp.objects.filter(collectdate__gt=Search_Reference_Datetime).aggregate(Max('temperature'))['temperature__max']
        
        if not Sql_out_max_value == None:
            Sql_out_max_value = round(Sql_out_max_value, 1)
        else:        
            Sql_out_curr_temp = 99.9
            Sql_out_curr_humidity = 99.9
            Sql_out_max_value = 99.9
            Sql_out_min_value = 99.9
            Sql_out_battery_level = 99


        Sql_out_min_value = Out_temp.objects.filter(collectdate__gt=Search_Reference_Datetime).aggregate(Min('temperature'))['temperature__min']
        Sql_out_min_value = round(Sql_out_min_value, 1)

        Sql_out_battery_level = int(round(_Sql_out_curr_values.battery_level, 0))

    except Exception as e:
        Message_To_Display = "Error : Get_Outside_Temperature"
        Build_ErrorMessage(Message_To_Display, e, traceback)
        IsExceptionRaised = True



###################################################### get the current Inside temperature, the last 24 hours minimum and maximum temperatures

def Get_Inside_Temperature():

    global IsExceptionRaised
    global ErrorMessage
    # global Search_Reference_Datetime

    global Sql_in_curr_temp
    global Sql_in_curr_humidity
    global Sql_in_max_value
    global Sql_in_min_value
    global Sql_in_battery_level

    try:
        _Sql_in_curr_values = In_temp.objects.order_by('-collectdate').first()

        Sql_in_curr_temp = round(_Sql_in_curr_values.temperature, 2)
        Sql_in_curr_humidity = int(round(_Sql_in_curr_values.humidity, 0))

        Sql_in_max_value = In_temp.objects.filter(collectdate__gt=Search_Reference_Datetime).aggregate(Max('temperature'))['temperature__max']
        
        if not Sql_in_max_value == None:        
        
            Sql_in_max_value = round(Sql_in_max_value, 1)
        else:

            Sql_in_curr_temp = 99.9
            Sql_in_curr_humidity = 99.9
            Sql_in_max_value = 99.9
            Sql_in_min_value = 99.9
            Sql_in_battery_level = 99            

        Sql_in_min_value = In_temp.objects.filter(collectdate__gt=Search_Reference_Datetime).aggregate(Min('temperature'))['temperature__min']
        Sql_in_min_value = round(Sql_in_min_value, 1)  

        Sql_in_battery_level = int(round(_Sql_in_curr_values.battery_level, 0))

    except Exception as e:
        Message_To_Display = "Error : Get_Inside_Temperature"
        Build_ErrorMessage(Message_To_Display, e, traceback)
        IsExceptionRaised = True


###################################################### get the current Serre temperature, the last 24 hours minimum and maximum temperatures

def Get_Serre_Temperature():

    global IsExceptionRaised
    global ErrorMessage
    # global Search_Reference_Datetime

    global Sql_serre_curr_temp
    global Sql_serre_curr_humidity
    global Sql_serre_max_value
    global Sql_serre_min_value
    global Sql_serre_battery_level
    
    try:
        _Sql_serre_curr_values = Serre_temp.objects.order_by('-collectdate').first()

        Sql_serre_curr_temp = round(_Sql_serre_curr_values.temperature, 2)
        Sql_serre_curr_humidity = int(round(_Sql_serre_curr_values.humidity, 0))

        Sql_serre_max_value = Serre_temp.objects.filter(collectdate__gt=Search_Reference_Datetime).aggregate(Max('temperature'))['temperature__max']
        if not Sql_serre_max_value == None:

            Sql_serre_max_value = round(Sql_serre_max_value, 1)

            Sql_serre_min_value = Serre_temp.objects.filter(collectdate__gt=Search_Reference_Datetime).aggregate(Min('temperature'))['temperature__min']
            Sql_serre_min_value = round(Sql_serre_min_value, 1)  

            Sql_serre_battery_level = int(round(_Sql_serre_curr_values.battery_level, 0))
        else:
            Sql_serre_curr_temp = 99.9
            Sql_serre_curr_humidity = 99.9
            Sql_serre_max_value = 99.9
            Sql_serre_min_value = 99.9
            Sql_serre_battery_level = 99

    except Exception as e:
        Message_To_Display = "Error : Get_Serre_Temperature"
        Build_ErrorMessage(Message_To_Display, e, traceback)
        IsExceptionRaised = True



###################################################### get the current Outside temperature, the last 24 hours minimum and maximum temperatures

def Get_Next_5_Days_Forecast(request):


    global IsExceptionRaised
    global ErrorMessage

    global out_curr_icon
    global out_curr_description
    global out_curr_temp_min
    global out_curr_temp_max
    global out_curr_temp_morn
    global out_curr_temp_day
    global out_curr_temp_night

    global out_curr_wind_speed
    global out_curr_wind_deg

    global out_curr_sunrise
    global out_curr_sunset
    global sunshine_duration



    global Forecasts

    try:

        from prj_meteo.settings import BASE_DIR
        import os
        import time



        # _hostname = socket.gethostname()
        # _local_ip = socket.gethostbyname(_hostname + ".local")
        # proxies = { 
        #     "http": _local_ip + ":8888",
        #     "https": _local_ip + ":8888",
        #     }
        # url = 'https://api.openweathermap.org/data/3.0/onecall?lat=49.70987099981567&lon=5.7303613911147835&&appid=' + os.getenv('openWeatherMapKey') + '&units=metric&lang=fr'
        # _city_weather = requests.get(url.format()).json()
        




############################### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!       
#################### ---> COMMENT Line in production : force to call the Openweather map API. MUST be commented in production
############################### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!       
             

        if APP_FORCE_OWM_API_CALL == True:
            request.session['OpenWeather_Trigger_Counter'] = 901




        if request.session['OpenWeather_Trigger_Counter'] < 0 or request.session['OpenWeather_Trigger_Counter'] > 900:
            OpenWeather_Trigger_Counter = math.ceil(OPENWEATHER_REFRESH_SECONDS / PAGE_REFRESH_SECONDS)
            request.session['OpenWeather_Trigger_Counter'] = OpenWeather_Trigger_Counter
            print("=====================================>    Calling OpenWeatherMap URL.  <====================================")



            if APP_ENVIRONMENT_TYPE == "prod" or APP_FORCE_OWM_API_CALL == True:
                url = 'https://api.openweathermap.org/data/3.0/onecall?lat=49.70987099981567&lon=5.7303613911147835&&appid=' + os.getenv('openWeatherMapKey') + '&units=metric&lang=fr'
                _city_weather = requests.get(url.format()).json()
                
                if 'cod' in _city_weather:
                    raise Exception("401 - Error calling OpenWeatherMap")

                
                request.session['_city_weather'] = _city_weather
                request.session['monitoring_OMW_calls'] = request.session['monitoring_OMW_calls'] + 1


            else:
                _OWM_file_path = os.path.join(BASE_DIR, "app_meteo/static/OWM.json")
                _OWM_file_handle = open(_OWM_file_path,'r')
                _OWM_file_content = _OWM_file_handle.read()
                _OWM_file_handle.close()
                _city_weather = json.loads(_OWM_file_content)











    #       compute sunshine duration and save the differrence only if the request.session['sunshine_time_laps'] exist otherwise set it to 0


            # the  sunshine_time_laps_diff was already computed

            sunshine_today_total = datetime.fromtimestamp(_city_weather['current']['sunset']) - datetime.fromtimestamp(_city_weather['current']['sunrise'])
            sunshine_today_total_min = int(sunshine_today_total.total_seconds() / 60)


            if 'sunshine_time_difference_min' in request.session:

                if request.session['sunshine_day_total_min'] != sunshine_today_total_min:

                    request.session['sunshine_time_difference_min'] = sunshine_today_total_min - request.session['sunshine_day_total_min']
                    request.session['sunshine_day_total_min'] =  sunshine_today_total_min


            else:

                # the sunshine_time_laps_diff was not computed yet. Initialize it to 0
                request.session['sunshine_day_total_min'] = sunshine_today_total_min
                request.session['sunshine_time_difference_min'] = 0


        else:
            _city_weather = request.session['_city_weather']




        i = 1
        Forecasts = []


        for _day in _city_weather['daily']:

            _s = datetime.utcfromtimestamp(_day['dt']).strftime("%A %d/%m")


            if i == 1:      # today

                out_curr_icon = _day['weather'][0]['id']  
                out_curr_description = _day['weather'][0]['description'] 
                out_curr_temp_min = _day['temp']['min']
                out_curr_temp_max = _day['temp']['max']
                out_curr_temp_morn = _day['temp']['morn']
                out_curr_temp_day = _day['temp']['day']
                out_curr_temp_night = _day['temp']['night']
                out_curr_wind_speed = int(round(_day['wind_speed']/1000*3600, 0))
                out_curr_wind_deg = _day['wind_deg']
                if out_curr_wind_deg >= 180:
                    out_curr_wind_deg = out_curr_wind_deg - 180
                else:
                    out_curr_wind_deg = out_curr_wind_deg + 180

                out_curr_sunrise = datetime.utcfromtimestamp(_day['sunrise'] + _city_weather['timezone_offset']).strftime("%H:%M")  
                out_curr_sunset = datetime.utcfromtimestamp(_day['sunset'] + _city_weather['timezone_offset']).strftime("%H:%M") 

      



            if i >= 2 and i <= 6:
            
                _wind_deg = int(round(_day['wind_deg'],0))
                if _wind_deg >= 180:
                    _wind_deg = _wind_deg - 180
                else:
                    _wind_deg = _wind_deg + 180    

                    
                Forecasts.append( 
                    {
                        'ind': i, 
                        'day': _s,
                        'icon': _day['weather'][0]['id'],
                        'description': _day['weather'][0]['description'],
                        'temp_min': round(_day['temp']['min'],1),
                        'temp_max': round(_day['temp']['max'],1),
                        'temp_morn': round(_day['temp']['morn'],1),
                        'temp_day': round(_day['temp']['day'],1),
                        'temp_night': round(_day['temp']['night'],1),
                        'wind_speed': int(round(_day['wind_speed']/1000*3600,0)),
                        'wind_deg': _wind_deg,
                    }
                )
            

            i = i + 1



    except Exception as e:
        if e.args[0][0:3] == "401":
            Message_To_Display = "401 - Error calling OpenWeatherMap"
            Build_ErrorMessage(Message_To_Display, e, traceback)
            IsExceptionRaised = True
        else:    
            Message_To_Display = "Error : Get_Next_5_Days_Forecast"
            Build_ErrorMessage(Message_To_Display, e, traceback)
            IsExceptionRaised = True            


###################################################### Fill in the HTTP Request values to pass to the HTML template

def Prepare_Return_HTTP_Request_Values(request):

    global IsExceptionRaised
    global ErrorMessage

    global context


    try:



        

        context = {

            # 'out_curr_icon': city_weather['current']['weather'][0]['icon'],

            'out_curr_icon': out_curr_icon,
            'out_curr_description': out_curr_description,
            'out_curr_temp_min': round(out_curr_temp_min, 1),
            'out_curr_temp_max': round(out_curr_temp_max, 1),
            'out_curr_temp_morn': round(out_curr_temp_morn, 1),
            'out_curr_temp_day': round(out_curr_temp_day, 1),
            'out_curr_temp_night': round(out_curr_temp_night, 1),
            
            'out_curr_wind_speed': out_curr_wind_speed,
            'out_curr_wind_deg': out_curr_wind_deg,
            
            'current_date_time': Curr_DateIime_Formatted,
            'out_curr_sunrise': out_curr_sunrise,
            'out_curr_sunset': out_curr_sunset,
            'sunshine_time_difference_min': '%+d' % request.session['sunshine_time_difference_min'],
            'wifi_class': wifi_icon,

            'ErrorMessageDisplay' : ErrorMessage,


            'out_curr_temp': Sql_out_curr_temp,
            'out_curr_humidity': Sql_out_curr_humidity,
            'out_max_temp': Sql_out_max_value,
            'out_min_temp': Sql_out_min_value,
            'out_battery_level': Sql_out_battery_level,


            'in_curr_temp': Sql_in_curr_temp,
            'in_curr_humidity': Sql_in_curr_humidity,
            'in_max_temp': Sql_in_max_value,
            'in_min_temp': Sql_in_min_value,
            'in_battery_level': Sql_in_battery_level,


            'serre_curr_temp': Sql_serre_curr_temp,
            'serre_curr_humidity': Sql_serre_curr_humidity,
            'serre_max_temp': Sql_serre_max_value,
            'serre_min_temp': Sql_serre_min_value,
            'serre_battery_level': Sql_serre_battery_level,


            'Page_Refresh': PAGE_REFRESH_SECONDS,
            'OpenWeather_Trigger_Counter': OpenWeather_Trigger_Counter,
            'monitoring_OMW_calls': request.session['monitoring_OMW_calls'],

            'Forecasts': Forecasts,

        }

        return context
        




    except Exception as e:
        if ErrorMessage == "":      # do not change the ErrorMessage if it already has a content
            Message_To_Display = "Error : Prepare_Return_HTTP_Request_Values"
            Build_ErrorMessage(Message_To_Display, e, traceback)
            IsExceptionRaised = True 

        context = {
            'ErrorMessageDisplay' : ErrorMessage,
        }
        return context



###################################################### Build the error message in case of exception

def Build_ErrorMessage(Message_To_Display, e, traceback):

    import re

    global ErrorMessage

    re.IGNORECASE
    result = re.search('line (\d+)', traceback.format_exc())
    ErrorMessage = "Error : " + result.group(0) + " : " + Message_To_Display + " -->" + str(e)


