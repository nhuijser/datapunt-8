# import modulen
from pathlib import Path
import json
import pprint
from database_wrapper import Database

# initialisatie

# parameters voor connectie met de database
db = Database(host="localhost", gebruiker="user", wachtwoord="password", database="attractiepark")


# main

# Haal de eigenschappen op van een personeelslid
# altijd verbinding openen om query's uit te voeren
db.connect()

# pas deze query aan om het juiste personeelslid te selecteren
personeelslid_nummer = 3
personeelslid = Path(f"personeelsgegevens_personeelslid_{personeelslid_nummer}.json")

if personeelslid.exists():
  personeelslid = json.loads(personeelslid.read_text(encoding="utf-8"))
else:
    print(f"{personeelslid} bestaat niet")


# select_query = "SELECT * FROM personeelslid WHERE id = 1"
# personeelslid = db.execute_query(select_query)

# altijd verbinding sluiten met de database als je klaar bent
db.close()

# BEREKEN MAX FYSIEKE BELASTING
leeftijd = int(personeelslid['leeftijd'])

if leeftijd <= 24:
    max_fysieke_belasting = 25
elif leeftijd <= 50:
    max_fysieke_belasting = 40
else:
    max_fysieke_belasting = 20

if personeelslid['verlaagde_fysieke_belasting']:
    max_fysieke_belasting = int(personeelslid['verlaagde_fysieke_belasting'])

# EINDE BEREKENEN MAX FYSIEKE BELASTING

db.connect()

# pas deze query aan en voeg queries toe om de juiste onderhoudstaken op te halen
select_query = "SELECT * FROM onderhoudstaak WHERE afgerond = 0 AND beroepstype = %s AND bevoegdheid = %s AND fysieke_belasting <= %s"
params = (personeelslid['beroepstype'], personeelslid['bevoegdheid'], max_fysieke_belasting)
onderhoudstaken = db.execute_query(select_query, params)

db.close()

        

totale_duur = 0
for taak in onderhoudstaken:
    totale_duur += taak['duur']

# verzamel alle benodigde gegevens in een dictionary
dagtakenlijst = {
    "personeelsgegevens" : {
        "naam": personeelslid['naam'], # voorbeeld van hoe je bij een eigenschap komt
        "werktijd": personeelslid['werktijd'],
        "beroepstype": personeelslid['beroepstype'],
        "bevoegdheid": personeelslid['bevoegdheid'],
        "specialist_in_attracties": personeelslid['specialist_in_attracties'],
        "pauze_opsplitsen": bool(personeelslid['pauze_opsplitsen']),
        "leeftijd": personeelslid['leeftijd'],
        "max_fysieke_belasting": max_fysieke_belasting,
    },
    "weergegevens" : {
        # STAP 4: vul aan met weergegevens
    }, 
    "dagtaken": onderhoudstaken # STAP 2: hier komt een lijst met alle dagtaken
    ,
    "totale_duur": totale_duur 
}

# uiteindelijk schrijven we de dictionary weg naar een JSON-bestand, die kan worden ingelezen door de acceptatieomgeving
with open(f'dagtakenlijst_personeelslid_{personeelslid_nummer}.json', 'w') as json_bestand_uitvoer:
    json.dump(dagtakenlijst, json_bestand_uitvoer, indent=4)
    print(f"dagtakenlijst_personeelslid_{personeelslid_nummer}.json weggeschreven")