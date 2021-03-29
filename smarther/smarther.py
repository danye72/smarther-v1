# v6.0.3
# gestione spegnimento boost

from datetime import datetime, timedelta
import requests, json, time, sys, pathlib

nome_script, nome, funz, val = sys.argv

path_dir = "/config/smarther/"
#path_dir = "/home/daniele/Scrivania/smarther/"

max_rit_webhook = 60 #secondi

################
#   CLASSI     #
################

class Termostato:

    def __init__(self,nome):

        self.nome = nome
        
        with open(path_dir +"conf_smarther.json") as f:
            self.conf = json.load(f)
                    
        if not 'plants' in self.conf:
            r=requests.get('https://api.developer.legrand.com/smarther/v2.0/plants',
            headers={
            "content-type" : "text",
            "Ocp-Apim-Subscription-Key" : self.conf["primary_key"],
            "Authorization" : "Bearer " + str(Termostato.token(self,"access_token")) 
                }
            )
            self.plant_id_total = json.loads((r.text))
            self.conf.update(self.plant_id_total)
            with open(path_dir +"conf_smarther.json", 'w') as outfile:
                json.dump(self.conf, outfile, indent=2)
                Termostato.log(self, "plant_id recuperate")

        if not 'c2c' in self.conf:
            headers={
            "Host": "api.developer.legrand.com",
            "content-type" : "application/json",
            "Ocp-Apim-Subscription-Key" : self.conf["primary_key"],
            "Authorization" : "Bearer " + str(Termostato.token(self,"access_token"))                
            }

            payload = {
            "EndPointUrl": self.conf["c2c_url"] 
            }
            
            c2c_count = 0
            for id in self.conf["plants"]:
                r = requests.post('https://api.developer.legrand.com/smarther/v2.0/plants/' + self.conf["plants"][c2c_count]["id"] + '/subscription', data=json.dumps(payload), headers=headers)
                c2c_count += 1
            self.conf["c2c"] = "ok"
            with open(path_dir +"conf_smarther.json", 'w') as outfile:
                json.dump(self.conf, outfile, indent=2)
                Termostato.log(self, "c2c sottoscritto "+val)

        self.dati_termostato = {}
        self.get_topology()

        if self.nome == "webhooks":
            self.dati_webhook = json.loads(funz)
            self.module_id = self.dati_webhook[0]["data"]["chronothermostats"][0]["sender"]["plant"]["module"]["id"]
            self.get_nome()
        else:            
            self.get_module_id()

        self.get_plant_id()
        self.get_dati_termostato()
        self.log = {}    

    def token(self,key):
        path = pathlib.Path(path_dir +"token.json")
        if path.is_file():
            expires_on = False
            with open(path_dir +"token.json") as f:
                keys = json.load(f)
            if int(time.time()) < keys["expires_on"]:
                expires_on = True
            if expires_on == False:
                Termostato.log(self, "token scaduti, procedo al rinnovo... ")
                payload = {
                'client_id': self.conf["client_id"],
                'client_secret' : self.conf["client_secret"],
                'grant_type' : 'refresh_token',
                'refresh_token' : keys['refresh_token']
                }
                r = requests.post("https://partners-login.eliotbylegrand.com/token", data=payload)
                keys = json.loads((r.text))
                if 'expires_on' in keys:
                    with open(path_dir +"token.json", 'w') as outfile:
                        json.dump(keys, outfile, indent=2)
                        Termostato.log(self, "token rinnovati correttamente")
            return keys[key]
        else:
            payload = {
            'client_id':  self.conf["client_id"],
            'client_secret' : self.conf["client_secret"],
            'grant_type' : 'authorization_code',
            'code' : self.conf["code"]
            }
            r = requests.post("https://partners-login.eliotbylegrand.com/token", data=payload)
            keys = json.loads((r.text))
            if 'expires_on' in keys:
                with open(path_dir +"token.json", 'w') as outfile:
                    json.dump(keys, outfile, indent=2)
                    Termostato.log(self, "token generati")
            return keys[key]

    def get_nome(self):
        top_count = 0
        for plant in self.topology["plants"]:
            count = 0
            for modules in self.topology["plants"][top_count]["plant"]["modules"]:
                if self.module_id == self.topology["plants"][top_count]["plant"]["modules"][count]["id"]:
                    nome = self.topology["plants"][top_count]["plant"]["modules"][count]["name"]
                count += 1
            top_count += 1
        self.nome = nome

    def get_plant_id(self):
        top_count = 0
        for plant in self.topology["plants"]:
            count = 0
            for modules in self.topology["plants"][top_count]["plant"]["modules"]:
                if self.nome == self.topology["plants"][top_count]["plant"]["modules"][count]["name"]:
                    plant_id = self.topology["plants"][top_count]["plant"]["id"]
                count += 1
            top_count += 1
        self.plant_id = plant_id

    def get_module_id(self):
        top_count = 0
        for plant in self.topology["plants"]:
            count = 0
            for modules in self.topology["plants"][top_count]["plant"]["modules"]:
                if self.nome == self.topology["plants"][top_count]["plant"]["modules"][count]["name"]:
                    module_id = self.topology["plants"][top_count]["plant"]["modules"][count]["id"]
                count += 1
            top_count += 1
        self.module_id = module_id

    def get_topology(self):
        path = pathlib.Path(path_dir +"topology.json")
        refresh_topology = True
        if path.is_file():
            refresh_topology = False
            with open(path_dir +"topology.json") as f:
                topology = json.load(f)
        if refresh_topology == True:
            lista = []
            topology = {"plants":lista}
            id_count = 0
            for id in self.conf["plants"]:
                r=requests.get('https://api.developer.legrand.com/smarther/v2.0/plants/'+ self.conf["plants"][id_count]["id"] +'/topology',
                            headers={
                            "content-type" : "text",
                            "Ocp-Apim-Subscription-Key" : self.conf["primary_key"],
                            "Authorization" : "Bearer " + str(Termostato.token(self,"access_token")) 
                                }
                            )
                lista.append(json.loads((r.text)))
                id_count += 1
            with open(path_dir +"topology.json", 'w') as outfile:
                json.dump(topology, outfile, indent=2)
                Termostato.log(self, "file topology generato")
        self.topology = topology

    def get_dati_termostato(self):
        path = pathlib.Path(path_dir + self.nome + ".json")
        if path.is_file():
            with open(path_dir + self.nome + ".json", "r") as f:
                self.dati_termostato = json.load(f)
        else:
            Termostato.valori_api(self)

    def save_dati_termostato(self):
        with open(path_dir + self.nome + ".json", 'w') as outfile:
            json.dump(self.dati_termostato, outfile, indent=2)
            Termostato.log(self, self.nome+" - dati per homeassistant salvati")

    def active_program_name(self, program_number):
        count = 0
        for number in self.dati_termostato["programmi"]:
            if int(program_number) == self.dati_termostato["programmi"][count]["number"]:
                program_str = str(self.dati_termostato["programmi"][count]["number"]) + " - " + self.dati_termostato["programmi"][count]["name"]
            count = count + 1
        programma_attivo = {"programma_attivo":program_str}
        self.dati_termostato.update(programma_attivo)

    def get_programs(self):
        r=requests.get('https://api.developer.legrand.com/smarther/v2.0/chronothermostat/thermoregulation/addressLocation/plants/'+ str(self.plant_id) + '/modules/parameter/id/value/' + str(self.module_id) + "/programlist",
            headers={
            "content-type" : "text",
            "Ocp-Apim-Subscription-Key" : self.conf["primary_key"],
            "Authorization" : "Bearer " + str(Termostato.token(self,"access_token")) 
                }
            )
        programs_data = json.loads((r.text))
        if "chronothermostats" in programs_data:
            programs = programs_data["chronothermostats"][0]["programs"]
            lista_programmi = {"programmi":programs}
            programs_str = "["
            data = 0    
            for number in lista_programmi["programmi"]: 
                programs_str += "'" + str(lista_programmi["programmi"][data]["number"]) + " - " + lista_programmi["programmi"][data]["name"] + "',"
                data = data + 1
            programs_str += "]"
            programmi_stringa = {"select_programmi":programs_str}              
            self.dati_termostato.update(programmi_stringa)
            self.dati_termostato.update(lista_programmi)
            Termostato.log(self, self.nome+" - lista programmi aggiornati correttamente")
            Termostato.save_dati_termostato(self)

    def log(self, data_log):
        with open(path_dir + "log", "a+") as file_log:
            file_log.seek(0)
            data = file_log.read(100)
            if len(data) > 0 :
                file_log.write("\n")
            file_log.write(datetime.now().strftime(" %d/%m/%Y-%H:%M:%S")+" "+data_log)

    def check_status_webhook(self):
        if "delay" in self.dati_termostato:
            if self.dati_termostato["delay"] > max_rit_webhook or self.dati_termostato["api"] == "ko":
                    Termostato.valori_api(self)
        else:
            self.dati_termostato["delay"] = max_rit_webhook
            Termostato.valori_api(self)

    def valori_api(self):
        r=requests.get('https://api.developer.legrand.com/smarther/v2.0/chronothermostat/thermoregulation/addressLocation/plants/'+ str(self.plant_id) +'/modules/parameter/id/value/'+ str(self.module_id),
                    headers={
                    "content-type" : "text",
                    "Ocp-Apim-Subscription-Key" : self.conf["primary_key"],
                    "Authorization" : "Bearer " + str(Termostato.token(self,"access_token")) 
                        }
                    )
        dati_ricevuti = json.loads((r.text))
        # se ho dati validi
        if 'chronothermostats' in dati_ricevuti:
            valori_smarther = {
                "temperatura":dati_ricevuti["chronothermostats"][0]["thermometer"]["measures"][0]["value"],
                "umidita":dati_ricevuti["chronothermostats"][0]["hygrometer"]["measures"][0]["value"],
                "funzione":dati_ricevuti["chronothermostats"][0]["function"],
                "modo":dati_ricevuti["chronothermostats"][0]["mode"],
                "set_point":dati_ricevuti["chronothermostats"][0]["setPoint"]["value"],
                "stato":dati_ricevuti["chronothermostats"][0]["loadState"],
                "programma_attivo":dati_ricevuti["chronothermostats"][0]["programs"][0]["number"],
                "aggiornato":datetime.now().strftime("%H:%M:%S") + " api",
                "timestamp":datetime.now().timestamp(),
                "boost_type":0,
                "boost_remaining":0,
                "api":"ok"
            }           
            ########################### controllo se i boost è attivo
            if dati_ricevuti["chronothermostats"][0]["mode"] == "BOOST":
                boost_activationtime_str = dati_ricevuti["chronothermostats"][0]["activationTime"]
                boost_activatontime = datetime.strptime(boost_activationtime_str,"%Y-%m-%dT%H:%M:%S")
                now = datetime.now()
                boost_time_minutes = int(((boost_activatontime - now).total_seconds()-60) / 60)
                boost_time_seconds = int((boost_activatontime - now).total_seconds())
                if boost_time_minutes > 60:
                    boost_type = 90
                elif boost_time_minutes >= 30 and boost_time_minutes <= 60:
                    boost_type = 60
                elif boost_time_minutes <= 30:
                    boost_type = 30
                new_boost_type = {"boost_type":boost_type}
                boost_remaining = {"boost_remaining":boost_time_seconds}
                valori_smarther.update(new_boost_type)
                valori_smarther.update(boost_remaining)
            ###########################
            
            Termostato.log(self, self.nome+" - dati api ricevuti")
            self.dati_termostato.update(valori_smarther)

            ########################### Recupero la lista dei programmi ed estraggo il programma attivo
            if 'programmi' in self.dati_termostato:
                Termostato.active_program_name(self, valori_smarther["programma_attivo"])
                Termostato.save_dati_termostato(self)
            else:
                Termostato.get_programs(self)
                Termostato.active_program_name(self, valori_smarther["programma_attivo"])
            ###########################
            
        else:
            # scrivo l'errore nel file errori
            Termostato.log(self,r.text)

            # aggiorno l'ora dell'operazione segnalando l'errore ad HA
            self.dati_termostato["aggiornato"] = datetime.now().strftime("%H:%M:%S") + " err"

            # se ho terminato le richieste api giornaliere
            if "statusCode" in dati_ricevuti:
                if dati_ricevuti["statusCode"] == 403:
                    self.dati_termostato["api"] = "ko"
            Termostato.save_dati_termostato(self)

    def webhooks(self):
        Termostato.log(self, self.nome+" - webhook ricevuto")
        valori_smarther = {
            "temperatura":self.dati_webhook[0]["data"]["chronothermostats"][0]["thermometer"]["measures"][0]["value"],
            "umidita":self.dati_webhook[0]["data"]["chronothermostats"][0]["hygrometer"]["measures"][0]["value"],
            "funzione":self.dati_webhook[0]["data"]["chronothermostats"][0]["function"],
            "modo":self.dati_webhook[0]["data"]["chronothermostats"][0]["mode"],
            "set_point":self.dati_webhook[0]["data"]["chronothermostats"][0]["setPoint"]["value"],
            "stato":self.dati_webhook[0]["data"]["chronothermostats"][0]["loadState"],
            "programma_attivo":self.dati_webhook[0]["data"]["chronothermostats"][0]["programs"][0]["number"],
            "aggiornato":datetime.now().strftime("%H:%M:%S") + " web",
            "timestamp":datetime.now().timestamp(),
            "boost_type":0,
            "boost_remaining":0
        }
        
        # controllo se il webhook è valido
        webhook_data_time = int(datetime.strptime(self.dati_webhook[0]["data"]["chronothermostats"][0]["time"], "%Y-%m-%dT%H:%M:%S%z").timestamp())
        webhook_send_time = int(datetime.strptime(self.dati_webhook[0]["data"]["chronothermostats"][0]["thermometer"]["measures"][0]["timeStamp"], "%Y-%m-%dT%H:%M:%S%z").timestamp())
        #webhook_send_time = (int(datetime.now().timestamp()))
        webhook_delay=webhook_send_time-webhook_data_time
        if webhook_delay < 1:
            webhook_delay = 0           
        valori_smarther["delay"] = webhook_delay #valori_smarther["delay"] = time.strftime('%H:%M:%S', time.gmtime(diff_time))
        # accetto il webhook se....
        if (webhook_delay < max_rit_webhook) or (self.dati_termostato["timestamp"] <= webhook_data_time and self.dati_termostato["api"] == "ko"):
            Termostato.log(self, self.nome+" - webhook valido")
            ########################### controllo se i boost è attivo
            if self.dati_webhook[0]["data"]["chronothermostats"][0]["mode"] == "BOOST":
                boost_activationtime_str = self.dati_webhook[0]["data"]["chronothermostats"][0]["activationTime"]
                boost_activatontime = datetime.strptime(boost_activationtime_str,"%Y-%m-%dT%H:%M:%S")
                now = datetime.now()
                boost_time_minutes = int(((boost_activatontime - now).total_seconds()-60) / 60)
                boost_time_seconds = int((boost_activatontime - now).total_seconds())
                if boost_time_minutes > 60:
                    boost_type = 90
                elif boost_time_minutes >= 30 and boost_time_minutes <= 60:
                    boost_type = 60
                elif boost_time_minutes <= 30:
                    boost_type = 30
                new_boost_type = {"boost_type":boost_type}
                boost_remaining = {"boost_remaining":boost_time_seconds}
                valori_smarther.update(new_boost_type)
                valori_smarther.update(boost_remaining)
            ###########################
   
            self.dati_termostato.update(valori_smarther)

            ########################### Recupero la lista dei programmi ed estraggo il programma attivo
            if 'programmi' in self.dati_termostato:
                Termostato.active_program_name(self, valori_smarther["programma_attivo"])
                Termostato.save_dati_termostato(self)
            else:
                Termostato.get_programs(self)
                Termostato.active_program_name(self, valori_smarther["programma_attivo"])
            ###########################

        else:
            Termostato.log(self, self.nome+" - webhook scartato")
            self.dati_termostato["delay"] = webhook_delay
            Termostato.save_dati_termostato(self)
            
##################################### COMANDI #########################################################################

    def set_mode(self,mode,val):
        url = 'https://api.developer.legrand.com/smarther/v2.0/chronothermostat/thermoregulation/addressLocation/plants/'+ self.plant_id +'/modules/parameter/id/value/'+ self.module_id

        if mode == "programma":
            body = {
                    "function": self.dati_termostato["funzione"],
                    "mode": "automatic",
                    "setPoint": {
                        "value": 7,
                        "unit": "C"
                    },
                    "programs": [
                        {
                        "number": val[0:1]
                        }
                    ]
                    }
            Termostato.log(self, self.nome+" - impostato programma "+val)

        elif mode == "automatico":
            body = {
                    "function": self.dati_termostato["funzione"],
                    "mode": "automatic",
                    "setPoint": {
                        "value": 7,
                        "unit": "C"
                    },
                    "programs": [
                        {
                        "number": self.dati_termostato["programma_attivo"][0:1]
                        }
                    ]
                    }
            Termostato.log(self, self.nome+" - impostato in automatico con programma "+self.dati_termostato["programma_attivo"])

        elif mode == "set_point":
            body = {
                    "function": self.dati_termostato["funzione"],
                    "mode": "manual",
                    "setPoint": {
                        "value": val,
                        "unit": "C"
                    }
                    }
            Termostato.log(self, self.nome+" - impostato set pont a "+val+" gradi")

        elif mode == "manuale":
            body = {
                    "function": self.dati_termostato["funzione"],
                    "mode": "manual",
                    "setPoint": {
                        "value": val,
                        "unit": "C"
                    }
                    }
            Termostato.log(self, self.nome+" - impostato manuale a "+val+" gradi")

        elif mode == "protezione":
            body = {
                    "function": self.dati_termostato["funzione"],
                    "mode": "protection"
                    }
            Termostato.log(self, self.nome+" - impostato programma protezione")

        elif mode == "boost":
            now = datetime.now()
            time = now + timedelta(minutes=int(val))
            now_str = now.strftime("%Y-%m-%dT%H:%M:%S")
            time_str = time.strftime("%Y-%m-%dT%H:%M:%S")
            body = {
                    "function": self.dati_termostato["funzione"],
                    "mode": "boost",
                    "setPoint": {
                        "value": self.dati_termostato["temperatura"],
                        "unit": "C"
                    },
                    "programs": [
                        {
                            "number": str(self.dati_termostato["programma_attivo"])[0:1]
                        }
                    ],
                    "activationTime": now_str + "/" + time_str
                 }
            Termostato.log(self, self.nome+" - impostato boost "+val)

        elif mode == "funzione":
            body = {
                    "function": val,
                    "mode": "manual",
                    "setPoint": {
                        "value": self.dati_termostato["set_point"],
                        "unit": "C"
                    }
                    }
            Termostato.log(self, self.nome+" - impostato modo funzionamento "+val)

        headers = {
                    'Content-Type' : 'application/json',
                    'Ocp-Apim-Subscription-Key' : self.conf["primary_key"],
                    'Authorization' : 'Bearer ' + str(Termostato.token(self,"access_token"))
                }
        r = requests.post(url, data=json.dumps(body), headers=headers)

        # aggiorno i valori per homeassistant dopo averli impostati
        Termostato.valori_api(self)
        
        










termostato = Termostato(nome)
if nome != "webhooks":
    if funz == "programma":
        termostato.set_mode("programma", val)
    if funz == "valori_api":      
        termostato.check_status_webhook()
    if funz == "set_point":
        termostato.set_mode("set_point", val)
    if funz == "manuale":
        termostato.set_mode("manuale", val)
    if funz == "automatico":
        termostato.set_mode("automatico", val)
    if funz == "protezione":
        termostato.set_mode("protezione", val)
    if funz == "boost":
        termostato.set_mode("boost", val)
    if funz == "funzione":
        termostato.set_mode("funzione", val)
    if funz == "get_programs":
        termostato.get_programs()

if nome == "webhooks":
    termostato.webhooks()
