from flask import Flask, render_template, request
from datetime import datetime
import os
import requests
import folium

CURRENT_YEAR = datetime.now().year
API_KEY = os.environ['api_key']

HEADER = {
    'Authorization': f'{os.environ["ipinfo_token"]}',
    'Accept': 'application/json'
}

IP_ADDRESS = '8.8.8.8'

app = Flask(__name__)


class IpInfo:
    def __init__(self, ip_address):
        self.header = HEADER
        self.url = f'https://ipinfo.io/{ip_address}/json'
        self.lat = None
        self.lan = None
        self.city = ''
        self.country = ''
        self.hostname = ''
        self.ip = ''
        self.org = ''
        self.postal = ''
        self.region = ''
        self.timezone = ''
        self.info = True

    def get_info(self):
        response = requests.get(url=self.url, headers=self.header)
        print(response.status_code)
        result = response.json()
        try:
            self.lat = float(result['loc'].rsplit(',', 1)[0])
            self.lan = float(result['loc'].rsplit(',', 1)[1])
            self.city = result['city']
            self.country = result['country']
            self.ip = result['ip']
            self.postal = result['postal']
            self.region = result['region']
            self.timezone = result['timezone']
        except KeyError as ke:
            print(f'{ke}')
            self.info = False
            return

    def create_map(self):
        my_map = folium.Map(location=[self.lat, self.lan], zoom_start=6)
        my_map.save('templates/map.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    global IP_ADDRESS
    if request.method == 'POST':
        IP_ADDRESS = request.form.get('text')
        m = IpInfo(IP_ADDRESS)
        m.get_info()
        if m.info:
            m.create_map()
            return render_template('index.html', current_year=CURRENT_YEAR,
                                   ip_info=m, api_key=API_KEY)
        else:
            return {
                    'Error': 'Please enter valid ip address.'
                }
    m = IpInfo(request.remote_addr)
    m.get_info()
    return render_template('index.html', current_year=CURRENT_YEAR,
                           ip_info=m, api_key=API_KEY)


@app.route('/map')
def render_map():
    if os.path.isfile('templates/map.html'):
        return render_template('map.html')
    else:
        return {
            'Error': 'No Map',
        }


if __name__ == '__main__':
    app.run(debug=True, port=5003, host='0.0.0.0')

