import requests

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup


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

