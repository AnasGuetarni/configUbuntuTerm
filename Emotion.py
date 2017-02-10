########### Python 2.7 #############
import httplib, urllib, base64

headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': 'b00404132a5e42ed82d9c72f5ea4ed83',
}

params = urllib.urlencode({
})

try:
    conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
    conn.request("POST", "/emotion/v1.0/recognize?%s" % params, "{'url':'https://leperversnarcissique.files.wordpress.com/2015/01/enfanttriste-pn2.jpg?w=720'}", headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))

