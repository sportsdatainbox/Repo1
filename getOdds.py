import urllib2, json, pandas as pd,requests,os
import callBetfair

def xpCSV(season,rnd,rtn):

    print '\nCollect odds:'

    def TAB(season,rnd,rtn):
        print '  > Collect odds from TAB API'
        url = 'https://api.beta.tab.com.au/v1/recommendation-service/AFL%20Football/featured?jurisdiction=NSW'
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        jsonResponse = response.read()
        jn = json.loads(jsonResponse)

        DfTeams    = []
        DfOppoents = []
        DfFixture  = []
        DfOdds     = []


        for c in jn['competitions']:
            for c1 in c.get('matches'):
                if c1.get('name').upper().find(' V ') != -1:
                    DfFixture += 2*[c1.get('name')]
                    t = []
                    for c2 in c1.get('markets')[0].get('propositions'):
                        t.append(c2.get('name').upper())
                        DfOdds.append(c2.get('returnWin'))
                    DfTeams.extend(t)
                    DfOppoents.extend(t[::-1])


        df = pd.DataFrame(
            {
             'fixture'     : DfFixture,
             'team_odds_p' : DfOdds,
             'team'        : DfTeams,
             'opponent'    : DfOppoents
             })

        df['team'    ] = df['team'    ].replace(rtn)
        df['opponent'] = df['opponent'].replace(rtn)
        df['round_no'] = rnd
        df['season'  ] = season

        return df

    def Betfair(season,rnd,rtn):
        print '  > Collect Betfair Odds:'
        #login to betfair (get token)
        headers = callBetfair.login()
        #call API

        DfEventIds    = []
        DfEventNames  = []
        DfTeams       = []
        DfOpponents   = []
        DfMarketIds   = []
        MarketIds     = []
        SelectionIds  = []
        SelectionOdds = []

##        print 'Get AFL IDs List....'
        jn = callBetfair.API('{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listEventTypes", "params": {"filter":{}}, "id": 1}',headers)
        eventTypeIds = ",".join([c.get('eventType').get('id').encode("utf-8") for c in jn['result'] if c.get('eventType').get('name') == 'Australian Rules'])
        print '    > Collect event list:'
        jn = callBetfair.API('{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listEvents", "params": {"filter":{"eventTypeIds":['+eventTypeIds+']} }, "id": 1}',headers)

        for c in jn['result']:
            if c.get('event').get('name').find(' v ') != -1:
                DfEventIds   += 2 * [c.get('event').get('id'  ).encode("utf-8")]
                DfEventNames += 2 * [c.get('event').get('name').encode("utf-8")]
                DfTeams.extend(c.get('event').get('name').encode("utf-8").split(' v '))
                DfOpponents.extend(c.get('event').get('name').encode("utf-8").split(' v ')[::-1])

        eventIds = [c.get('event').get('id').encode("utf-8") for c in jn['result'] if c.get('event').get('name').find(' v ') != -1]

        print '      > Collect marketIds:'
        for eventId in eventIds:
##            print 'eventId: ' + eventId
            jn = callBetfair.API('{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketCatalogue", "params": {"filter":{"eventIds":['+eventId +']},"maxResults":"1000"}, "id": 1}',headers)
            for c in jn['result']:
                if c.get('marketName') == 'Match Odds':
                    DfMarketIds += 2* [c.get('marketId').encode("utf-8")]
                    MarketIds.append(c.get('marketId').encode("utf-8"))

        ##marketIds= ",".join([c.get('marketId').encode("utf-8") for c in jn['result'] if c.get('marketName') == 'Match Odds'])
        ##print marketIds

        print '        > Collect selectionIds + odds.'
        for MarketId in MarketIds:
##            print 'Get Market Info For: '+ MarketId
            jn = callBetfair.API('{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketBook", "params": {"marketIds":[' + MarketId + '],"priceProjection":{"priceData":["EX_BEST_OFFERS"]} }, "id": 1}',headers)
            if not jn.get('result'):
                SelectionIds.extend([0,0])
                SelectionOdds.extend([0,0])
            else:
                for c in jn['result']:
                    for c1 in c.get('runners'):
                        SelectionIds.append(c1.get('selectionId'))
                        SelectionOdds.append(c1.get('ex').get('availableToBack')[0].get('price'))

        df = pd.DataFrame(
            {
             'eventId'     : DfEventIds,
             'eventName'   : DfEventNames,
             'team'        : DfTeams,
             'opponent'    : DfOpponents,
             'marketId'    : DfMarketIds,
             'selectionId' : SelectionIds,
             'team_odds'   : SelectionOdds
             })

        df['team'    ] = map(lambda x: x.upper(), df['team'    ])
        df['opponent'] = map(lambda x: x.upper(), df['opponent'])

        df['team'    ] = df['team'    ].replace(rtn)
        df['opponent'] = df['opponent'].replace(rtn)

        df['round_no'] = rnd
        df['season'  ] = season

        return df

    todf = TAB(season,rnd,rtn)
    bodf = Betfair(season,rnd,rtn)

    print '  > Merge odds frames'
    todf.sort_values(by=['season','round_no','team','opponent'], ascending=True, inplace=True)
    bodf.sort_values(by=['season','round_no','team','opponent'], ascending=True, inplace=True)

    bodf = bodf.merge(todf,how='left',on=['season','round_no','team','opponent'])

    bodf = bodf[[
                  'eventId'
                 ,'marketId'
                 ,'selectionId'
                 ,'season'
                 ,'round_no'
                 ,'team'
                 ,'opponent'
                 ,'team_odds'
                 ,'team_odds_p'
                 ]].sort_values(by=[
                                     'eventId'
                                     ,'marketId'
                                     ,'selectionId'
                                     ,'season'
                                     ,'round_no'
                                     ,'team'
                                     ,'opponent'
                                     ], ascending=True)

    bodf[['eventId','marketId']] = bodf[['eventId','marketId']].apply(pd.to_numeric)
    bodf['marketId'] = bodf['marketId'].round(10)

    #check for existence of odds file.  If it is there then take the old file and overwrite it with available odds
    #this will be applicable when we are running the process after the 1st day of the round
    if os.path.isfile('D:/AFL/Model/Data/CSVs/Odds/%s/Round %s.csv' % (season,rnd)):
        oodf = pd.read_csv('D:/AFL/Model/Data/CSVs/Odds/%s/Round %s.csv' % (season,rnd), engine='c', float_precision='round_trip')
        oodf['marketId'] = oodf['marketId'].round(10)
        bodf = bodf.merge(oodf,how='left',on=[
                                               'eventId'
                                              ,'marketId'
                                              ,'selectionId'
                                              ,'season'
                                              ,'round_no'
                                              ,'team'
                                              ,'opponent'
                                              ])
        bodf['team_odds'  ] = bodf.team_odds_x.combine_first(bodf.team_odds_y)
        bodf['team_odds_p'] = bodf.team_odds_p_x.combine_first(bodf.team_odds_p_y)
##        with pd.option_context('display.precision', 10):
##            print bodf
        bodf = bodf[[
                  'eventId'
                 ,'marketId'
                 ,'selectionId'
                 ,'season'
                 ,'round_no'
                 ,'team'
                 ,'opponent'
                 ,'team_odds'
                 ,'team_odds_p'
                 ]]

    bodf.to_csv('D:/AFL/Model/Data/CSVs/Odds/%s/Round %s.csv' % (season,rnd), index=False )
    print '  > Combined odds file sent to CSV'

    return None