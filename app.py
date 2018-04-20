#import all required modules to run the app.  These must be saved in the same folder as the top level app
#(or python root)
import getInputs
import getResFix
import getStats
import runSAS
import getOdds
import callBetfair
import tidy

#season, current round and previous round generated via popup window
season, cr, pr, dor = getInputs.startMenu()
#get mappings from tidy module (needed to reduce clutter)
rtn, rv = tidy.mappings()

#print some stuff to the log
print 'season: %s' % season
print 'round : %s' % cr
print 'day   : %s' % dor
print '\nOff we go!'

#conditionally process getting the team stats and last weeks results
#(only need to get these on the first day of the round)
if dor == 1:
    #get stats
    getStats.xpCSVs(season,'Round %s' % pr)
    #get all results for the last round
    getResFix.xpCSV(season,pr,rtn,rv)

#get the current rounds fixtures / results
#these will change as the round processes (i.e more results come in)
getResFix.xpCSV(season,cr,rtn,rv)

#run the SAS program to produce the win probability (only on day 1)
#and get the betting bank (all days)
runSAS.winProb(season,dor,cr)

#get the odds from Betfair and TAB
getOdds.xpCSV(season,cr,rtn)

#these will be the actual calls when we have some model results for the year
#run the sas program that uses the Kelly criterion to produce optimal bets
#(sizes based on overlay between odds and generated probability of team winning)
#runSAS.betSize(season,dor,cr)
#push the required data into the Betfair API (automated betting for Betfair only)
#callBetfair.placeOrder(season,dor,cr)

#test calls
runSAS.betSize(2017,2,22)
callBetfair.placeOrder(2017,2,22)
