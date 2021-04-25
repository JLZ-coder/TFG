from .Builder import Builder
from pymongo import MongoClient
import markdown
import pypandoc
import os
from model.gdriveUploader import gDriveUploader

class ReportBuilder(Builder):
    def __init__(self):
        super().__init__("report")

    def reportPDF(self, filepath, pdfpath=None):
        if pdfpath == None:
            pdfpath, old_ext = os.path.splitext(filepath)
            pdfpath += ".pdf"

        output = pypandoc.convert_file(filepath, 'pdf', outputfile=pdfpath, extra_args=['-H', 'markdown/header.sty'])

        return pdfpath

    def pdf_to_drive(self, filepath, title=None, folder=None):
        uploader = gDriveUploader()
        uploader.upload_file(filepath, title, folder)

    def create(self, start, end, parameters):
        
        client = MongoClient('mongodb://localhost:27017/')
        db = client.lv
        brotes_db = db.outbreaks
        comarca_db = db.comarcas

        cabecera = ("# DiFLUsion: Informe de Alerta Semanal \n\n - *Fecha*: " +  start.strftime('%Y-%m-%d') 
        + "\n - *Periodo de*: " +   start.strftime('%Y-%m-%d') + " a " + end.strftime('%Y-%m-%d') + "\n")

        cabeceraTablaAlertas = ("\n\n## Tabla de alertas \n" 
        + "| Nº | Fecha  | Comarca  | ID CG | Nº brotes | Nº mov. Riesgo | Grado alerta | Temperatura estimada  | Supervivencia del virus en días |\n"
        + "|:-:|:-------:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|\n")

        cabeceraGenericaTablaBrotesAlertas = "\n\n## Tablas de brotes de IAAP en Europa y su conexión a España a través de  movimientos de aves silvestres"
        
        tablaBrotesAlertas = ("\n| ID | Event ID | Reporting date |Observational date |Country |Location | Latitud | Longitud | An. Type | Species | Cases | Deaths | Especie movimiento |Cód.  Especie | Prob mov semanal |\n" 
        +"|:-:|:---------:|:----------------:|:-------------:|:--------------:|:-----------:|:------------:|:-----------:|:-------------:|:----------:|:--------:|:--------:|:----------------:|:--------------:|:------------------:|\n" )
       
        todosBrotes = ""
        nAlerta = 1
        filasAlertas = ""
        filasBrotes = ""
        nBrote = 0
        allNBrotes = 0
        for alerta in parameters['alertas']:
            #Sacar informacion de la comarca
            
            cursor = list(comarca_db.find({'comarca_sg': alerta['comarca_sg']}))
            comarca = cursor[0]
            filasAlertas += ("|" +  str(nAlerta) + "|" + end.strftime('%Y-%m-%d') + "|" + comarca['com_sgsa_n'] + "|" + alerta['comarca_sg'] 
            + "|" + str(len(alerta['brotes'])) + "|" + "N mov Riesgo" + "|" + str(alerta["risk"])+ "|" + str(round(alerta["temperatura"],4)) + "|" 
            + "Supervivencia" + "|\n" )

            encabezadoTablasBrotesAlertas = ("\n\n### Alerta {} \n".format(nAlerta)
            + "- *Id comarca*: "+ alerta['comarca_sg'] + "\n"
            + "- *Localización comarca*: " +  comarca['com_sgsa_n'] + "\n")

            
            #Sacar informacion de brotes
            for brote, especie in alerta['brotes'].items():
                cursor = list(brotes_db.find({'oieid': brote}))
                broteMongo = cursor[0]

                if 'city' not in broteMongo:
                    broteMongo['city'] = "Not especified"

                filasBrotes += ("| "  + str(nBrote)  + "| " + str(brote)
                + "|" + broteMongo['report_date'].strftime('%Y-%m-%d')  + "|" + broteMongo['observation_date'].strftime('%Y-%m-%d') + "|" + broteMongo['country']  + "|" + broteMongo['city'] 
                + "|" + str(broteMongo['lat']) + "|" + str(broteMongo['long']) + "|" +broteMongo['epiunit']  + "|" + especie['cientifico']  + "|" + str(broteMongo['cases'])
                + "|" + str(broteMongo['deaths'])  + "|" +especie['especie']  + "|" + str(especie["codigoE"]) + "|" + str(round(especie["probEspecie"],4)) + "|\n" )

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

        informePath = "markdown/Informe_Semanal_" + start.strftime("%d-%m-%Y") + ".md"
        f = open (informePath,'w+', encoding="utf-8")
        f.write(textoFinal)
        f.close()

        informePdfPath = self.reportPDF(informePath)
        #informePdfName = informePdfPath.split("/")[-1]
        #self.pdf_to_drive(informePdfPath, informePdfName, "alertas")

        return textoFinal

