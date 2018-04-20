#import the required modules
import urllib2, json, pandas as pd,requests

def xpCSV(season,rnd,rtn,rv):
    """
    Used to pull json files from a backdoor in the AFL website into CSV files
    which are then used in the SAS data build (saves me doing it manually).
    """
    print '\nCollect fixtures / results from http://www.afl.com.au/:'

    #standard urllib2 request for JSON / load of data
    url = 'http://www.afl.com.au/aflrender/get?params=seasonId?:CD_S%s014,roundId?:CD_R%s014%s,competitionType?:AFL&service=fullFixture&field=json&site=AFL&instart_disable_injection=true' % (season,season,"%02d" % (rnd,))
    req          = urllib2.Request(url)
    response     = urllib2.urlopen(req)
    jsonResponse = response.read()
    jn           = json.loads(jsonResponse)

    #get JSON into structured dataframe then send it to a CSV,  Use lists and get method
    DfDate           = []
    DfFixture        = []
    DfTeams          = []
    DfTeamPoints     = []
    DfOpponents      = []
    DfOpponentPoints = []
    DfVenue          = []
    DfRound          = []

    for c in jn['fixtures']:
        DfDate    += 2*[c.get('match').get('startDateTimes')[0].get('date')]
        DfFixture += 2*[c.get('homeTeam').get('teamName') + ' v ' + c.get('awayTeam').get('teamName')]
        DfVenue   += 2*[c.get('match').get('venueAbbr'  )]
        DfRound   += 2*[c.get('match').get('roundNumber')]

        DfTeams.append(         c.get('homeTeam').get('teamName'  ).upper())
        DfTeamPoints.append(    c.get('homeTeam').get('totalScore')        )
        DfOpponents.append(     c.get('awayTeam').get('teamName'  ).upper())
        DfOpponentPoints.append(c.get('awayTeam').get('totalScore')        )

        DfTeams.append(         c.get('awayTeam').get('teamName'  ).upper())
        DfTeamPoints.append(    c.get('awayTeam').get('totalScore')        )
        DfOpponents.append(     c.get('homeTeam').get('teamName'  ).upper())
        DfOpponentPoints.append(c.get('homeTeam').get('totalScore')        )

    df = pd.DataFrame(
        {
          'date'           : DfDate
         ,'fixture'        : DfFixture
         ,'venue'          : DfVenue
         ,'round'          : DfRound
         ,'team'           : DfTeams
         ,'opponent'       : DfOpponents
         ,'points_for'     : DfTeamPoints
         ,'points_against' : DfOpponentPoints
         })

    df['team'    ] = df['team'    ].replace(rtn)
    df['opponent'] = df['opponent'].replace(rtn)
    df['venue'   ] = df['venue'   ].replace(rv )
    df['season'  ] = season

    df = df[['date','fixture','venue','season','round','team','opponent','points_for','points_against']]
    df.to_csv('D:/AFL/Model/Data/CSVs/Results/%s/Round %s.csv' % (season,rnd), index=False )

    print '  > Round ' + str(rnd) + ' sent to csv: D:/AFL/Model/Data/CSVs/Results/%s/Round %s.csv' % (season,rnd)

    return None