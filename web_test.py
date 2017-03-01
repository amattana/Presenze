import web
import os
from read_pdf import *

# Process favicon.ico requests
class icon:
    def GET(self): raise web.seeother("/static/favicon.ico")

urls = ("/", "Index", "favicon.ico", "icon",
        "/Risposta","Risposta",
        "/Modifica","Modifica",
        "/Cancella","Cancella",
        "/Stampa","Stampa")

app = web.application(urls, globals())

PATH_TMP='dati_cartellini/'

gg = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]    

feste=[]

feste_nazionali = {'Natale': (25,12),
                   'S.Stefano': (26,12),
                   'Capodanno': (1, 1),
                   'Epifania': (6, 1),
                   'Tutti i Santi': (1, 11),
                   'Santo Patrono': (4, 10),
                   'Liberazione': (25, 4),
                   'Lavoratori': (1, 5),
                   'Immacolata': (8, 12),
                   'Ferragosto': (15, 8),
                   'Repubblica': (2, 6)
                   }

santa_pasqua = {
                '2000': (23,4),
                '2001': (15,4),
                '2002': (31,3),
                '2003': (20,4),
                '2004': (11,4),
                '2005': (27,3),
                '2006': (16,4),
                '2007': (8,4),
                '2008': (23,3),
                '2009': (12,4),
                '2010': (4,4),
                '2011': (24,4),
                '2012': (8,4),
                '2013': (31,3),
                '2014': (20,4),
                '2015': (5,4),
                '2016': (27,3),
                '2017': (16,4),
                '2018': (1,4),
                '2019': (21,4),
                '2020': (12,4),
                '2021': (4,4),
                '2022': (17,4),
                '2023': (9,4),
                '2024': (31,3),
                '2025': (20,4),
                '2026': (5,4)
                }

testo_note = "Si richiede il pagamento di X ore diurne, Y ore notturne, Z ore festive."

def init_feste(anno):
    feste=[]
    for k in feste_nazionali:
        feste += [datetime.datetime(anno,feste_nazionali[k][1],feste_nazionali[k][0])]
    feste += [datetime.datetime(anno, santa_pasqua[str(anno)][1],santa_pasqua[str(anno)][0])] # Pasqua
    feste += [datetime.datetime(anno, santa_pasqua[str(anno)][1],santa_pasqua[str(anno)][0])+datetime.timedelta(1)] # Pasquetta
    return feste
       
def header():
    head  = "<html>\n  <head>\n    <title>Gestione Turni osservativi (cod.67)</title>\n <meta http-equiv=\"cache-control\" content=\"no-cache\" />"
    head += "\n<link rel=\"shortcut icon\" href=\"/static/favicon.ico\" type=\"image/x-icon\"></head>\n\n<body>"  
    head += "\n    <center><h1>Gestione Turni osservativi (cod.67)</h1></center>"
    return head

def stampa_utente(user, mese):
    return  "\n    <div><center><h3 style=\"color:#00F\">"+user+" - Mese di "+mese+"</h3></center></div>"

def intabella(ris, n, m, modifica=True, linkm="", linkd=""):
    page = "\n    <div><center><table style=\"width:900\">"
    page += "\n    <tr bgcolor=\"#30A0FF\"><th align=\"center\">#</th>"
    page += "\n    <th align=\"center\">ENTRATA</th>"
    page += "\n    <th align=\"center\">USCITA</th>"
    page += "\n    <th align=\"center\">TURNO</th>"
    page += "\n    <th align=\"center\">DURATA</th>"
    if modifica==True:
        page += "\n    <th align=\"center\"> </th>"
        page += "\n    <th align=\"center\"> </th></tr>"
    i = n
    ok = 0
    while i < len(ris):
        if ((modifica == False) and (i==m)):
            page += "\n        <tr bgcolor=\"#00FFFF\">"
        elif ((not ris[i].split('.')[1].split(',')[0]== " ") and (not ris[i].split(',')[1]== " ") and (ris[i].find("Turno")>-1)):
            page += "\n        <tr bgcolor=\"#40FF40\">"
            ok = ok +1
        else:
            page += "\n        <tr bgcolor=\"#FFFF00\">"
        page += "\n             <td align=\"center\"><font size=\"3\">"
        page += ris[i].split('.')[0]+"</font></td>"
        page += "\n             <td align=\"center\"><font size=\"3\">"
        page += ris[i].split('.')[1].split(',')[0]+"</font></td>"
        page += "\n             <td align=\"center\"><font size=\"3\">"
        page += ris[i].split('.')[1].split(',')[1]+"</font></td>"
        page += "\n             <td align=\"center\"><font size=\"3\">"
        page += ris[i].split('.')[1].split(',')[2][:-1]+"</font></td>"
        if ((not ris[i].split('.')[1].split(',')[0]== " ") and (not ris[i].split(',')[1]== " ") and (ris[i].find("Turno")>-1)):
            page += "\n             <td align=\"center\"><font size=\"3\">"
            page += calcola_ore(ris[i])
            page += " </font></td>"
        else:
            page += "\n             <td align=\"center\"><font size=\"3\"> </font></td>"            
        if modifica==True:
            page += "\n             <td align=\"center\"><font size=\"3\"><a href=\""+linkm+str(i-n)+"\"> Modifica </a></font></td>"
            page += "\n             <td align=\"center\"><font size=\"3\"><a href=\""+linkd+str(i-n)+"\"> Elimina </a></font></td>"
        page += "\n        </tr>"
        i = i + 1 
    page += "</table></center></div><br><br>"
    return page, ok

def add_turno(user, err):
    page = "\n      <div>"
    if err=='1':
        page += "<center><font size=\"2\" color=\"#FF0000\"><u>ERRORE NEL FORMATO DELL\'ORARIO DI INGRESSO</u></font></center>"
    elif err=='2':
        page += "<center><font size=\"2\" color=\"#FF0000\"><u>ERRORE NEL FORMATO DELL\'ORARIO DI USCITA</u></font></center>"
    elif err=='3':
        page += "<center><font size=\"2\" color=\"#FF0000\"><u>L\'ORARIO DI USCITA DEVE ESSERE MAGGIORE DELL'ORARIO DI INGRESSO</u></font></center>"
    page += "<br><form method=\"POST\" enctype=\"multipart/form-data\" action=\"\"><center>\n      ENTRATA: <input style=\"text-align:center;\" type=\"text\" size=\"16\"  maxlength=\"16\" name=\"entrata\" value=\""
    page += "\" required=\"true\">\n   &nbsp;&nbsp;&nbsp;   USCITA: <input style=\"text-align:center;\" type=\"text\" size=\"16\"  maxlength=\"16\" name=\"uscita\" value=\""
    page += "\" required=\"true\">\n  &nbsp;&nbsp;&nbsp;    <input type=\"submit\" value=\"Aggiungi\"></center>"
    page += "\n      <input type=\"hidden\" name=\"sess\" value=\""+user+"\">"
    page += "\n      <input type=\"hidden\" name=\"nuovorecord\" value=\"True\">"
    page += "</form>"
    page += "\n   <center><font size=\"2\">formato data-ora come: \"DD/MM/YYYY HH:MM\" (esempio: 26/05/2016 08:00)</font></center></div><br>"
    return page

def calcola_ore(riga):
    entra = datetime.datetime.strptime(riga.split('.')[1].split(',')[0][5:], "%d/%m/%Y E%H:%M(67)")
    esce = datetime.datetime.strptime(riga.split('.')[1].split(',')[1][5:], "%d/%m/%Y U%H:%M(67)")
    ore = (esce - entra).seconds/60/60
    minuti = (esce - entra).seconds/60%60
    return str(ore)+":"+str(minuti).zfill(2)

def turni_status(ris, ok, total, ans):
    if ok == total:
        n=go_to_records(ris)
        feste=init_feste(int(ris[2].split(' ')[1][:-1]))
        #print feste
        giorno, notte, festa = calcola_mese(ris[n:], feste)
        #page = "\n    <div><center><a href=\"/Stampa?ans="+ans+"\"><b>STAMPA CONSUNTIVO</b></a></center></div><br>"
        page = "\n   <div><center>\n     <table style=\"width:300\">"
        page += ""
        page += "\n     <tr bgcolor=\"#40FF40\">\n        <td align=\"left\"><font size=\"3\">"
        page += "&nbsp;Diurno:</font></td>\n        <td align=\"center\"><font size=\"3\">"+stampa_oremin(giorno)
        page += "</font></td>\n     </tr>"
        page += "\n     <tr bgcolor=\"#40FF40\">\n       <td align=\"left\"><font size=\"3\">"
        page += "&nbsp;Notturno:</font></td>\n        <td align=\"center\"><font size=\"3\">"+stampa_oremin(notte)
        page += "</font></td>\n     </tr>"
        page += "\n     <tr bgcolor=\"#40FF40\">\n       <td align=\"left\"><font size=\"3\">"
        page += "&nbsp;Festivo:</font></td>\n        <td align=\"center\"><font size=\"3\">"+stampa_oremin(festa)
        page += "</font></td>\n     </tr>"
        page += "\n     </table></center>\n   </div><br>"
        nota=testo_note.replace("X",str(giorno/60)).replace("Y",str(notte/60)).replace("Z",str(festa/60))
        page += "\n\n<br><form  method=\"POST\" enctype=\"multipart/form-data\" action=\"\"><center><input type=\"submit\" value=\"STAMPA CONSUNTIVO\"><br><br><input name=\"note\" type=\"checkbox\" value=\"True\"> Spunta per includere le seguenti NOTE:<br><br> <textarea name=\"BoxNote\" cols=\"80\" rows=\"5\">"+nota+"</textarea></center>"
        page += "\n      <input type=\"hidden\" name=\"stampa\" value=\"True\"></form>\n"
    else:
        page = "\n    <div><center><font size=\"4\" color=\"#FF0000\">Devi correggere gli orari dei turni per poter stampare il consuntivo.</font></center></div><br>"    
    return page

def stampa_oremin(ore):
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

def diurno(orario):
    if (orario.hour >= 6) and (orario.hour < 22) and (orario.isoweekday() < 6):
        return True
    else:
        return False   

def notturno(orario):
    if (orario.hour >= 22) or (orario.hour < 6) and (orario.isoweekday() < 6):
        return True
    else:
        return False   

def festivo(orario, feste):
    #print feste
    for k in feste:
        if orario.date()==k.date():
            return True
    if orario.isoweekday() >= 6:
        return True
    else:
        return False   

def calcola_dnf(riga, feste):
    entra = datetime.datetime.strptime(riga.split('.')[1].split(',')[0][5:], "%d/%m/%Y E%H:%M(67)")
    esce = datetime.datetime.strptime(riga.split('.')[1].split(',')[1][5:], "%d/%m/%Y U%H:%M(67)")
    orario = entra
    ore_diurne = ore_notturne = ore_festive = 0 
    while orario < esce:
        if festivo(orario, feste):
            ore_festive = ore_festive + 1
        elif diurno(orario):
            ore_diurne = ore_diurne + 1
        elif notturno(orario):
            ore_notturne = ore_notturne + 1
        orario = orario + datetime.timedelta(0,60)
    return ore_diurne, ore_notturne, ore_festive

def calcola_mese(turni, feste):
    #print turni
    ore_diurne = ore_notturne = ore_festa = 0
    for i in xrange(len(turni)):
        giorno, notte, festa = calcola_dnf(turni[i], feste)
        #print giorno, notte, festa
        ore_diurne = ore_diurne + giorno 
        ore_notturne = ore_notturne + notte 
        ore_festa = ore_festa + festa 
    #print ore_diurne, ore_notturne, ore_festa
    return ore_diurne, ore_notturne, ore_festa


def modifica_campi(ris, n, user, riga):
    page = "\n      <div><form method=\"POST\" enctype=\"multipart/form-data\" action=\"\"><center>\n      "
    if ((not ris[n].split('.')[1].split(',')[0] == ' ') and (ris[n].find('E')>-1)):
        page += "<font size=\"3\" style=\"background-color:#40FF40\">ENTRATA</font>:&nbsp;&nbsp;<input style=\"text-align:center;\" type=\"text\" size=\"16\"  maxlength=\"16\" name=\"entrata\" value=\""+ris[n].split('.')[1].split(',')[0].split('E')[0][-11:-1]+" "+ris[n].split('.')[1].split(',')[0].split('E')[1][:-4]
    else:
        page += "<font size=\"3\" style=\"background-color:#FFFF00\">ENTRATA</font>:&nbsp;&nbsp;<input style=\"text-align:center;\" type=\"text\" size=\"16\"  maxlength=\"16\" name=\"entrata\" value=\""
    page += "\" required=\"true\">\n   &nbsp;&nbsp;&nbsp;"

    if ((not ris[n].split('.')[1].split(',')[1] == ' ') and (ris[n].find('U')>-1)):
        page += "<font size=\"3\" style=\"background-color:#40FF40\">USCITA</font>:&nbsp;&nbsp;<input style=\"text-align:center;\" type=\"text\" size=\"16\"  maxlength=\"16\" name=\"uscita\" value=\""+ris[n].split('.')[1].split(',')[1].split('U')[0][-11:-1]+" "+ris[n].split('.')[1].split(',')[1].split('U')[1][:-4]
    else:
        page += "<font size=\"3\" style=\"background-color:#FFFF00\">USCITA</font>:&nbsp;&nbsp;<input style=\"text-align:center;\" type=\"text\" size=\"16\"  maxlength=\"16\" name=\"uscita\" value=\""
    page += "\" required=\"true\">\n  &nbsp;&nbsp;&nbsp;    <input type=\"submit\" value=\"Correggi\">"
    page += "\n  &nbsp;&nbsp;&nbsp;<button type=\"reset\" formnovalidate value=\"Annulla\" onclick=\"location.href=\'/Risposta?ans="+user+"\';\">Annulla</button></center>"
    page += "\n      <input type=\"hidden\" name=\"sess\" value=\""+user+"\">"
    page += "\n      <input type=\"hidden\" name=\"riga\" value=\""+riga+"\">"
    page += "</form>"
    page += "\n   <center><font size=\"3\">formato data-ora come: \"DD/MM/YYYY HH:MM\" (esempio: 26/05/2016 08:00)</font></center></div><br>"
    return page

def go_to_records(ris):
    n=0
    while not ris[n]=="[cod.67]\n":
        n=n+1
    n=n+1
    return n

    
def mostra_cartellino(pdf_name):
        return "<br>\n    <div>\n     <center>\n      <embed src=\""+pdf_name+"\" width=\"900\" \n              height=\"500\" alt=\"pdf\" pluginspage=\"http://www.adobe.com/products/acrobat/readstep2.html\">\n     </center>\n    </div>"


def close_html():
    return "\n  </body>\n</html>"

def leggi_tmp_file(fname):
    foo = open(fname,'r')
    ris = foo.readlines() 
    foo.close()
    return ris

def scrivi_tmp_file(fname, ris):
    foo = open(fname,'w')
    i=0
    while not ris[i]=="[cod.67]\n":
        foo.write(ris[i])
        i=i+1
    foo.write(ris[i]) 
    i=i+1
    a=1
    while i < len(ris):
        foo.write(str(a)+"."+ris[i].split('.')[1])
        i=i+1
        a=a+1
    foo.close()

def clean_tmp_files():
    files=os.listdir("dati_cartellini")
    for f in files:
        data_file=datetime.datetime.fromtimestamp(os.path.getctime("dati_cartellini/"+f))
        permanenza = datetime.datetime.now() - data_file
        if permanenza.days>0:
            os.system("rm -f dati_cartellini/"+f)
    files=os.listdir("static")
    lista_filtrata = []
    for f in files:
        if ((not f=='missioni.png') and (not f=='missioni.pdf')):
            lista_filtrata += [f]
    for f in lista_filtrata:
        data_file=datetime.datetime.fromtimestamp(os.path.getctime("static/"+f))
        permanenza = datetime.datetime.now() - data_file
        if permanenza.days>0:
            os.system("rm -f static/"+f)

    

class Index:
    def GET(self):
        args = web.input(err = '0',name = 'web', ans = 'web')
        clean_tmp_files()
        web.header("Content-Type","text/html; charset=utf-8")
        page  = header()
        page += "\n    <center><a href=\"https://presenze.bo.cnr.it/cartellino/index.htm\">CARTELLINO</a></center>"
       
        page += "\n <center><br><br>Prendi il pdf del cartellino e fai \"INVIA\" qui sotto<br><br><br></center>"
        if args.err=='1':
            page += "<center><font size=\"2\" color=\"#FF0000\"><u>ERRORE NEL FORMATO DEL FILE PDF DEL CARTELLINO. PROVA CON UN NUOVO FILE...</u></font></center><br><br>"
        page += "<form method=\"POST\" enctype=\"multipart/form-data\" action=\"\"><center><input type=\"file\" name=\"myfile\" size=\"100\"></center><br><br><center><input type=\"submit\" value=\"INVIA\"></center></form>"
 
        page += "\n <center><br><br><font color=\"#FF0000\"><u>LINK UTILI:</u></font><br><br><a href=\"static/manuale.pdf\">MANUALE</a> DI QUESTO TOOL<br><br><a href=\"static/missioni.pdf\">MANUALE</a> MISSIONI PER TURNI OSSERVATIVI<br><br><a href=\"http://servizi1.ced.inaf.it:8080/TNSINA\">LINK</a> PROGRAMMA MISSIONI<br><br><a href=\"http://servizi1.ced.inaf.it:8080/TNSINA\"><img src=\"static/missioni.png\" alt=\"\" width=\"170\" height=\"170\" border=\"0\"></a></center>"
        page += "\n  </body>\n</html>"
        return page

    def POST(self):
        x = web.input(myfile={})
        #print x.myfile.filename
        ans=""
        filedir = 'static'
        if not x.myfile.filename=='':
            if 'myfile' in x:
                filepath=x.myfile.filename.replace('\\','/').replace('(','').replace(')','')
                filename="POST_"+filepath.split('/')[-1].replace(' ','_') # splits the and chooses the last part (the filename with extension)
                fout = open(filedir +'/'+ filename,'w') # creates the file where the uploaded file should be stored
                fout.write(x.myfile.file.read()) # writes the uploaded file to the newly created file.
                fout.close() # closes the file, upload complete.
                try:
                    ans=analizza(filedir +'/'+ filename)
                except:
                    web.seeother("/?err=1")
                    pass
        else:
            web.seeother("/?err=1")

        if ans=="":
            web.seeother("/?err=1")
        else:
            web.seeother("/Risposta?ans="+ans)

class Risposta:
    def GET(self):
        args = web.input(name = 'web', ans = 'web', inputerr = '0')
        ansname = PATH_TMP+args.ans+'.dat'
        ris = leggi_tmp_file(ansname)
        pdf_name=ris[4][:-1]
        n=go_to_records(ris)
        page  = header()
        page += stampa_utente(ris[1][:-1], ris[2][:-1])
        linkm="/Modifica?ans="+args.ans+"&riga="
        linkd="/Cancella?ans="+args.ans+"&riga="
        html, ok = intabella(ris, n, len(ris), True, linkm, linkd)
        page += html

        page += add_turno(args.ans, args.inputerr)
  
        page += turni_status(ris, ok, len(ris)-n, args.ans)

        page += mostra_cartellino(pdf_name)
        page += close_html()
        return page

    def POST(self):
        store = web.input(ans = 'web', riga = '0', entrata = '01/01/2000 00:00', uscita = '01/01/2000 00:00', note=False, nuovorecord=False, stampa=False)
        if store.nuovorecord:
            err=0
            try:
                entr=datetime.datetime.strptime(store.entrata, "%d/%m/%Y %H:%M")
            except:
                err=1
                pass
            try:
                usc=datetime.datetime.strptime(store.uscita, "%d/%m/%Y %H:%M")
            except:
                err=2
                pass
            if err==0:
                if entr>usc:
                    err=3
            ansname = PATH_TMP+store.ans+'.dat'
            ris = leggi_tmp_file(ansname)
            n=go_to_records(ris)
        
            if err==0:
                try:
                    ris += [str(int(ris[len(ris)-1].split(".")[0])+1)+". "+gg[entr.isoweekday()-1]+" "+entr.strftime("%d/%m/%Y E%H:%M(67), ")+gg[usc.isoweekday()-1]+" "+usc.strftime("%d/%m/%Y U%H:%M(67), Turno\n")]
                except:
                    ris += ["1. "+gg[entr.isoweekday()-1]+" "+entr.strftime("%d/%m/%Y E%H:%M(67), ")+gg[usc.isoweekday()-1]+" "+usc.strftime("%d/%m/%Y U%H:%M(67), Turno\n")]
                scrivi_tmp_file(ansname, ris)
            web.seeother("/Risposta?ans="+store.ans+"&inputerr="+str(err))

        if store.stampa:
            if store.note:
                f=open(PATH_TMP+store.ans+".note",'w')
                f.write(store.BoxNote)
                f.close()
            else:
                if os.path.isfile(PATH_TMP+store.ans+".note"):
                    os.system("rm "+PATH_TMP+store.ans+".note")
            web.seeother("/Stampa?ans="+store.ans)
            

class Modifica:
    def GET(self):
        args = web.input(ans = 'web', riga = '0')
        ansname = PATH_TMP+args.ans+'.dat'
        ris = leggi_tmp_file(ansname) 
        pdf_name=ris[4][:-1]
        n=go_to_records(ris)

        page  = header()
        page += stampa_utente(ris[1][:-1], ris[2][:-1])

        html, ok = intabella(ris, n, n+int(args.riga), False)
        page += html

        n=n+int(args.riga)
        page += modifica_campi(ris, n, args.ans, args.riga)
        page += mostra_cartellino(pdf_name)
        page += close_html()

        return page

    def POST(self):
        store = web.input(ans = 'web', riga = '0', entrata = '01/01/2000 00:00', uscita = '01/01/2000 00:00')
        err=0
        try:
            entr=datetime.datetime.strptime(store.entrata, "%d/%m/%Y %H:%M")
        except:
            err=1
            pass
        try:
            usc=datetime.datetime.strptime(store.uscita, "%d/%m/%Y %H:%M")
        except:
            err=2
            pass
        if entr>usc:
            err=3
        ansname = PATH_TMP+store.ans+'.dat'
        ris = leggi_tmp_file(ansname)
        n=go_to_records(ris)
        if err==0:
            ris[n+int(store.riga)] = str(int(store.riga)+1)+". "+gg[entr.isoweekday()-1]+" "+entr.strftime("%d/%m/%Y E%H:%M(67), ")+gg[usc.isoweekday()-1]+" "+usc.strftime("%d/%m/%Y U%H:%M(67), Turno\n")
            scrivi_tmp_file(ansname, ris)

        web.seeother("/Risposta?ans="+store.ans+"&inputerr="+str(err))

class Cancella:
    def GET(self):
        args = web.input(ans = 'web', riga = '0')
        ansname = PATH_TMP+args.ans+'.dat'
        ris = leggi_tmp_file(ansname) 
        n=go_to_records(ris)
        scrivi_tmp_file(ansname, ris[:n+int(args.riga)]+ris[n+int(args.riga)+1:])
        web.seeother("/Risposta?ans="+args.ans)

class Stampa:
    def GET(self):
        from gen_pdf import genera_pdf
        args = web.input(ans = 'web')
        fname = PATH_TMP+args.ans+'.dat'
        pdf_name=genera_pdf(fname)

        web.seeother(pdf_name)

if __name__ == "__main__":
    app.run()





