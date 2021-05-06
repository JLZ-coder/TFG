from .Builder import Builder
from pymongo import MongoClient
import markdown
import pypandoc
import os
from model.gdriveUploader import gDriveUploader
import unicodecsv as csv
import codecs
import os
from os import remove
class ReportBuilder(Builder):
    uploader = gDriveUploader()

    def __init__(self):
        super().__init__("report")

    def reportPDF(self, filepath, pdfpath=None):
        if pdfpath == None:
            pdfpath, old_ext = os.path.splitext(filepath)
            pdfpath += ".pdf"

        output = pypandoc.convert_file(filepath, 'pdf', outputfile=pdfpath, extra_args=['-H', 'markdown/header.sty'])

        return pdfpath

    def file_to_drive(self, filepath, title=None, folder=None):
        self.uploader.upload_file(filepath, title, folder)

    def load_csv(self, cabeceraAlertas, cabeceraBrotes, nuevasAlertas, nuevosBrotes):
        #CSV generales
        alertasDrive = None
        brotesDrive = None
        #CSV Alertas
        if not os.path.isfile("markdown/alertasDriveNewModelo.csv"): 
            alertasDrive = codecs.open("markdown/alertasDriveNewModelo.csv", "wb+")  
            writer = csv.DictWriter(alertasDrive, fieldnames=cabeceraAlertas)         
            writer.writeheader()
        else: 
            alertasDrive = codecs.open("markdown/alertasDriveNewModelo.csv", "ab+") 
            writer = csv.DictWriter(alertasDrive, fieldnames=cabeceraAlertas)

        writer.writerows(nuevasAlertas)
        alertasDrive.close()
        self.file_to_drive("markdown/alertasDriveNewModelo.csv", "alertasNewModelo.csv", "alertas")

        #CSV Brotes
        
        if not os.path.isfile("markdown/brotesDriveNewModelo.csv"):
            brotesDrive = codecs.open("markdown/brotesDriveNewModelo.csv", "wb+")
            writer = csv.DictWriter(brotesDrive, fieldnames=cabeceraBrotes)
            writer.writeheader()
        else:
            brotesDrive = codecs.open("markdown/brotesDriveNewModelo.csv", "ab+")
            writer = csv.DictWriter(brotesDrive, fieldnames=cabeceraBrotes)

        writer.writerows(nuevosBrotes)
        brotesDrive.close()
        self.file_to_drive("markdown/brotesDriveNewModelo.csv", "brotesNewModelo.csv", "alertas")
        
    def create(self, start, end, parameters):
        
        client = MongoClient('mongodb://localhost:27017/')
        db = client.lv
        brotes_db = db.outbreaks
        comarca_db = db.comarcas

        cabecera = ("# DiFLUsion: Informe de Alerta Semanal \n\n - *Fecha*: " +  start.strftime('%d-%m-%Y') 
        + "\n - *Periodo de*: " +   start.strftime('%d-%m-%Y') + " a " + end.strftime('%d-%m-%Y') + "\n")

        cabeceraTablaAlertas = ("\n\n## Tabla de alertas \n" 
        + "| Nº | Fecha  | Comarca  | ID CG | Nº brotes | Nº mov. Riesgo | Grado alerta | Temperatura estimada  | Supervivencia del virus en días |\n"
        + "|:-:|:-------:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|\n")

        cabeceraGenericaTablaBrotesAlertas = "\n\n## Tablas de brotes de IAAP en Europa y su conexión a España a través de  movimientos de aves silvestres"
        
        tablaBrotesAlertas = ("\n| ID | Event ID | Reporting date |Observational date |Country |Location | Latitud | Longitud | An. Type | Species | Cases | Deaths | Especie movimiento |Cód.  Especie | Prob mov semanal |\n" 
        +"|:-:|:---------:|:----------------:|:-------------:|:--------------:|:-----------:|:------------:|:-----------:|:-------------:|:----------:|:--------:|:--------:|:----------------:|:--------------:|:------------------:|\n" )

        #CSV
        csvCabeceraAlertas = ["Nº","Fecha","Comarca","ID CG","Nº brotes","Nº mov. Riesgo","Grado alerta","Temperatura estimada","Supervivencia del virus en días"]
        csvCabeceraBrotes = ["ID","Nº Alerta","Comarca","ID CG", "Grado alerta", "Fecha Alerta", "Event ID", "Temperatura estimada", "Supervivencia del virus en días",
        "Reporting date","Observational date", "Country", "Location", "Latitud", "Longitud", "Ponderacion brote", "Riesgo brote", "An. Type","Species", "Cases", "Deaths","Especie movimiento", "Cód.  Especie", "Prob mov semanal"]
        
        
        todosBrotes = ""
        nAlerta = 1
        filasAlertas = ""
        filasBrotes = ""
        nBrote = 0
        allNBrotes = 0

        #csv
        filasAlertasCsv = []
        filasBrotesCsv = []
        for alerta in parameters['alertas']:
            #Sacar informacion de la comarca
            
            cursor = list(comarca_db.find({'comarca_sg': alerta['comarca_sg']}))
            comarca = cursor[0]

            alerta["temperatura"] = "No data" if alerta['temperatura'] == "No data" else round(alerta["temperatura"],2)
            filasAlertas += ("|" +  str(nAlerta) + "|" + start.strftime('%d-%m-%Y') + "|" + comarca['com_sgsa_n'] + "|" + alerta['comarca_sg'] 
            + "|" + str(len(alerta['brotes'])) + "|" + str(alerta['movRiesgo']) + "|" + str(alerta["risk"])+ "|" + str(alerta["temperatura"]) + "|" 
            + str(round(alerta['super'],4)) + "|\n" )

            encabezadoTablasBrotesAlertas = ("\n\n### Alerta {} \n".format(nAlerta)
            + "- *Id comarca*: "+ alerta['comarca_sg'] + "\n"
            + "- *Localización comarca*: " +  comarca['com_sgsa_n'] + "\n")

            #Csv
            filasAlertasCsv.append({"Nº": nAlerta ,"Fecha": start.strftime('%d-%m-%Y') ,"Comarca": comarca['com_sgsa_n'],"ID CG": alerta['comarca_sg'] ,"Nº brotes": len(alerta['brotes']),
            "Nº mov. Riesgo": alerta['movRiesgo'] ,"Grado alerta": alerta["risk"],"Temperatura estimada": alerta["temperatura"] ,"Supervivencia del virus en días": round(alerta['super'],4)})
            
            #Sacar informacion de brotes
            for brote, especie in alerta['brotes'].items():
                cursor = list(brotes_db.find({'oieid': brote}))
                broteMongo = cursor[0]

                if 'city' not in broteMongo:
                    broteMongo['city'] = "Not especified"

                filasBrotes += ("| "  + str(nBrote)  + "| " + str(brote)
                + "|" + broteMongo['report_date'].strftime('%d-%m-%Y')  + "|" + broteMongo['observation_date'].strftime('%d-%m-%Y') + "|" + broteMongo['country']  + "|" + broteMongo['city'] 
                + "|" + str(broteMongo['lat']) + "|" + str(broteMongo['long']) + "|" +broteMongo['epiunit']  + "|" + especie['cientifico']  + "|" + str(broteMongo['cases'])
                + "|" + str(broteMongo['deaths'])  + "|" +especie['especie']  + "|" + str(especie["codigoE"]) + "|" + str(round(especie["probEspecie"],4)) + "|\n" )
                
                filasBrotesCsv.append({
                    "ID": nBrote,"Nº Alerta": nAlerta,"Comarca": comarca['com_sgsa_n'],"ID CG": alerta['comarca_sg'], 
                    "Grado alerta": alerta["risk"], "Fecha alerta": start.strftime('%d-%m-%Y'),
                    "Event ID": brote, "Temperatura estimada": alerta["temperatura"],
                    "Supervivencia del virus en días": round(alerta['super'],4),
                    "Reporting date": broteMongo['observation_date'].strftime('%d-%m-%Y'),
                    "Observational date": broteMongo['observation_date'].strftime('%d-%m-%Y'), 
                    "Country": broteMongo['country'], "Location": broteMongo['city'], 
                    "Latitud": broteMongo['lat'], "Longitud": broteMongo['long'],
                    "Ponderacion brote": especie['probType'], "Riesgo brote": especie['riesgoBrote'],
                    "An. Type": broteMongo['epiunit'],"Species": especie['cientifico'], "Cases": broteMongo['cases'], 
                    "Deaths": broteMongo['deaths'],"Especie movimiento": especie['especie'], 
                    "Cód.  Especie": especie["codigoE"], "Prob mov semanal":round(especie["probEspecie"],4)
                })
                nBrote+=1
        

            #Creamos tabla de brotes de la alerta i
            todosBrotes += encabezadoTablasBrotesAlertas + tablaBrotesAlertas + filasBrotes
            nAlerta += 1
            allNBrotes += nBrote
            filasBrotes = ""
            nBrote=0

        sumario = ("\n## Sumario del informe \n" +  " - *Número de comarcas ganaderas en alerta*: " + str(len(parameters['alertas']))
        + "\n - *Número de brotes en Europa asociados con movimientos de riesgo a España*: {}".format(allNBrotes))
        
        #Volcar fichero
        if len(parameters['alertas']) > 0:
            textoFinal = cabecera + sumario + cabeceraTablaAlertas + filasAlertas + cabeceraGenericaTablaBrotesAlertas + todosBrotes
        else:
            textoFinal = cabecera + sumario

        #Creamos csv brotes
        self.load_csv(csvCabeceraAlertas, csvCabeceraBrotes, filasAlertasCsv, filasBrotesCsv)

        #Actualizacion
        informePath = "markdown/InformeSemanal_" + start.strftime("%d-%m-%Y") + ".md"
        f = open (informePath,'w+', encoding="utf-8")
        f.write(textoFinal)
        f.close()

        #informePdfPath = self.reportPDF(informePath)
        #informePdfName = informePdfPath.split("/")[-1]
        #self.file_to_drive(informePdfPath, informePdfName, "alertas")

        return textoFinal

