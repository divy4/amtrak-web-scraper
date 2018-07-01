import datetime
import math
import pytz
import requests

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup


__DAY_DELTA = datetime.timedelta(days=2)


''' Converts a BeautifulSoup object to a ascii string.
    @param [object] bs A BeautifulSoup object.
    @return [string] A string.
'''
def beautifulSoupToStr(bs):
    text = bs.getText()
    return str(text.encode('ascii', 'ignore'))[2:-1]


''' Tries to resolve a station by its code or location.
    @param [string] codeOrLoc   The station code OR the city the station is in.
    @return [string, string, string]    The station code, the city the station is in, the time station's time zone.
'''
def getStationInfo(codeOrLoc):
    # TODO: support more stations
    if codeOrLoc == 'CHI' or codeOrLoc == 'Chicago, IL':
        return 'CHI', 'Chicago, IL', pytz.timezone('US/Central')
    elif codeOrLoc == 'CHM' or codeOrLoc == 'Champaign, IL':
        return 'CHM', 'Champaign, IL', pytz.timezone('US/Central')
    elif codeOrLoc == 'RTL' or codeOrLoc == 'Rantoul, IL':
        return 'RTL', 'Rantoul, IL', pytz.timezone('US/Central')
    raise NotImplementedError('Unable to resolve station!')


''' Combines the date, time, and time zone into a datetime object.
    @param [datetime]   date        The date the train is arriving/departing.
    @param [string]     timeStr     The time string from the page text.
    @param [timezone]   timezone    The timezone the station is in.
'''
def __timeToDatetime(date, timeStr, timezone):
    if len(timeStr) == 7:
        timeStr = '0' + timeStr
    time = datetime.datetime.strptime(
        '{} {}'.format(date.strftime('%Y-%m-%d'), timeStr),
        '%Y-%m-%d %I:%M %p')
    return timezone.localize(time)


''' Gets the url of the train statis page.
    @return [string] A url.
'''
def __getStatusUrl():
    return 'https://assistive.amtrak.com/h5/assistive/train-status'


''' Gets the header for requesting a train's status.
    @return [dict(string, string)]
'''
def __getStatusHeader():
    return {'accept'                    : 'text/html',
            'accept-encoding'           : 'gzip, deflate, br',
            'accept-language'           : 'en-US,en-q=0.9',
            'cache-control'             : 'max-age=0',
            'Content-Type'              : 'application/x-www-form-urlencoded',
            'upgrade-insecure-requests' : '1'
            }


''' Gets the form for requesting a train's status.
    @param [bool] arrival               True if requesting the arrival status, False for departure.
    @param [int] trainNumber            The number of the train.
    @param [string] stationCode         The code of the station.
    @param [string] stationLoc          The location of the station. e.g. 'Chicago, IL'
    @param [datetime.datetime] date     The date to query.
    @return [dict(string, string)]      The form.
'''
def __getStatusForm(arrival, trainNumber, stationCode, stationLoc, date): 
    form = {'action': 'searchTrainStatus'}
    if arrival:
        form['radioSelect'] = 'arrivalTime'
    else:
        form['radioSelect'] = 'departTime'
    form['wdf_trainNumber'] = str(trainNumber)
    form['unStCode_wdf_destination'] = stationCode
    form['wdf_destination'] = stationLoc
    form['departdisplay_train_number'] = date.strftime('%m/%d/%Y')
    return form


''' Gets the train status page.
    @param [bool] arrival               True if requesting the arrival status, False for departure.
    @param [int] trainNumber            The number of the train.
    @param [string] stationCode         The code of the station.
    @param [string] stationLoc          The location of the station.
    @param [datetime.datetime] date     The date to query.
    @return [BeautifulSoup]             The page.
'''
def __getStatusPage(arrival, trainNumber, stationCode, stationLoc, date):
    # setup request info
    url = __getStatusUrl()
    header = __getStatusHeader()
    form = __getStatusForm(arrival, trainNumber, stationCode, stationLoc, date)
    # get page
    response = requests.post(url, headers=header, data=form)
    return BeautifulSoup(response.content, 'html5lib')


''' Gets the status of a train.
    @param [bool] arrival               True if requesting the arrival status, False for departure.
    @param [int] trainNumber            The number of the train.
    @param [string] station             The code or location of the station.
    @param [datetime.datetime] date     The date to query.
    @return [dict]                      The status of the train. None if an error occurred while parsing.
'''
def getStatus(arrival, trainNumber, station, date):
    if not isinstance(arrival, bool):
        raise ValueError('arrival must be a boolean.')
    elif not isinstance(trainNumber, int):
        raise ValueError('trainNumber must be a integer.')
    elif not isinstance(station, str):
        raise ValueError('station must be a string.')
    elif not isinstance(date, datetime.datetime):
        raise ValueError('date must be a datetime object.')
    code, location, timezone = getStationInfo(station)
    page = __getStatusPage(arrival, trainNumber, code, location, date)
    # find each piece of the status
    rawStatus = page.find('div', {'class': 'result-content'})
    status = {}
    status['station']       = rawStatus.find('div', {'class': 'result-stations'})
    status['scheduledTime'] = rawStatus.find('div', {'class': 'result-scheduled'})
    status['expectedTime']  = rawStatus.find('div', {'class': 'result-time'})
    status['difference']    = rawStatus.find('div', {'class': 'result-primary'})
    # normalize data
    for key, value in status.items():
        status[key] = beautifulSoupToStr(value).replace('Scheduled', '')
        if 'time' in key.lower():
            status[key] = __timeToDatetime(date, status[key], timezone)
    # Make sure expected arrival time is no more than half a day early.
    diff = status['expectedTime'] - status['scheduledTime']
    if diff <= -0.5 * __DAY_DELTA:
        status['expectedTime'] = status['expectedTime'] + math.ceil(diff / __DAY_DELTA) * __DAY_DELTA
    # include extra info
    status['isArrival'] = arrival
    status['stationCode'] = code
    status['stationLocation'] = location
    status['trainNumber'] = trainNumber
    return status


if __name__ == '__main__':
    status = getStatus(True, 392, 'CHI', datetime.datetime.now())
    if status is not None:
        for label, value in status.items():
            print(label + ' : ' + str(value))

