import datetime
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-i", "--ingresso",
                  dest="ingresso",
                  default="",
                  help="Orario di ingresso (esempio: 09:00)")
parser.add_option("-u", "--uscita",
                  dest="uscita",
                  default="",
                  help="Orario di uscita presunto per fare calcoli (esempio: 17:00)")
(options, args) = parser.parse_args()
print
if len(args)<1:
    try:
        entrata=datetime.datetime.strptime(options.ingresso, "%H:%M")
    except:
        print "Non hai fornito un orario di ingresso!"
        exit()
else:
    entrata=datetime.datetime.strptime(args[0], "%H:%M")

a=(datetime.datetime.now()-entrata)
print "Sei in servizio da",str(a.seconds/60/60),
if (a.seconds/60/60) == 1:
    print "ora e",
else:
    print "ore e",
print str(a.seconds/60%60),
if (a.seconds/60%60) == 1:
    print "minuto."
else:
    print "minuti."
uscita=entrata+datetime.timedelta(0,60*60*7+42*60)
ticket=entrata+datetime.timedelta(0,60*60*6+30*60)
left_h=(uscita - datetime.datetime.now()).seconds/60/60
left_m=(uscita - datetime.datetime.now()).seconds/60%60
print "\nDovresti uscire alle", datetime.datetime.strftime(uscita,"%H:%M,"),
if left_h==1:
    print "\nmancano "+str(left_h)+" ora e",
else:
    print "\nmancano "+str(left_h)+" ore e",
if left_m==1:
    print str(left_m)+" minuto,"
else:
    print str(left_m)+" minuti,"

print "maturerai il ticket alle "+datetime.datetime.strftime(ticket,"%H:%M.")
if not options.uscita == "":
    previsione_uscita=datetime.datetime.strptime(options.uscita, "%H:%M")
    minuti_fatti=(previsione_uscita-entrata) 
    print "\nSe uscirai alle "+options.uscita+" avrai lavorato: "+str(minuti_fatti)[:-6]+" ore e "+str(minuti_fatti)[-5:-3],
    if int(str(minuti_fatti)[-5:-3])==1:
        print "minuto",
    else:
        print "minuti",
    if minuti_fatti>=datetime.timedelta(0, 23400):
        print "(OK TICKET)."
    else:
        print "(NO TICKET!!!)."
print




