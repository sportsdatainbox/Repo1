import urllib2, json, requests,pandas as pd

def login():
    """
    Used to login to the Betfair API - return the required headers
    so that other functions can be used to talk to the API
    """
    payload = {
                'username' : 'mattseddon@hotmail.com'
               ,'password' : ''
               }

    headers = {'X-Application': 'U1tJ6hfuIid95IJG', 'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.post('https://identitysso.betfair.com/api/certlogin', data=payload, cert=('C:/Program Files (x86)/OpenSSL-Win32/bin/certs/client-2048.crt', 'C:/Program Files (x86)/OpenSSL-Win32/bin/certs/client-2048.key'), headers=headers)

    if r.status_code == 200:
        resp_json = r.json()
        print '    > login status: ' + resp_json['loginStatus'].lower()
        token = resp_json['sessionToken']
    else:
        print "    > Request failed."

    headers = {'X-Application': 'U1tJ6hfuIid95IJG', 'X-Authentication': token, 'content-type': 'application/json'}

    return headers

def API(jsonrpc_req,headers):
    """
    Used to communicate with the Betfair API.  Will return a JSON response when the correct JSON is posted
    otherwise will return an error
    """
    try:
        req = urllib2.Request("https://api.betfair.com/exchange/betting/json-rpc/v1", jsonrpc_req, headers)
        response = urllib2.urlopen(req)
        jsonResponse = response.read()
        jn = json.loads(jsonResponse)
        return jn
    except urllib2.URLError:
        print 'Oops no service available at ' + str(url)
        exit()
    except urllib2.HTTPError:
        print 'Oops not a valid operation from the service ' + str(url)
        exit()

def placeOrder(season,dor,rnd):
    """
    Used to automatically generate bets via the Betfair API
    NOT CURRENTLY SETUP TO COMMUNICATE AS THAT COSTS MONEY
    """
    bdf = pd.read_csv('D:/AFL/Model/Data/CSVs/Bets/%s/betfair_%s_%s_%s.csv' %(season,season,rnd,dor))
    bdf['selectionId'] = bdf['selectionId'].astype(int)

    #login to betfair (get token)
    headers = login()

    for (idx, row) in bdf.iterrows():
        #print(row.marketId)
        #print(row.index)
        order = \
                '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/placeOrders", "params": '                           + \
                      '{ '                                                                                          + \
                        '"marketId":"' + str(row['marketId'])                                                       + \
                      '","instructions":['                                                                          + \
                                          '{"selectionId":"' + str(row['selectionId']) + '"'                        + \
                                          ',"handicap":"0","side":"BACK","orderType":"LIMIT","limitOrder":'         + \
                                          '{"size":'+ str(row['risk'])                                              + \
                                          ',"price":'+str(row['odds'])                                              + \
                                          ',"persistenceType":"LAPSE"}}'                                            + \
                                         ']'                                                                        + \
                      ',"customerRef":"'+"".join(row['team'].split())+'|'+str(row['odds'])+'|'+str(row['risk'])+'"' + \
                      '}, "id": 1}'
        #jn = API(order)
        #print jn
        print order

