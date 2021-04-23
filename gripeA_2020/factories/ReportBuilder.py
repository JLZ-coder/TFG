from .Builder import Builder
from pymongo import MongoClient
import markdown
import pypandoc
import os
from model.gdriveUploader import gDriveUploader

class ReportBuilder(Builder):
    def __init__(self):
        super().__init__("report")

    def reportPDF(self):
        output = pypandoc.convert_file('markdown/informePrueba.md', 'pdf', outputfile="markdown/informePrueba.pdf", extra_args=['-H', 'markdown/header.sty'])

    def pdf_to_drive(self):
        uploader = gDriveUploader()
        uploader.upload_file('markdown/informePrueba.pdf', 'informeCron.pdf', 'informeSemanal')

    def create(self, start, end, parameters):
        
        client = MongoClient('mongodb://localhost:27017/')
        db = client.lv
        brotes_db = db.outbreaks
        comarca_db = db.comarcas

        cabecera = ("# DiFLUsion: Informe de Alerta Semanal \n\n - *Fecha*: " +  start.strftime('%Y-%m-%d') 
        + "\n - *Periodo de*: " +   start.strftime('%Y-%m-%d') + " a " + end.strftime('%Y-%m-%d') + "\n")

        sumario = ("\n## Sumario del informe \n" +  " - *Número de comarcas ganaderas en alerta*: " + str(len(parameters['alertas']))
        + "\n - *Número de brotes en Europa asociados con movimientos de riesgo a España*: " + str(parameters["nBrotes"]))

        cabeceraTablaAlertas = ("\n\n## Tabla de alertas \n " 
        + "| Nº | Fecha  | Comarca  | ID CG | Nº brotes | Nº mov. Riesgo | Grado alerta | Temperatura estimada  | Supervivencia del virus en días | Validacion\n"
        + "|:-:|:-------------:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|\n")

        cabeceraTablaBrotesAlertas = ("\n\n## Tablas de brotes de IAAP en Europa y su conexión a España a través de  movimientos de aves silvestres\n "
        +"| ID | Nº alerta | Comarca | ID CG | Event ID | Reporting date |Observational date |Country |Location | Latitud | Longitud | An. Type | Species | Cases | Deaths | Especie movimiento |Cód.  Especie | Prob mov semanal |\n" 
        +"|:-:|:---:|:--------------:|:------------:|:---------:|:----------------:|:-------------:|:--------------:|:-----------:|:------------:|:-----------:|:-------------:|:----------:|:--------:|:--------:|:----------------:|:--------------:|:------------------:|\n" )
        
        nAlerta = 1
        filasAlertas = ""
        filasBrotes = ""
        nBrote = 1
        for alerta in parameters['alertas']:
            #Sacar informacion de la comarca
            if alerta["risk"] > 0:
                cursor = list(comarca_db.find({'comarca_sg': alerta['comarca_sg']}))
                comarca = cursor[0]
                filasAlertas += ("|" +  str(nAlerta) + "|" + end.strftime('%Y-%m-%d') + "|" + comarca['com_sgsa_n'] + "|" + alerta['comarca_sg'] 
                + "|" + str(len(alerta['brotes'])) + "|" + "N mov Riesgo???" + "|" + str(alerta["risk"])+ "|" + str(alerta["temperatura"]) + "|" 
                + "Supervivencia?????" + "|"  +"Validacion??" + "|")

                #Sacar informacion de brotes
                for brote, especie in alerta['brotes'].items():
                    cursor = list(brotes_db.find({'oieid': brote}))
                    broteMongo = cursor[0]
                    filasBrotes += ("| "  + str(nBrote)  + "| "  + str(nAlerta) + "| " + comarca['com_sgsa_n'] + "|" + alerta['comarca_sg'] + "|" + str(brote)
                    + "|" + broteMongo['report_date'].strftime('%Y-%m-%d')  + "|" + broteMongo['observation_date'].strftime('%Y-%m-%d') + "|" + broteMongo['country']  + "|" + broteMongo['location'] 
                    + "|" + str(broteMongo['lat']) + "|" + str(broteMongo['long']) + "|" +broteMongo['epiunit']  + "|" + especie['cientifico']  + "|" + str(broteMongo['cases'])
                    + "|" + str(broteMongo['deaths'])  + "|" +especie['especie']  + "|" + str(especie["codigoE"]) + "|" + str(especie["probEspecie"]) + "|\n" )

                    nBrote+=1
                nAlerta += 1

        #Volcar fichero
        if len(parameters['alertas']) > 0:
            textoFinal = cabecera + sumario + cabeceraTablaAlertas + filasAlertas + cabeceraTablaBrotesAlertas + filasBrotes
        else:
            textoFinal = cabecera + sumario

        f = open ('markdown/informePrueba.md','w', encoding="utf-8")
        f.write(textoFinal)
        f.close()

        self.reportPDF()
        self.pdf_to_drive()

        return textoFinal

