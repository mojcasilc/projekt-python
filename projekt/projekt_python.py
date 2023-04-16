import re
import requests
import csv
from bs4 import BeautifulSoup
import random
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import os
from sklearn.linear_model import LinearRegression
import numpy as np

leta = ["chamonix-1924", "st-moritz-1928", "lake-placid-1932",
        "garmisch-partenkirchen-1936", "st-moritz-1948", "oslo-1952",
        "cortina-d-ampezzo-1956", "squaw-valley-1960", "innsbruck-1964",
        "grenoble-1968", "sapporo-1972", "innsbruck-1976", "lake-placid-1980",
        "sarajevo-1984", "calgary-1988", "albertville-1992", "lillehammer-1994",
        "nagano-1998", "salt-lake-city-2002", "turin-2006", "vancouver-2010",
        "sochi-2014"]

discipline = ['500m-men', '500m-women', '1000m-men', '1000m-women', '1500m-men','1500m-women', 
            '3000m-women', '5000m-men', '5000m-women', '10000m-men']

naslov = 'https://olympics.com/en/olympic-games/'
naslov2 = '/results/speed-skating/'

def imenik():
    '''naredi imenik za pdf datoteke'''
    if not os.path.exists("grafi"): #če imenik ne obstaja ga naredi
        os.mkdir('grafi')
             
def pridobitev_podatkov_tekmovalcev():
    '''
    Funkcija sprejme ime discipline in olimpijske igre in naredi seznam
    slovarjev v katerih so rezultati tekmovalca.
    '''
    for leto in leta:
        for disciplina in discipline:

            url = naslov + leto + naslov2 + disciplina
            req = requests.get(url)
            vsebina = BeautifulSoup(req.content, 'html.parser')
            
            if "PAGE NOT FOUND" not in vsebina:
                #pridobitev vseh mest oz. uvrstitev tekmovalcev
                s1 = vsebina.find_all('span', class_='Medalstyles__Medal-sc-1tu6huk-1')
                mesta = []
                for mesto in s1:
                    mesto = re.search(r'<span class=".*?" data-cy="medal-main">(?P<mesto>.+?)</span>',str(mesto))
                    if mesto == None: #če tekmovalec nima mesta (diskvalificiran, ni začel)
                        break
                    mesto = mesto.group('mesto')
                    razvrstitev = re.search('\d+', mesto) 
                    if razvrstitev: #če je stevilka
                        mesto = razvrstitev.group()
                    else:
                        if mesto == 'G':
                            mesto = '1'
                        elif mesto == 'S':
                            mesto = '2'
                        elif mesto == 'B':
                            mesto = '3'
                        else:
                            break
                    mesta.append(mesto) 
                    
                #pridobitev vseh drzav tekmovalcev
                s2 = vsebina.find_all('span', class_='styles__CountryName-sc-1r5phm6-1 bojjbG')
                drzave = []
                for drzava in s2:
                    drzava = re.search(r'<span class="styles__CountryName-sc-1r5phm6-1 bojjbG" data-cy=".*?">(?P<drzava>\D{3})</span>',str(drzava))
                    drzava = drzava.group('drzava')
                    drzave.append(drzava)

                #pridobitev vseh imen tekmovalcev
                s3 = vsebina.find_all('h3', class_="styles__AthleteName-sc-1yhe77y-3 jkTgwS")
                imena = []
                for ime in s3:
                    ime = re.search(r'<h3 class="styles__AthleteName-sc-1yhe77y-3 jkTgwS" data-cy="athlete-name">(?P<ime>.*?)</h3>',str(ime))
                    ime = ime.group('ime')
                    if ime not in seznam_tekmovalcev:
                        seznam_tekmovalcev.add(ime)
                    ime = ime.replace("-", " ")
                    ime = ime.title() 
                    imena.append(ime)

                #pridobitev vseh rezultatov tekmovalcev
                s4 = vsebina.find_all('span', class_='styles__Info-sc-cjoz4h-0 kLiUyB')
                rezultati = []
                for rezultat in s4:
                    rezultat = re.search(r'<span data-cy="result-info-content">(?P<rezultat>.*?)</span>',str(rezultat))
                    rezultat = rezultat.group('rezultat')
                    rezultati.append(rezultat)

                igre = leto
                igre = igre.replace("-", " ")
                igre = igre.title()

                # za vsakega drsalca ustvarimo slovar in ga dodamo v tabelo rezultatov
                for i in range(len(mesta)):
                    drsalec = {}
                    drsalec['igre'] = igre
                    drsalec['disciplina'] = disciplina
                    drsalec['mesto'] = mesta[i]
                    drsalec['ime'] = imena[i]
                    drsalec['drzava'] = drzave[i]
                    drsalec['rezultat'] = rezultati[i]
                    results.append(drsalec)
    ustvari_tabelo('tabela.csv',results)

def zapis_imen(seznam_tekmovalcev):
    '''zapise imena tekmovalcev na datoteko po abecedi'''
    with open('tekmovalci.txt', 'w', encoding='utf8') as file:
        seznam = sorted(seznam_tekmovalcev)
        for tekmovalec in seznam:
            tekmovalec = re.sub(' ','-', tekmovalec)
            file.write(tekmovalec)
            file.write('\n')

def rojstni_dnevi():
    '''funkcija pridobi podatke o rojstnih dnevih tekmovalcev in polno ime države'''
    #pridobitev vseh rojstnih dnevov tekmovalcev
    with open('tekmovalci.txt', 'r', encoding='utf8') as file:
        for tekmovalec in file:
            print(tekmovalec)
            tekmovalec = tekmovalec.strip('\n')
            participant = {}
            drzave = {}

            tekmovalec = re.sub(' ','-', tekmovalec)
            url = 'https://olympics.com/en/athletes/' +  tekmovalec
            req = requests.get(url)
            vsebina = BeautifulSoup(req.content, 'html.parser')
            
            s = vsebina.find_all('div', class_='slug__Wrapper-sc-4eg0c6-0 iWAhTO')
            if s == []:
                continue
            leto = re.search(r'<span data-cy="year-of-birth">(?P<bd>\d{4})</span>',str(s))
            if leto == None: #tekmovalec nima zapisanega rojstnega dneva
                continue
            leto = leto.group('bd')
            participant['ime'] = tekmovalec
            participant['letnica rojstva'] = leto
            
            rd.append(participant)

            dr = vsebina.find(class_='indexstyles__StyledNocsWrapper-sc-1j7ze2h-2 ejIGfT')
            if dr == '':
                continue
            drzava = re.search(r'<span>(?P<drzava>.*?)</span>',str(dr))
            if drzava == None:
                continue
            drzava = drzava.group('drzava')
            drzave['drzava'] = drzava

            kr = vsebina.find_all(id='olympicResultRef')
            if kr == '':
                continue
            kratica = re.search(r'<span>(?P<kratica>.*?)</span>',str(kr))
            if kratica == None:
                continue
            kratica = kratica.group('kratica')
            drzave['kratica'] = kratica 

            if drzave not in countries:
                countries.append(drzave)
            
    ustvari_tabelo('rd.csv', rd, ['ime', 'letnica rojstva'])
    ustvari_tabelo('drzave.csv', countries, ['kratica', 'drzava'])

def ustvari_tabelo(dat, slovarji, imena = ['igre', 'disciplina', 'mesto', 'drzava', 'ime', 'rezultat']):
    '''iz seznama slovarjev ustvari tabele csv'''
    with open(dat, 'w', encoding='utf8') as file:
        writer = csv.DictWriter(file, fieldnames = imena)
        writer.writeheader()
        for slovar in slovarji:
            writer.writerow(slovar)

def shrani_podatke():
    '''shrani podatke posameznega tekmovalca skupaj z njegovimi rezultati in drzavo'''
    with open('tabela.csv', 'r', encoding="utf-8") as file1:
        with open('rd.csv', 'r', encoding="utf-8") as file2:
            vrstice1 = file1.readlines()
            vrstice2 = file2.readlines()
            imena = []
            datumi = []
            for line in vrstice2[1:]:
                pod = line.strip().split(',')
                if pod[0] == '':
                    continue
                ime = re.sub('-', ' ', pod[0]).title()
                imena.append(ime)
                datumi.append(pod[1])

            for line in vrstice1[1:]:
                podatki = line.strip().split(',')
                if podatki[0] == '':
                    continue
                if podatki[4] in podatki_tekmovalcev: #tekmovalec je že vnešen, le dodamo mu podatke drugih oi
                    podatki_tekmovalcev[podatki[4]].append(
                        (podatki[0], podatki[1], podatki[2], podatki[3], podatki[5])
                    )
                else:
                    if podatki[4] in imena: #preverimo ali tekmovalec ima rojstni datum in ga doda
                        i = imena.index(podatki[4])
                        podatki_tekmovalcev[podatki[4]] = [
                            datumi[i], (podatki[0], podatki[1], podatki[2], podatki[3], podatki[5])
                        ]

    return podatki_tekmovalcev

#stara imena držav sva nadomestili z današnjimi
popravek_drzav = {"People's Republic of China" : "China", "Chinese Taipei" : "China", '"Hong Kong, China"' : "China",
"Russian Federation" : "Russia", "Soviet Union" : "Russia", "ROC" : "Russia",
"German Democratic Republic (Germany)" : "Germany", "Federal Republic of Germany" : "Germany",
'"Virgin Islands, US"' : "Virgin Islands" }
#države ki ne obstajajo več
ne_obstaja_vec = ['Czechoslovakia', 'Yugoslavia']

def tabela_koordinat():
    '''Funkcija prebere wikipedijo posamezne drzave in razbere geografsko sirino in geografsko visino.'''
    with open('drzave.csv', 'r', encoding='utf8') as file:
        dat = file.readlines()
        for line in dat[1:]:
            sez = {}
            if line == '\n':
                continue
            podatki = line.strip().split(',')
            drzava = podatki[-1]

            if drzava in ne_obstaja_vec:
                continue
            if drzava in popravek_drzav.keys():
                drzava = popravek_drzav[drzava]

            url = 'https://en.wikipedia.org/wiki/' + drzava      
            req = requests.get(url)
            vsebina = BeautifulSoup(req.content, 'html.parser')

            s1 = vsebina.find('span', class_='latitude')
            s2 = vsebina.find('span', class_='longitude')

            if s1 == None or s2 == None:
                continue

            geo_v = re.search(r'(<span class="latitude">(?P<geo_visina>.*?)</span>)', str(s1)) 
            geo_s = re.search(r'(<span class="longitude">(?P<geo_sirina>.*?)</span>)', str(s2))

            if geo_v == '' or geo_s == '':
                continue

            geo_visina = geo_v.group('geo_visina')
            geo_sirina = geo_s.group('geo_sirina')

            kratica = podatki[0]
            seznam[kratica] = (geo_visina, geo_sirina)
            sez['kratica_drzave'] = kratica
            sez['geo_visina'] = geo_visina
            sez['geo_sirina'] = geo_sirina

            koordinate.append(sez)           
    ustvari_tabelo('koordinate.csv', koordinate, ['kratica_drzave', 'geo_visina', 'geo_sirina'])
    #izračun zemljepisne višine in širine le v stopinjah 
    konec = {}
    for drzava in seznam:
        dolzina, sirina = seznam[drzava]
        stopinje, ostanek1 = dolzina.split('°')
        if len(ostanek1) != 1:
            minute, ostanek2 = ostanek1.split("′")
            if len(ostanek2) != 1:
                sekunde, ostanek3 = ostanek2.split('″')
                if ostanek3 == 'N':
                    longitude = float(stopinje) + float(minute)/60 + float(sekunde)/3600
                else:
                    longitude = -1*(float(stopinje) + float(minute)/60 + float(sekunde)/3600)                    
            else:
                if ostanek2 == 'N':
                    longitude = float(stopinje) + float(minute)/60
                else:
                    longitude = -1*(float(stopinje) + float(minute)/60)
        else:
            if ostanek1 == 'N':
                longitude = float(stopinje)
            else:
                longitude = -1*(float(stopinje))

        if sirina != '':
            stopinje, ostanek1 = sirina.split('°')
            if len(ostanek1) != 1:
                minute, ostanek2 = ostanek1.split("′")
                if len(ostanek2) != 1:
                    sekunde, ostanek3 = ostanek2.split('″')
                    if ostanek3 == 'E':
                        latitude = float(stopinje) + float(minute)/60 + float(sekunde)/3600
                    else:
                        latitude = -1*(float(stopinje) + float(minute)/60 + float(sekunde)/3600)                    
                else:
                    if ostanek2 == 'E':
                        latitude = float(stopinje) + float(minute)/60
                    else:
                        latitude = -1*(float(stopinje) + float(minute)/60)
            else:
                if ostanek1 == 'E':
                    latitude = float(stopinje)
                else:
                    latitude = -1*(float(stopinje))
        konec[drzava] = (longitude, latitude)
    return konec

class Tekmovalec:
    '''Razred predstavi tekmovalca in njegove rezultate'''
    def __init__(self, ime, nastopi, rojen=""):
        self.ime = ime
        self.rojen = rojen
        self.stevilo_nastopov = len(set([i[0] for i in nastopi]))
        self.drzava = nastopi[0][3]
        self.discipline = set([i[1] for i in nastopi])
        self.nastopi = nastopi
        self.spol = nastopi[0][1].split('-')[-1]

    def __str__(self):
        nastopi = ''
        for nastop in self.nastopi:
            if self.spol == 'men':
                nastopi += 'Na {0} olimpijskih igrah v {1} disciplini je bil na {2} mestu z rezultatom {3}, '.format(
                nastop[0], nastop[1], nastop[2], nastop[4]
                )
                rojen_rojena = 'rojen  '
            if self.spol == 'women':
                nastopi += 'Na {0} olimpijskih igrah v {1} disciplini je bila na {2} mestu z rezultatom {3}, '.format(
                nastop[0], nastop[1], nastop[2], nastop[4]
                )
                rojen_rojena = 'rojena '
        return " ime     | {0} \n {4} | {1} v {3} \n nastopi | {2} \n".format(
            self.ime, self.rojen, nastopi, self.drzava, rojen_rojena
        )

    def __repr__(self):
        return 'Tekmovalec({0},{1},{2})'.format(self.ime, self.nastopi, self.rojen)

    def natancna_predstavitev_tekmovalca(self):
        '''Funkcija vrne seznam naborov z imenom, rojstvom, drzavo, rezultatom in starostjo.'''
        seznam = []
        for nastop in self.nastopi:
            if not isinstance(self.rojen, str):
                break
            if self.rojen == '':
                seznam.append((self.ime, self.rojen, self.drzava, nastop[0], nastop[1], nastop[2], nastop[4].replace('"',''), 'Ni podatka'))
                continue
            starost = int(nastop[0][-4:]) - int(self.rojen[-4:])
            seznam.append((self.ime, self.rojen, self.drzava, nastop[0], nastop[1], nastop[2], nastop[4].replace('"',''), str(starost)))
        return seznam
            
    def podatki_po_disciplinah(self):
        '''Funkcija vrne slovar, kjer je kljuc disciplina in vrednost seznam rezultatov pri tej disciplini.'''
        slovar={}
        for nastop in self.nastopi:
            if nastop[1] in slovar: #nastop[1] = disciplina
                slovar[nastop[1]].append(nastop)
            else:
                slovar[nastop[1]] = [nastop]
        return slovar
    
    def iz_katere_drzave(self):
        return self.nastopi[0][3]

class Tekmovalci:
    '''Razred Tekmovalci zajame vse tekmovalce in z njimi dela poizvedbe.'''
    def __init__(self, vsi_rezultati):
        drzave = set()
        discipline = set()
        oi = set()
        for tekmovalec in vsi_rezultati:
            for nastop in vsi_rezultati[tekmovalec][1:]:
                drzave.add(nastop[3])
                discipline.add(nastop[1])
                oi.add(nastop[0])
        self.vse_drzave = drzave
        self.vse_discipline = discipline
        self.oi = oi
        self.vsi_rezultati = vsi_rezultati
        self.sez_tekmovalcev = list(vsi_rezultati.keys())

    def __str__(self):
        return "Ta razred predstavlja rezultate {} olimpijskih iger v {} disciplinah iz {} držav.".format(
            len(self.oi), len(self.vse_discipline), len(self.vse_drzave)
            )
    def __repr__(self):
        return "Tekmovalci({})".format(self.vsi_tekmovalci)

    def izpisi_tekmovalca(self, ime=None):
        '''Funkcija vrne izpis podatkov za tekmovalca, ce ga podamo, sicer si ga nakljucno izbere.'''
        if ime == None:
            ime = random.choice(self.sez_tekmovalcev)
            return Tekmovalec(ime, podatki_tekmovalcev[ime][1:], podatki_tekmovalcev[ime][0])
        else:
            return Tekmovalec(ime, podatki_tekmovalcev[ime][1:], podatki_tekmovalcev[ime][0])

    def natancno_izpisi_tekmovalca(self, ime=None):
        '''Funkcija vrne seznam naborov z imenom, rojstvom, drzavo, rezultatom in starostjo za tekmovalca, ki ga napisemo oz
        ce ne podamo tekmovalca, ga funkcija nakljucno izbere.'''
        if ime == None:
            ime = random.choice(self.sez_tekmovalcev)
            return Tekmovalec(ime, podatki_tekmovalcev[ime][1:], podatki_tekmovalcev[ime][0]).natancna_predstavitev_tekmovalca()
        else:
            return Tekmovalec(ime, podatki_tekmovalcev[ime][1:], podatki_tekmovalcev[ime][0]).natancna_predstavitev_tekmovalca()

    def tekmovalci_po_disciplinah(self):
        '''Funkcija vrne slovar, kjer so kljuci discipline in vrednosti so seznami tekmovalcev z njihovimi rezultati.'''
        vsi = [(
            ime,
            Tekmovalec(ime, podatki_tekmovalcev[ime][1:], podatki_tekmovalcev[ime][0]).podatki_po_disciplinah(),
            Tekmovalec(ime, podatki_tekmovalcev[ime][1:], podatki_tekmovalcev[ime][0]).rojen
            ) for ime in self.sez_tekmovalcev]
        razvrsceno_po_disciplinah = {}
        for ime, nastopi, roj in vsi:
            for disc in nastopi:
                if disc in razvrsceno_po_disciplinah:
                    razvrsceno_po_disciplinah[disc].append((ime,nastopi[disc],roj))
                else:
                    razvrsceno_po_disciplinah[disc] = [(ime,nastopi[disc],roj)]
        return razvrsceno_po_disciplinah

    def zmagovalci_po_disciplinah(self):
        '''Funkcija vrne slovar, kjer so kljuci discipline in vrednosti so tekmovalci s prvih treh mest z rezultati.'''
        zmagovalci = {}
        for disc in self.vse_discipline:
            zmagovalci[disc] = []
        for disc in self.tekmovalci_po_disciplinah():
            for ime,nastopi,roj in self.tekmovalci_po_disciplinah()[disc]:
                sez = [(nastop[0][-4:],nastop[2],nastop[-1]) for nastop in nastopi if nastop[2] == '1' or nastop[2] == '2' or nastop[2] == '3']
                if sez != []:
                    zmagovalci[disc].append((ime,sez,roj))
        return zmagovalci

    def st_raz_drzav_pri_disc(self, disc):
        '''Funkcija vrne slovar, kjer so kljuci olimpijske igre in vrednosti so stevilo razlicnih drzav pri teh olimpijskih
        igrah in podatni disciplini.'''
        slovar1 = self.tekmovalci_po_disciplinah()
        slovar2 = {}
        for i in self.oi:
            slovar2[i] = set()
        for tekmovalec in slovar1[disc]:
            for nastop in tekmovalec[1]:
                slovar2[nastop[0]].add(nastop[3])
        for oi in slovar2:
            slovar2[oi] = len(slovar2[oi])
        return slovar2

    def tekmovalec_in_drzava(self):
        '''Funkcija vrne slovar, kjer so kljuci drzave in vrednosti so stevilo razlicnih tekmovalcev iz te drzave
        skozi vse olimpijske igre.'''
        mnozica = set()
        for ime in self.sez_tekmovalcev:
            tekmovalec = self.natancno_izpisi_tekmovalca(ime)
            nabor = (tekmovalec[0][0], tekmovalec[0][2])
            mnozica.add(nabor)
        slovar={}
        for _, drzava in mnozica:
            if drzava in slovar:
                slovar[drzava] += 1
            else:
                slovar[drzava] = 1
        return slovar

def plot_evolve(slovar, disciplina):
    '''Spreminjanje rezultatov skozi cas pri podani disciplini.'''
    seznam1,seznam2,seznam3=[[],[],[]]
    leto1,leto2,leto3=[[],[],[]]
    rezultat1,rezultat2,rezultat3=[[],[],[]]

    for _,sez,_ in slovar[disciplina]:
        for s in sez:
            if s[2] == '':
                continue
            r = 0
            # Zapis v sekundah pri vseh disciplinah
            if s[2] == 'Did not start':
                continue
            #pri nekaterih oi so bili pri teh dveh disciplinah časi drugače podani
            if disciplina == '500m-men' or disciplina == '500m-women':
                if ':' in s[2]:
                    razrez = s[2].split(':')    
                    j = razrez[0]
                    i = razrez[1]
                    r += float(j)*60 + float(i)
                    r = r/2
                else:
                    r += float(s[2])
            else:
                if ':' in s[2]:
                    razrez = s[2].split(':')
                    j = razrez[0]
                    i = razrez[1]
                    r += float(j)*60 + float(i)
                else:
                    r += float(s[2])
            #potrebujemo le prve tri tekmovalce
            if s[1] == '1':
                try:
                    seznam1.append((int(s[0]),float(r)))
                except:
                    continue
            if s[1] == '2':
                try:
                    seznam2.append((int(s[0]),float(r)))
                except:
                    continue
            if s[1] == '3':
                try:
                    seznam3.append((int(s[0]),float(r)))
                except:
                    continue

    # Naredimo sezname potrebne za risanje grafa
    for i, j in sorted(seznam1[::-1]):
        leto1.append(i)
        rezultat1.append(j)
    for i, j in sorted(seznam2[::-1]):
        leto2.append(i)
        rezultat2.append(j)
    for i, j in sorted(seznam3[::-1]):
        leto3.append(i)
        rezultat3.append(j)

    # Izris oz shranitev grafa
    fig = plt.figure()

    plt.plot(leto1, rezultat1, marker='o', color='gold', markeredgecolor = 'white', zorder=0, label = "1.mesto")
    plt.plot(leto2, rezultat2, marker='o', color='gray', markeredgecolor = 'white', zorder=0, label = "2.mesto")
    plt.plot(leto3, rezultat3, marker='o', color='brown', markeredgecolor = 'white', zorder=0, label = "3.mesto")

    plt.title("Spreminjanje rezultatov skozi cas pri disciplini {}".format(disciplina))
    plt.xlabel("Leta")
    plt.ylabel("Rezultati")
    plt.legend(loc = 'best')
    plt.close()
    fig.savefig('grafi/rezultati_skozi_cas_pri_{}_disciplini.pdf'.format(disciplina))

    return leto1, rezultat1

def bar_st_drzav_po_disc(slovar, disciplina):
    '''Stevilo drzav pri doloceni disciplini'''
    olimpijske_igre = []
    st_drzav = []

    # Naredimo sezname potrebne za risanje grafa
    for oi in slovar:
        if slovar[oi] != 0:
            olimpijske_igre.append(int(oi[-4:]))
            st_drzav.append(slovar[oi])

    # Izris oz shranitev grafa
    fig = plt.figure(figsize = (10,6))
    plt.bar(olimpijske_igre, st_drzav, color = 'gray', edgecolor = 'white')
    plt.title('Stevilo drzav pri {} disciplini'.format(disciplina))
    plt.xlabel('Olimpijske igre')
    plt.ylabel('Stevilo drzav')
    plt.close()
    fig.savefig('grafi/stevilo_drzav_skozi_cas_pri_{}_disciplini.pdf'.format(disciplina))

def st_tek_iz_drzav(slovar):
    '''Stevilo tekmovalcev iz posameznih drzav'''
    drzave = []
    st_tekmovalcev = []

    # Naredimo sezname potrebne za risanje grafa
    for drzava in slovar:
        drzave.append(drzava)
        st_tekmovalcev.append(slovar[drzava])

    # Izris oz shranitev grafa
    fig = plt.figure(figsize=(14,10))
    plt.bar(drzave, st_tekmovalcev, color = 'pink', edgecolor = 'black')
    plt.title('Stevilo tekmovalcev iz posameznih drzav')
    plt.xlabel('Drzave')
    plt.ylabel('Stevilo tekmovalcev')   
    fig.autofmt_xdate()
    plt.close()
    fig.savefig('grafi/st_tek_iz_pos_drzave.pdf')

def men_vs_women(slovar, mendisciplina, womendisciplina):
    '''Primerjava moskih in zenskih zmagovalcev skozi cas pri doloceni disciplini.'''
    seznam1,seznam2=[[],[]]
    leto1,leto2=[[],[]]
    rezultat1,rezultat2=[[],[]] 

    for _, sez, _ in slovar[mendisciplina]:
        for s in sez:
            if s[2] == '':
                continue
            r = 0
            # Zapis v sekundah pri vseh disciplinah
            if s[2] == 'Did not start':
                continue
            if mendisciplina == '500m-men' or mendisciplina == '500m-women':
                if ':' in s[2]:
                    razrez = s[2].split(':')    
                    j = razrez[0]
                    i = razrez[1]
                    r += float(j)*60 + float(i)
                    r = r/2
                else:
                    r += float(s[2])
            else:
                if ':' in s[2]:
                    razrez = s[2].split(':')
                    j = razrez[0]
                    i = razrez[1]
                    r += float(j)*60 + float(i)
                else:
                    r += float(s[2])
            if s[1] == '1':
                try:
                    seznam1.append((int(s[0]),r))
                except:
                    continue

    for _, sez, _ in slovar[womendisciplina]:
        for s in sez:
            if s[2] == '':
                continue
            r = 0
            # Zapis v sekundah pri vseh disciplinah
            if s[2] == 'Did not start':
                continue
            if womendisciplina == '500m-men' or womendisciplina == '500m-women':
                if ':' in s[2]:
                    razrez = s[2].split(':')    
                    j = razrez[0]
                    i = razrez[1]
                    r += float(j)*60 + float(i)
                    r = r/2
                else:
                    r += float(s[2])
            else:
                if ':' in s[2]:
                    razrez = s[2].split(':')
                    j = razrez[0]
                    i = razrez[1]
                    r += float(j)*60 + float(i)
                else:
                    r += float(s[2])
            if s[1] == '1':
                try:
                    seznam2.append((int(s[0]),r))
                except:
                    continue

    # Naredimo sezname potrebne za risanje grafa
    for i, j in sorted(seznam1[::-1]):
        leto1.append(i)
        rezultat1.append(j)
    for i, j in sorted(seznam2[::-1]):
        leto2.append(i)
        rezultat2.append(j)

    # Izris oz shranitev grafa
    fig = plt.figure()
    plt.plot(leto1, rezultat1, marker = 'o', color = 'gold', markeredgecolor = 'white', zorder = 0, label = "moski")
    plt.plot(leto2, rezultat2, marker = 'o', color = 'gray', markeredgecolor = 'white', zorder = 0, label = "zenske")
    plt.title("Primerjava moskih in zenskih zmagovalcev skozi cas pri disciplini {}".format(mendisciplina[:-4]))
    plt.xlabel("Leta")
    plt.ylabel("Rezultati")
    plt.legend(loc = 'best')
    plt.close()
    fig.savefig('grafi/primerjava moskih in zenskih zmagovalcev skozi cas pri disciplini {}.pdf'.format(mendisciplina[:-4]))

def narisi_zemlevid(slovar_kolicin, slovar_koordinat):
    '''Funkcija izrise zemljevid in velicina pik oznacuje stevilo tekmovalcev iz te drzave.'''
    drzave = []
    kolicina = []
    longitudes = []
    latitudes = []

    for drzava in slovar_kolicin:
        if drzava in slovar_koordinat:
            drzave.append(drzava)
            kolicina.append(slovar_kolicin[drzava])
            latitudes.append(slovar_koordinat[drzava][0])
            longitudes.append(slovar_koordinat[drzava][1])

    fig = plt.figure(figsize = (16,11))
    map = Basemap()
    map.drawcoastlines()
    map.drawmapboundary(fill_color = 'blue')
    map.fillcontinents(color = 'black', lake_color = 'blue')

    for i in range(len(drzave)):
        plt.scatter(longitudes[i], latitudes[i], marker = 'o', s = kolicina[i], c = 'white', edgecolors = 'gray', zorder = 2*(len(drzave)-1-i))
    plt.title('Od kod prihajajo tekmovalci')
    plt.ylabel('Country latitude')
    plt.xlabel('Country longitude')    
    plt.close()
    fig.savefig('grafi/od kod prihajajo tekmovalci.pdf')

seznam ={}
seznam_tekmovalcev = set()
results = []
rd = []
countries = []
podatki_tekmovalcev={}
koordinate = []

# Klici funkcij

imenik()
pridobitev_podatkov_tekmovalcev()
zapis_imen(seznam_tekmovalcev)
rojstni_dnevi()

shrani_podatke()

# Podatki, ki jih rabimo

# za izris zemljevida
slovar_kolicin = Tekmovalci(podatki_tekmovalcev).tekmovalec_in_drzava()
narisi_zemlevid(slovar_kolicin, tabela_koordinat())

# za funkcijo plot_evolve
slovar1 = Tekmovalci(podatki_tekmovalcev).zmagovalci_po_disciplinah()
for disciplina in discipline:
    plot_evolve(slovar1, disciplina)

# za funkcijo bar_st_drzav_po_disc 
for disciplina in discipline:
    slovar2 = Tekmovalci(podatki_tekmovalcev).st_raz_drzav_pri_disc(disciplina)
    bar_st_drzav_po_disc(slovar2, disciplina)

# za funkcijo st_tek_iz_drzav   
drzave = Tekmovalci(podatki_tekmovalcev).tekmovalec_in_drzava()
st_tek_iz_drzav(drzave)

#za funkcijo men_vs_women
seznam3 = [('500m-men', '500m-women'),('1000m-men', '1000m-women'),
        ('1500m-men','1500m-women'),('5000m-men', '5000m-women')]
for men, women in seznam3:
    men_vs_women(slovar1,men,women)

def linearna_regresija():
    '''Funkcija napove čase v sekundah za naslednje olimpijske igre po posameznih disciplinah'''
    slovar1 = Tekmovalci(podatki_tekmovalcev).zmagovalci_po_disciplinah()
    for disciplina in discipline:
        model = LinearRegression()
        X, y = plot_evolve(slovar1, disciplina)
        X1 = []
        for el in X:
            el = [int(el)]
            X1.append(el)
        X = np.array(X1, dtype=float)
        model.fit(X, y)
        X_predict = [[2026]]
        y_predict = model.predict(X_predict)

        print(f'Na zimskih olimpijskih igrah leta 2026 je pri disciplini {disciplina} hitrostno drsanje predviden zmagovalen rezultat {round(y_predict[0],2)} sekund.')

linearna_regresija()