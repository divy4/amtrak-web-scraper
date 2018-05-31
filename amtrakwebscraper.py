import requests

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup


if __name__ == '__main__':
    url = 'https://assistive.amtrak.com/h5/assistive/train-status'
    post = {'action': 'searchTrainStatus',
            'radioSelect': 'arrivalTime',
            'wdf_trainNumber': '392',
            'wdf_destination': 'Chicago, IL',
            'unStCode_wdf_destination': 'CHI',
            'departdisplay_train_number': '05/27/2018'
            }
    response = requests.post(url, json=post)
    parsedPage = BeautifulSoup(response.content)
    status = parsedPage.body.find('div', attrs={'class': 'result-label'})
    print(status)
