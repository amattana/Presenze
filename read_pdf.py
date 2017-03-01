import datetime
import os, time, sys
from optparse import OptionParser


def data(turno):
    return turno[turno.find('/')-2:turno.find('/')+8]

def isIeri(data1, data2):
    if data2<data1 and (data1-data2).days==1:
        return True
    else:
        return False

def ingresso(turno):
    if occorrenze(turno,'E')==1:
        return turno[turno.find('E'):turno.find('E')+6]
    # Caso particolare, hai timbrato anche in entrata con verso USCITA
    # Sicuramente la prima uscita sara' un ingresso
    elif occorrenze(turni[i],'U')==2:
        return turni[i][turni[i].find('U'):turni[i].find('U')+6]
    else:
        return ""

def uscita(turno):
    if occorrenze(turno,'U')==1:
        return turno[turno.find('U'):turno.find('U')+6]
    # Caso particolare, hai timbrato anche in uscita con verso ENTRATA
    # Sicuramente la seconda entrata sara' un uscita
    elif occorrenze(turni[i],'E')==2:
        pos=turni[i].find('E',pos)+1
        return turni[i][turni[i].find('E',pos):turni[i].find('E',pos)+6]
    else:
        return ""

def occorrenze(riga, chiave):
    n=0
    pos=0
    #riga=riga.split(',')[0]
    while pos<len(riga) and riga.find(chiave, pos)>-1:
        n=n+1
        pos=riga.find(chiave, pos)+1
    return n

def correggi_doppi_turni(turni):
    i=0
    nuova=[]
    for i in xrange(len(turni)):
        if isDoppioTurno(turni[i]):
            nuova += [turni[i][:54]+"Turno"]
            nuova += [turni[i][54:]]
        else:
            nuova += [turni[i]]
    return nuova

def inserisci(lista, record, pos):
    i=0
    nuova = []
    while i<pos and i<(len(lista)):
        nuova += [lista[i]]
        i=i+1
    nuova += [record]
    while i<(len(lista)):
        nuova += [lista[i]]
        i=i+1
    return nuova

def isDoppioTurno(turno):
    if occorrenze(turno,'(67)')==4 and occorrenze(turno,'Turno')==1 and occorrenze(turno,'E')==2 and occorrenze(turno,'U')==2:
        return True
    else:
        return False

def seq_turni(turno):
    pos=0
    seq=""
    while ((turno.find('E',pos)>-1) or (turno.find('U',pos)>-1)):
        if ((turno.find('E',pos)>-1) and (turno.find('U',pos)>-1)):
            if (turno.find('E',pos))<(turno.find('U',pos)):
                seq += 'E'
                pos = turno.find('E',pos) +1
            else:
                seq += 'U'
                pos = turno.find('U',pos) +1
        else:
            if (turno.find('E',pos)>-1):
                seq += 'E'
                pos = turno.find('E',pos) +1
            else:
                seq += 'U'
                pos = turno.find('U',pos) +1
    return seq

def correggi_turni(turni):        
    i=0
    nuova=[]  
    for i in xrange(len(turni)):
        seq = seq_turni(turni[i])
        while len(seq)>0:
            if seq.find('E')==0 and seq.find('U')==1:
                nuova += [turni[i][:54]+"Turno"]
                turni[i] = turni[i][54:]
                seq=seq[2:]
            elif seq.find('U')==0:
                nuova += [", "+turni[i][:27]+"Turno"]
                turni[i] = turni[i][27:]
                seq=seq[1:]
            elif seq.find('E')==0 and len(seq)==1:
                nuova += [turni[i][:26]+" , Turno"]
                seq=seq[1:]
            elif seq.find('E')==0 and len(seq)>2:
                nuova += [turni[i][:26]+" , Turno"]
                turni[i] = turni[i][27:]
                seq=seq[1:]
    return nuova

def isDomani(data1, data2):
    if data2>data1 and (data2-data1).days==1:
        return True
    else:
        return False

def accorpa_turni(t):
    nuova = []
    i=0
    noskip=True
    while i<len(t)-1:
        if noskip:
            if not t[i].split(',')[0]=='':
                oggi=datetime.datetime.strptime(t[i].split(',')[0][4:14], "%d/%m/%Y")
                if not t[i+1].split(',')[1]==' ':
                    domani = datetime.datetime.strptime(t[i+1].split(',')[1][5:15], "%d/%m/%Y")
                    if t[i].split(',')[1]==' ' and t[i+1].split(',')[0]=='' and isDomani(oggi, domani):
                        nuova += [t[i][:26]+t[i+1].split(',')[1][:26]+", Turno"]
                        noskip=False
                        i=i+1
                    else:
                        nuova += [t[i]]
                        i=i+1
                else:
                    nuova += [t[i]]
                    i=i+1
            else:
                nuova += [t[i]]
                i=i+1
        else:
            i=i+1
            noskip=True
    if noskip: 
        nuova += [t[i]]
    return nuova

def stampa(lista):
    for i in xrange(len(lista)):
        print str(i+1)+". "+lista[i].replace('\r','').replace(',',' ').replace('\n','').replace('    ',' ').replace('   ',' ').replace('  ',' ').split('\"')[0]

def stampa_turni(lista):
    for i in xrange(len(lista)):
        print str(i+1)+". "+lista[i]+", durata "+calcola_ore(lista[i])

def _calcola_ore(riga):
    entra = datetime.datetime.strptime(riga.split(',')[0], "%d/%m/%Y E%H:%M")
    esce = datetime.datetime.strptime(riga.split(',')[1], " %d/%m/%Y U%H:%M")
    ore = (esce - entra).seconds/60/60
    minuti = (esce - entra).seconds/60%60
    return str(ore)+":"+str(minuti).zfill(2)

def _calcola_dnf(riga):
    entra = datetime.datetime.strptime(riga.split(',')[0], "%d/%m/%Y E%H:%M")
    esce = datetime.datetime.strptime(riga.split(',')[1], " %d/%m/%Y U%H:%M")
    orario = entra
    ore_diurne = ore_notturne = ore_festive = 0 
    while orario < esce:
        if diurno(orario):
            ore_diurne = ore_diurne + 1
        elif notturno(orario):
            ore_notturne = ore_notturne + 1
        elif festivo(orario):
            ore_festive = ore_festive + 1
        orario = orario + datetime.timedelta(0,60)
    return ore_diurne, ore_notturne, ore_festive

def _calcola_mese(turni):
    #print turni
    ore_diurne = ore_notturne = ore_festa = 0
    for i in xrange(len(turni)):
        giorno, notte, festa = calcola_dnf(turni[i])
        #print giorno, notte, festa
        ore_diurne = ore_diurne + giorno 
        ore_notturne = ore_notturne + notte 
        ore_festa = ore_festa + festa 
    #print ore_diurne, ore_notturne, ore_festa
    return ore_diurne, ore_notturne, ore_festa
    
def _stampa_oremin(ore):
    #print ore
    msg=str(ore/60)
    if (ore/60) == 1:
        msg += " ora e "+str(ore%60)
    else:
        msg += " ore e "+str(ore%60)
    if (ore%60) == 1:
        msg += " minuto"
    else:
        msg += " minuti"
    return msg 

def analizza(pdf_file):

#parser = OptionParser()
#parser.add_option("-f", "--pdffile",
#                  dest="pdf_file",
#                  default="",
#                  help="File PDF del cartellino")
#(options, args) = parser.parse_args()

    #print pdf_file
    os.system("java -jar tabula-0.9.1-jar-with-dependencies.jar -d -n "+pdf_file+" -o test.txt")

    csv=open("test.txt",'r')
    record=csv.readlines()
    csv.close()
    #print record

    # Looking for "Giorno,Timbrature,,Stato giornata," line
    i=0
    trova=True
    while trova:
        if record[i][:6]=="Giorno":
            trova=False
        else:
            i=i+1
    i=i+1

    multiriga = False
    records=[]
    trova=True
    n=0
    while trova:
        #time.sleep(0.1)
        #print i, multiriga, record[i][:3], record[i][:-2] 
        # Giorno ordinario
        if record[i][:3]=='Lun' or record[i][:3]=='Mar' or record[i][:3]=='Mer' or record[i][:3]=='Gio' or record[i][:3]=='Ven' or record[i][:3]=='Sab' or record[i][:3]=='Dom':
            if not multiriga:
                records += [record[i].split('\n')[0]]
                i=i+1
            else:
                records += [record[i]+record[i-1]+record[i+1]]
                multiriga = False
                i=i+2

        # Mese finito
        elif record[i].find('Causali')>-1 or record[i].find('CONSUNTIVO')>-1:
            trova=False
 
        # Orari distribuiti su + righe
        else:
            if record[i][:1]=='E' or record[i][:1]=='U':
                multiriga = True
            i=i+1

    #print "----------------------------------\n"
    #if record[i].find('CONSUNTIVO')>-1:
        #print record[2].split("-")[0]+" - "+record[i].split(',')[0]+"\n"
    #else:
        #print record[2].split("-")[0]+" - "+record[i+1].split(',')[0]+"\n"
    #stampa(records)
    #print "----------------------------------"
    turni=[]
    for i in xrange(len(records)):
        pos=0
        if records[i].find('(67)')>-1:
            turno=""
            trovato = 0
            while records[i].find('(67)',pos)>-1:
                turno += records[i][:14]+" "+records[i][records[i].find('(67)',pos)-6:records[i].find('(67)',pos)+4]+", "
                pos=records[i].find('(67)',pos)+4
                trovato = trovato +1
            if trovato == 1:
                turno += " , "
            if records[i].find('Turno')>-1:
                turno += records[i][records[i].find('Turno'):records[i].find('Turno')+5]
            turni += [turno]

    #Correzione doppia U o doppia E
    for i in xrange(len(turni)):
        # Doppia U
        if occorrenze(turni[i], 'E')==0 and occorrenze(turni[i], 'U')==2:
            turni[i] = turni[i][:turni[i].find('U')]+'E'+turni[i][turni[i].find('U')+1:]
        # Doppia E
        if occorrenze(turni[i], 'E')==2 and occorrenze(turni[i], 'U')==0:
            pos=turni[i].find('E')
            turni[i] = turni[i][:turni[i].find('E',pos+1)]+'U'+turni[i][turni[i].find('E',pos+1)+1:]

    # Correzione uscita e rientro durante turno
    #print turni
    turni = correggi_turni(turni) 
    #print turni 
    if len(turni)>1:
        turni = accorpa_turni(turni)
    #print turni

    #print record

    fname=datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(time.time()), "%Y%m%d%H%M%s.dat")
    foo = open('dati_cartellini/'+fname,'w')
    foo.write("[user]\n")
    foo.write(record[2].split('-')[0][14:-1]+"\n")
    for i in xrange(len(record)):
        if record[i][:10]=='CONSUNTIVO':
            foo.write(record[i].split(',')[0].split('di')[1][1:]+"\n")
    foo.write(record[2].split(',')[0].split('-')[1][7:]+"\n")
    foo.write(pdf_file+"\n\n")
    foo.write("[cod.67]\n")
    for i in xrange(len(turni)):
        foo.write(str(i+1)+". "+turni[i].replace('\r','').replace('\n','').replace('    ',' ').replace('   ',' ').replace('  ',' ').split('\"')[0]+"\n")
    foo.close()
    #print fname[:-4]
    return fname[:-4]   


 
    #print
    turni_corretti=[]
    for i in xrange(len(turni)):
        if occorrenze(turni[i],'E')>0 and occorrenze(turni[i],'Turno')>0 and occorrenze(turni[i],'U')>0:
            turni_corretti += [data(turni[i])+" "+ingresso(turni[i])+", "+data(turni[i])+" "+uscita(turni[i])+", Turno"]
        elif turni[i].find('Turno')>-1:
            if turni[i].find('U')>-1:
                #print i,turni[i],giorno(i-1),ingresso(i-1),giorno(i),uscita(i) 
                turni_corretti += [data(turni[i-1])+" "+ingresso(turni[i-1])+", " + data(turni[i])+" "+ uscita(turni[i])+", Turno"]
            elif turni[i].find('E')>-1:
                turni_corretti += [data(turni[i])+" "+ingresso(turni[i])+", " + data(turni[i+1])+" "+ uscita(turni[i+1])+", Turno"]
            else:
                print "Ho trovato un caso non ancora implementato",turni[i]
        #else:
        #    print "Ho trovato un caso non ancora implementato",turni[i]

    print "----------------------------------"
    print "\nTurni corretti:\n"
    stampa_turni(turni_corretti)
    print "\n----------------------------------"

    fname=datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(time.time()), "%Y%m%d%H%M%s.dat")
    print "\nRiepilogativo:\n"
    giorno, notte, festa = calcola_mese(turni_corretti)
    print " - Diurno:    "+stampa_oremin(giorno)
    print " - Notturno:  "+stampa_oremin(notte)
    print " - Festivo:   "+stampa_oremin(festa)
    print "\n----------------------------------"
    foo = open('dati_cartellini/'+fname,'w')
    foo.write("Diurno:    "+stampa_oremin(giorno)) 
    foo.write("\nNotturno:  "+stampa_oremin(notte)) 
    foo.write("\nFestivo:   "+stampa_oremin(festa))
    foo.close() 

    return fname[:-4]


if __name__ == "__main__":
    analizza(sys.argv[1])




        
