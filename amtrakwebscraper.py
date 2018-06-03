import datetime
import requests

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup


def getStationInfo(codeOrLocation):
    pass


def __getStatusUrl():
    return 'https://assistive.amtrak.com/h5/assistive/train-status'


def __getStatusHeader():
    return {'accept'                    : 'text/html',
            'accept-encoding'           : 'gzip, deflate, br',
            'accept-language'           : 'en-US,en-q=0.9',
            'cache-control'             : 'max-age=0',
            'Content-Type'              : 'application/x-www-form-urlencoded',
            'upgrade-insecure-requests' : '1'
            }


def __getStatusForm(arrival, trainNumber, stationCode, stationLocation, date): 
    form = {'action': 'searchTrainStatus'}
    if arrival:
        form['radioSelect'] = 'arrivalTime'
    else:
        form['radioSelect'] = 'departTime'
    form['wdf_trainNumber'] = str(trainNumber)
    form['unStCode_wdf_destination'] = stationCode
    form['wdf_destination'] = stationLocation
    form['departdisplay_train_number'] = '%m/%d/%Y'
    return form


def __getStatusPage(arrival, trainNumber, station, date):
    pass


def getStatus(arrival, trainNumber, station, date):
    if not isinstance(arrival, bool):
        raise ValueError('arrival must be a boolean.')
    elif not isinstance(trainNumber, int):
        raise ValueError('trainNumber must be a integer.')
    elif not isinstance(station, str):
        raise ValueError('station must be a string.')
    elif not isinstance(date, datetime.datetime):
        raise ValueError('date must be a datetime object.')
    pass


if __name__ == '__main__':
    url = 'https://assistive.amtrak.com/h5/assistive/train-status'
    header = {  'accept': 'text/html',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en-q=0.9',
                'cache-control': 'max-age=0',
                'Content-Type': 'application/x-www-form-urlencoded',
                'upgrade-insecure-requests': '1'
            }
    form = {'action': 'searchTrainStatus',
            'radioSelect': 'arrivalTime',
            'wdf_trainNumber': '392',
            'wdf_destination': 'Chicago, IL',
            'unStCode_wdf_destination': 'CHI',
            'departdisplay_train_number': '06/02/2018'
            }
    response = requests.post(url, headers=header, data=form)
    parsedPage = BeautifulSoup(response.content, 'html5lib')
    status = parsedPage.find('div', {'class': 'result-content'})
    print(parsedPage.getText())

