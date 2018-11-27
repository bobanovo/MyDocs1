import urllib
import urllib2
import simplejson as json


url = 'http://0.0.0.0:8000/api2/auth-token/'
values = {'username': 'radek@bobanovo.cz',
          'password': 'bobanek'}
data = urllib.urlencode(values)
req = urllib2.Request(url, data)
response = urllib2.urlopen(req)
the_page = response.read()
token = json.loads(the_page)['token']

print (token)


