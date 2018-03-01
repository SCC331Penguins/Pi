import twitter

# Populate the Twitter API keys below
consumer_key = '03IfePawFpKcqIpcGtYKIHV8m'
consumer_secret = 'ZPyQOXTw6V5T0YTdXvtGTkDahObGL5Mn54rMkC9ii1hNzf4k3b'
access_token_key = '967806995381346305-aUvaNrRB8Ad6KmoDDjOO1LfYO8r8p8R'
access_token_secret = '3Wft8NQqHe9nPsrUjoTUisGIJvw1yiXWVsru9Pac0jY5V'

previous = {
    'temperature': 0,
    'humidity': 0,
    'light': -100,
    'tilt_x': 0,
    'tilt_y': 0,
    'motion': 'false',
    'uv': 0,
    'ir': 0,
    'sound': 0,
}

api = twitter.Api(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token_key=access_token_key,
    access_token_secret=access_token_secret)

def send_direct_message(msg, twitter_handle):
    # Send Direct Message to official Twitter handle
    try:
        api.PostDirectMessage(msg, user_id=None, screen_name=twitter_handle)
    except Exception as e:
        print(e)
        tweet_at_user(msg + " \n\nFollow us so we can DM you.", twitter_handle)

def tweet_at_user(msg, twitter_handle):
    # Tweet at official Twitter handle
    try:
        api.PostUpdate(status='@' + twitter_handle+" " + msg)
    except Exception as e:
        print(e)

# ---------------- Notifications ------------------
def humidity_twitter_check(humidity, twitter_handle, photon_id = None):
    try:
        msg = ''
        if (is_not_close(humidity, previous['humidity'])):
            if (photon_id != None):
                msg += photon_id + ' says: '

            if (humidity > 60):
                msg += 'This room appears to be pretty humid. Consider purchasing a dehumidifier.' + \
                       ' Humidity at ' + str(humidity) + '%.'
                send_direct_message(msg, twitter_handle)
            elif (humidity < 30):
                msg += 'This room appears to be pretty dry.' + \
                       ' Humidity at ' + str(humidity) + '%.'
                send_direct_message(msg, twitter_handle)
            print(msg)
        previous['humidity'] = humidity
    except Exception as e:
        print(e)


def temperature_twitter_check(temperature, twitter_handle, photon_id=None):
    try:
        msg = ''
        if(is_not_close(temperature, previous['temperature'])):
            if (photon_id != None):
                msg += photon_id + ' says: '

            if (temperature > 10):
                msg += 'Temperature readings in this room are extremely high. Are you sure you are not on the sun?' + \
                       ' Temperature is ' + str(temperature) + 'C.'
                send_direct_message(msg, twitter_handle)

            elif (temperature > 40):
                msg += 'This room appears to be pretty hot. Could we interest you in a smart fan?' + \
                       ' Temperature at ' + str(temperature) + 'C.'
                send_direct_message(msg, twitter_handle)

            elif (temperature < 10):
                msg += 'This room appears to be pretty cold. Maybe a radiator could be of use to you.' + \
                       ' Temperature at ' + str(temperature) + 'C.'
                send_direct_message(msg, twitter_handle)

            print(msg)
        previous['temperature'] = temperature
    except Exception as e:
        print(e)

def light_twitter_check(light, twitter_handle, photon_id=None):
    try:
        msg = ''
        if(is_not_close(light, previous['light'])):
            if (photon_id != None):
                msg += photon_id + ' says: '

            if (light > 50):
                msg += 'Your room is quite bright right now. Consider turning a few lights off to conserve energy.' + \
                       ' Light levels at ' + str(light) + 'lux.'
                send_direct_message(msg, twitter_handle)

            elif (light < 0):
                msg += 'Your room is quite dark.' + \
                       ' Light levels at ' + str(light) + 'lux.'
                send_direct_message(msg, twitter_handle)

            print(msg)
        previous['light'] = light
    except Exception as e:
        print(e)

def sound_twitter_check(sound, twitter_handle, photon_id=None):
    try:
        msg = ''
        if(is_not_close(sound, previous['sound'])):
            if (photon_id != None):
                msg += photon_id + ' says: '

            if (sound > 50):
                msg += 'I have detected loud sound levels in this room. I feel sorry for your neighbours.' + \
                       ' Sound levels at ' + str(sound) + 'dB.'
                send_direct_message(msg, twitter_handle)

            elif (sound < 0):
                msg += 'Your room appears to be very quiet at the moment.' + \
                       ' Sound levels at ' + str(sound) + 'dB.'
                send_direct_message(msg, twitter_handle)

            print(msg)
        previous['sound'] = sound
    except Exception as e:
        print(e)

def motion_twitter_check(motion, twitter_handle, photon_id=None):
    try:
        msg = ''
        if(motion == previous['motion']):
            if (photon_id != None):
                msg += photon_id + ' says: '
            msg += 'Motion Detected in this room.'
            send_direct_message(msg, twitter_handle)
            print(msg)
        previous['motion'] = motion
    except Exception as e:
        print(e)

def tilt_x_twitter_check(tilt_x, twitter_handle, photon_id=None):
    try:
        msg = ''
        if(is_not_close(tilt_x, previous['tilt_x'])):
            if (photon_id != None):
                msg += photon_id + ' says: I was tilted!'
            else:
                msg += 'Sensor was tilted'
            send_direct_message(msg, twitter_handle)
            print(msg)
        previous['tilt_x'] = tilt_x
    except Exception as e:
        print(e)

def tilt_y_twitter_check(tilt_y, twitter_handle, photon_id=None):
    try:
        msg = ''
        if(is_not_close(tilt_y, previous['tilt_y'])):
            if (photon_id != None):
                msg += photon_id + ' says: I was tilted!'
            else:
                msg += 'Sensor was tilted'
            send_direct_message(msg, twitter_handle)
            print(msg)
        previous['tilt_y'] = tilt_y
    except Exception as e:
        print(e)


def uv_twitter_check(uv, twitter_handle, photon_id=None):
    try:
        msg = ''
        if(is_not_close(uv, previous['uv'])):
            if (photon_id != None):
                msg += photon_id + ' says: '

            if (uv > 10):
                msg += 'Ultra Violet levels in the room are extremely high. Are you sure you are not on the sun?' + \
                       ' UV levels at ' + str(uv) + ' lux.'
                send_direct_message(msg, twitter_handle)

            elif (uv > 7):
                msg += 'Your room appears to have high Ultra Violet levels.' + \
                       ' UV levels at ' + str(uv) + ' lux.'
                send_direct_message(msg, twitter_handle)

            elif (uv < 4):
                msg += 'I am getting low Ultra Violet readings from this room.' + \
                       ' UV levels at ' + str(uv) + ' lux.'
                send_direct_message(msg, twitter_handle)

            print(msg)
        previous['uv'] = uv
    except Exception as e:
        print(e)


def if_twitter_check(ir, twitter_handle, photon_id=None):
    try:
        msg = ''
        if (is_not_close(ir, previous['uv'])):
            if (photon_id != None):
                msg += photon_id + ' says: '

            if (ir > 10):
                msg += 'I am detecting high Infrared Readings from this room.' + \
                       ' IR levels at ' + str(ir) + ' lux.'
                send_direct_message(msg, twitter_handle)

            elif (ir < 4):
                msg += 'I am getting low Infrared readings from this room.' + \
                       ' IR levels at ' + str(ir) + ' lux.'
                send_direct_message(msg, twitter_handle)

            print(msg)
        previous['ir'] = ir
    except Exception as e:
        print(e)


def is_not_close(new, old):
    # check range
    if(new < old-5 or new > old + 5):
        return True
    else:
        return False


if __name__ == '__main__':
    humidity_twitter_check(61, 'EduardSchlotter', 'Yeezy')
    humidity_twitter_check(20, 'EduardSchlotter', 'Yeezy')

    #send_direct_message("Test Message", 'EduardSchlotter')
    #tweet_at_user("Test Message", 'EduardSchlotter')
