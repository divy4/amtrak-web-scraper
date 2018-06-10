import datetime
import requests

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup


''' Converts a BeautifulSoup object to a ascii string.
    @param [object] bs A BeautifulSoup object.
    @return [string] A string.
'''
def beautifulSoupToStr(bs):
    text = bs.getText()
    return str(text.encode('ascii', 'ignore'))


''' Tries to resolve a station by its code or location.
    @param [string] codeOrLoc   The station code OR the city the station is in.
    @return [string, string]    The station code AND the city the station is in.
'''
def getStationInfo(codeOrLoc):
    # TODO: support more stations
    if codeOrLoc == 'CHI' or codeOrLoc == 'Chicago, IL':
        return 'CHI', 'Chicago, IL'
    elif codeOrLoc == 'CHM' or codeOrLoc == 'Champaign, IL':
        return 'CHM', 'Champaign, IL'
    elif codeOrLoc == 'RTL' or codeOrLoc == 'Rantoul, IL':
        return 'RTL', 'Rantoul, IL'
    raise NotImplementedError('Unable to resolve station!')


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
    @param [string] station             The code or location of the station.
    @param [datetime.datetime] date     The date to query.
    @return [BeautifulSoup]             The page.
'''
def __getStatusPage(arrival, trainNumber, station, date):
    # setup request info
    code, loc = getStationInfo(station)
    url = __getStatusUrl()
    header = __getStatusHeader()
    form = __getStatusForm(arrival, trainNumber, code, loc, date)
    # get page
    response = requests.post(url, headers=header, data=form)
    return BeautifulSoup(response.content, 'html5lib')


''' Gets the status of a train.
    @param [bool] arrival               True if requesting the arrival status, False for departure.
    @param [int] trainNumber            The number of the train.
    @param [string] station             The code or location of the station.
    @param [datetime.datetime] date     The date to query.
    @return [dict]                      The status of the train.
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
    page = __getStatusPage(arrival, trainNumber, station, date)
    # find each piece of the status
    rawStatus = page.find('div', {'class': 'result-content'})
    if rawStatus is None:
        return None
    status = {}
    status['station']       = rawStatus.find('div', {'class': 'result-stations'})
    status['scheduledTime'] = rawStatus.find('div', {'class': 'result-scheduled'})
    status['expectedTime']  = rawStatus.find('div', {'class': 'result-time'})
    status['difference']    = rawStatus.find('div', {'class': 'result-primary'})
    # normalize data to strings
    for key, value in status.items():
        status[key] = beautifulSoupToStr(value)
    return status


if __name__ == '__main__':
    status = getStatus(True, 3924, 'RTL', datetime.datetime.now())
    if status is not None:
        for label, value in status.items():
            print(label + ':')
            print(type(value))
            print(value)
            print('')
