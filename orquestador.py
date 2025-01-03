import os
import time
import pandas as pd
import pytz
import smtplib
from colorama import Fore
from datetime import date, timedelta, datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


def print_e(msg):
    print(Fore.RED+ msg +Fore.RESET)


def print_w(msg):
    print(Fore.YELLOW+ msg +Fore.RESET)


def send_email(df):
    today = date.today().strftime("%d_%m_%Y")

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Precios farmacias"
    msg['From'] = "gustavo@sintetiqai.com"
    msg['To'] = 'gustavo.gilramos@gmail.com'
    msg['Cco'] = 'iswjuanamaya@gmail.com'

    recipients = ["iswjuanamaya@gmail.com", "gustavo.gilramos@gmail.com"]

    attachment = MIMEApplication(df.to_csv())
    filename = f"precios_{today}.csv"
    attachment["Content-Disposition"] = 'attachment; filename=" {}"'.format(filename)
    msg.attach(attachment)

    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login("gustavo@sintetiqai.com", "dkalldlzavstssga" )
    smtp_server.sendmail("gustavo@sintetiqai.com", recipients, msg.as_string())
    smtp_server.quit()


def generate_df(tipo:str)->str:
    """ """
    def homologar(df):
        desc =  df['descripcion']
        med = df['medicamento']
        peso = df['peso']
        pres =df['presentacion']
        ff = df['forma_farmacologica']
        marca = str(df['marca'])
        
        if med not in desc.lower() and med not in marca.lower():
            return ""
        if not peso and not pres:
            return ""

        # perfect match
        df_c = dfm[ (dfm['name']==med) & (dfm['peso']==peso) & (dfm['presentacion']==pres) ]
        coinc = len(df_c)
        if coinc > 0:
            return str(df_c['Medicamento'].iloc[0]).strip()
        
        return str(desc).strip().upper()

    today = date.today().strftime("%d/%m/%Y")
    today_datetime = date.today()
    df = pd.read_csv('precios.csv')
    df.fillna("", inplace=True)
    dfm  = pd.read_csv('medicamentos_base_homologada.csv')

    if tipo == "normal":
        #Selecciona lo recolectado en el día
        df = df[df['scrapping_day'] == today].copy()
        
        #Homologa la BDD
        df['descripcion'] = df.apply(homologar, axis=1)

        #Ignora medicamentos que no se pudieron homolgar ni sinteticamente
        day_df = df[['descripcion', 'marca', 'precio', 'max_price',
                    'precio descontado', 'descuento', 'promotion', 'fuente',
                    'scrapping_day', 'detail_url']][df['descripcion'] != ''].copy()
        
    elif tipo == "lunes":
        sab_dom_lun = [
                today_datetime.strftime("%d/%m/%Y"),
                (today_datetime - timedelta(1)).strftime("%d/%m/%Y"), 
                (today_datetime - timedelta(2)).strftime("%d/%m/%Y") 
            ]
        day_df = df[df['scrapping_day'].isin(sab_dom_lun)].copy()

    return day_df


def main():
    today_datetime = date.today()
    scripts = ["farmacia_Del_Ahorro.py", "farmacia_guadalajara.py",  "farmacias_benavides.py", "farmacias_San_Pablo.py"]
    #scripts = []
    for script in scripts:
        print(f"///////////////++++++++++++++++++++++ ejecutando {script} ++++++++++++++++++++++////////////////")
        if os.name == 'nt':
            os.system(f"python {script}")
        else: 
            os.system(f"python3 {script}")

        print("\n\nEsperando para siguiente ejecución.")
        print("<----------")
        time.sleep(1)
        print("<---------")
        time.sleep(1)
        print("<--------")
        time.sleep(1)
        print("<-------")
        time.sleep(1)
        print("<------")
        time.sleep(1)
        print("<-----")
        time.sleep(1)
        print("<----")
        time.sleep(1)
        print("<---")
        time.sleep(1)
        print("<--")
        time.sleep(1)
        print("<-")
        time.sleep(1)

    print("///////////////////////++++++++++++++++++++++ FIN DE LA EJECUCION DE LOS SCRAPPERS ++++++++++++++++++++++////////////////")
    
    print("\n")

    print("/++++++++++++++++++++++ INICIA EJECUCIÓN DE ALERTA ++++++++++++++++++++++")

    #martes-viernes
    if today_datetime.weekday() in [1,2,3,4]:
        df = generate_df("normal")
        send_email(df)
    
    #lunes
    elif today_datetime.weekday() == 0:
        df = generate_df("lunes")
        send_email(df)
    
    # fin de semana no se envian alertas
    elif today_datetime.weekday() in [5,6]:
        print("--> Hoy es fin de semana, no se envian alertas")

if __name__ == "__main__":
    main()
