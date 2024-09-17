import requests
from lxml import html
from datetime import datetime
import re
import time
import random
import pandas as pd
from colorama import Fore

key_medicines = [
    'GIOTRIF', 'TARCEVA', 'IRESSA', 'VARGATEF', 'TAXOTERE', 'KEYTRUDA', 'OPDIVO', 'ACTILYSE',
    'METALYSE', 'VARIDASA', 'OFEV', 'KITOSCELL', 'SERETIDE', 'PULMICORT', 'ZENHALE', 'SYMBICORT', 
    'VANNAIR', 'RELVARE', 'COMBIVENT', 'VENTOLIN', 'STERIVENT', 'ATROVENT', 'ALUPENT', 'VINZA',
    'SPIRIVA', 'STRIVERDI', 'ONBRIZE', 'SEEBRI', 'EKLIRA', 'OSLIF', 'SPIOLTO', 'ULTIBRO', 'ANORO', 
    'DUAKLIR', 'ULUNAR', 'TRIMBOW', 'TRELEGY', 'MACRODANTINA', 'FURADANTINA', 'MICTASOL', 'FOSFOCIL',
    'VODELAN', 'NITROFURANT.GI', 'BACTRIM', 'SECOTEX', 'XATRAL-OD', 'AVODART', 'COMBODART', 'PROSCAR', 
    'ASOFLON', 'PROFIDOX', 'UPROSOL', 'TAMSULOSINA', 'SIFROL', 'AZILECT', 'NUBRENZA', 'STALEVO', 
    'SINEMET', 'SUNAM', 'CLOISONE', 'FLURINOL', 'AVIANT', 'XUZAL', 'ALLEGRA', 'VIRLIX', 'MOBICOX', 
    'VOLTAREN', 'EXEL', 'CELEBREX', 'MELOSTERAL', 'ARCOXIA', 'TRAYENTA', 'JANUVIA', 'ONGLYZA', 'GALVUS', 
    'FAZIQUE', 'INCRESINA', 'XILIARXS', 'JALRA', 'JANUMET', 'KOMBIGLYZE', 'VELMETIA', 
    'JARDIANZ', 'XIGDUO', 'INVOKANA', 'TRULICITY', 'OZEMPIC', 'CATAPRESAN', 'CARDURA', 'MICARDIS', 
    'EDARBI', 'LOSARTAN', 'ATACAND', 'ALMETEC', 'APROVEL', 'AVAPRO', 'COZAAR', 'DIOVAN', 'LEGIONIS', 
    'TELARTEQ', 'TRANSENDIS', 'AVALIDE', 'HYZAAR', 'COAPROVEL', 
    'LOSAR', 'OPENVAS', 'EXFORGE', 'APROVASC', 'BICARTIAL', 'DUOALMETEC', 'MAXOPRESS', 
    'PRADAXAR', 'XARELTO', 'ELICUIS', 'CLEXANE', 'COUMADIN', 'SINTROM', 'FRAXIPARINE'
]
key_medicines = [i.lower() for i in key_medicines]
today = datetime.today().strftime("%d/%m/%Y %H:%M:%S")
session = requests.Session()
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'es-419,es;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'origin': 'https://www.farmaciasanpablo.com.mx',
    'pragma': 'no-cache',
    'referer': 'https://www.farmaciasanpablo.com.mx/',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'x-anonymous-consents': '%5B%5D',
}

def print_e(msg):
    print(Fore.RED+ msg +Fore.RESET)


def print_w(msg):
    print(Fore.YELLOW+ msg +Fore.RESET)


def print_v(msg):
    print(Fore.GREEN+ msg +Fore.RESET)


def timing_val(func):
    def wrapper(*arg, **kw):
        t1 = time.time()
        func(*arg, **kw)
        t2 = time.time()
        segs = int(t2 - t1)
        if segs > 60:
            msg = f"tardó {segs/60} minutos..." 
        else:
            msg = f"tardó {segs} segs..." 
        print(msg)
        return segs
    return wrapper


def normalizar(text: str) -> str:
    """retorna la cadena del parametro sin acentos, en minuscula 
       y quita espacios al principio o fin de la cadena """
       
    a,b = 'áéíóúüÁÉÍÓÚÜ','aeiouuAEIOUU'
    trans = str.maketrans(a,b)
    try:
        text_normalized = text.translate(trans).lower().strip()
    except:
        print(f"error normalizando: {text}")
        text_normalized = "Error"
    return text_normalized


def get_concentracion_from_description(desc_comer) -> list:
   """ get the four characteristics from descripcion comercial( eg. 20 mg 20 tabletas)
    receives an import row from matched_imports.csv, tries to find the 
    presentation(concentration, concentration unit, presentation, farmacology form) 
    from the comercial description("descripcion_comercial") through differents forms
    with regular expressions.

    Returns
    -------
    list-like: 
         a list with concentration, concentration unit, presentation, farmacology form
         eg. 150 mg 20 tabletas which means: 150 milligrams 20 tablets
        
    explicacion extendida:
    ----------------------
        El import tiene una descripcion comercial como esta:
           # "ninlaro (ixazomib) caja colectiva con 3 cajas con una capsula de 3.5 mg (uso humano)"
        La sigueinte expresion regular encuentra la parte de la cadena que indica las 4 caracteristicas
        de su presentacion
           # \d+\.?\d*\s*mg\s*\d{1,3}\s*(tabletas|tab|capsulas|comprimidos|solucion oral|ge)
        En este caso devuelve esto: 3 cajas con una capsula de 3.5 mg 
        que se convierte en: 3 capsulas 3.5 mg
        Las regex descritas abajo se conforman básicamente de 4 partes que se alternan entre sí para
        resolver las multiples patrones encontrados en su descripcion comercial
        1) concentracion -> puede ser numero o flotante
           # regex:  \d+\.?\d*\s* numero entero o decimal seguido de 0,1 o más espacios
        2) unidad concentracion -> siempre mg por ahora 
           # mg
        3) presentacion
           # \d{1,3} número de capsulas, siempre es entero y debe existir minimo una vez y maximo 3
        4) forma farmacologica
            #(tabletas|tab|capsulas|comprimidos|solucion inyectable|solucion oral|ge) tiene que haber por 
            #lo menos una de estas formas
    """
   desc_comer = normalizar(desc_comer)
   #------------------------------4------------------------------#
   unidad_concentracion = '(mg|mcg|ml|gr)'
   cant_flot = '\d+\.?\d*\s*'
   cant_ent = '\d{1,3}'
   forma_farma = '(comprimidos|ampolletas|inyectable|suspension|tabletas|capsulas|solucion|jeringas|capsula|aerosol|parches|sobre|polvo|dosis|vial|tab|gel)'
   espacios = '\s*'
   any = '.{0,40}'
   # 'seretide diskus polvo 50mcg/500mcg, 60 dosis.'
   expresion_a = cant_flot+unidad_concentracion + "/" + cant_flot + unidad_concentracion + any + cant_ent + espacios + forma_farma
   expresion_b =  cant_flot + espacios + unidad_concentracion  + any + cant_ent + espacios + forma_farma
   expresion_c = cant_ent + espacios + forma_farma + any + cant_flot + unidad_concentracion
   expresion_d = forma_farma + any + cant_flot + espacios + unidad_concentracion
   expresion_e = cant_flot + espacios + unidad_concentracion  + any + forma_farma
   expresion_f = cant_ent + espacios + forma_farma
   expresion_g = cant_flot + espacios + unidad_concentracion

   if not isinstance(desc_comer, str):
       return ["", "",""]
   #----------------------------------------4--------------------------------------#
   #seretide diskus polvo 50mcg/500mcg, 60 dosis.' -4
   match = re.search(expresion_a, desc_comer)
   if match:
      info = match.group()

      regex = cant_flot+unidad_concentracion + "/" + cant_flot + unidad_concentracion
      peso = re.search(regex, info)
      peso = peso[0]

      regex = cant_ent + espacios + forma_farma
      cantidad_forma_farma = re.search(regex, info)
      cantidad = cantidad_forma_farma[0].split(" ")[0]
      forma_farmacologica = cantidad_forma_farma[0].split(" ")[1]
      
      return [peso, cantidad, forma_farmacologica]

   # 'clexane 80 mg solución inyectable, 2 jeringas con 0.8 ml c/u.' -4
   match = re.search(expresion_c, desc_comer)
   if match:
      info = match.group()
      regex = cant_flot + espacios + unidad_concentracion
      peso = re.search(regex, info)
      peso = peso[0]

      regex = cant_ent + espacios + forma_farma
      cantidad_forma_farma = re.search(regex, info)
      cantidad = cantidad_forma_farma[0].split(" ")[0]
      forma_farmacologica = cantidad_forma_farma[0].split(" ")[1]
      
      return [peso, cantidad, forma_farmacologica]
 
   # 'kitoscell lp 600 mg, 90 tabletas.' -4
   match = re.search(expresion_b, desc_comer)
   if match:
      info = match.group()
      regex = cant_flot + espacios + unidad_concentracion
      peso = re.search(regex, info)
      peso = peso[0]

      regex = cant_ent + espacios + forma_farma
      cantidad_forma_farma = re.search(regex, info)
      cantidad = cantidad_forma_farma[0].split(" ")[0]
      forma_farmacologica = cantidad_forma_farma[0].split(" ")[1]

      return [peso, cantidad, forma_farmacologica]

   # 'fosfocil 1 gr solución inyectable intravenosa, 1 pz.' -3 o -4
   match = re.search(expresion_e, desc_comer)
   if match:
      info = match.group()
      regex = cant_flot + espacios + unidad_concentracion 
      peso = re.search(regex, info)
      peso = peso[0]

      regex = forma_farma
      forma_farmacologica = re.search(regex, info)[0]

      cantidad = ''
      match = re.search("\d{1,3}\s*(pz|pzas|piezas)", desc_comer)
      if match:
         cantidad = re.search("\d{1,3}", info)[0] 
         
      return [peso, cantidad, forma_farmacologica]
 
   # 'kitoscell gel, 30 gr.' -3 
   match = re.search(expresion_d, desc_comer)
   if match:
      info = match.group()
      regex = cant_flot + espacios + unidad_concentracion
      peso = re.search(regex, info)
      peso = peso[0]

      regex = forma_farma
      forma_farmacologica = re.search(regex, info)[0]
      return [peso, "", forma_farmacologica]

   # 'allegra d tratamiento para la alergia y congestion nasal antihistaminico, 10 tabletas.' -2
   match = re.search(expresion_f, desc_comer)
   if match:
      info = match.group()
      regex = cant_ent + espacios + forma_farma
      cantidad_forma_farma = re.search(regex, info)
      cantidad = cantidad_forma_farma[0].split(" ")[0]
      forma_farmacologica = cantidad_forma_farma[0].split(" ")[1]
      return ["", cantidad, forma_farmacologica]
 
   #'atrovent 250mcg/ml, 20 ml.' -2
   match = re.search(expresion_g, desc_comer)
   if match:
      info = match.group()
      regex = cant_flot + espacios + unidad_concentracion
      peso = re.search(regex, info)
      peso = peso[0]
      return [peso, "", ""]
   
   return ["", "",""]


def clean_product_strings(medicine, descripcion, peso, presentacion, forma_farmacologica, 
                        marca, price, max_price, precio_descontado, descuento, promotion, 
                        today, detail_url):  
    """ Retorna un diccionario con la inf del producto. """
    medicine = medicine.strip().replace("\t","").replace("\n", "")
    descripcion = descripcion.strip().replace("\t","").replace("\n", "")
    marca = marca.strip().replace("\t","").replace("\n", "")
    price = price.strip().replace("\t","").replace("\n", "")
    precio_descontado = precio_descontado.strip().replace("\t","").replace("\n", "")
    max_price = max_price.strip().replace("\t","").replace("\n", "")
    promotion = promotion.strip().replace("\t","").replace("\n", "")

    product = {
        'medicamento': medicine,
        'descripcion': descripcion,
        'peso':peso, 
        'presentacion':presentacion,
        'forma_farmacologica':forma_farmacologica,
        'marca': marca,
        'price': price,
        'max_price': max_price,
        'precio descontado': precio_descontado,
        'descuento': descuento,
        'promotion': promotion,
        'fuente':'Farmacias San Pablo',
        'scrapping_day': today,
        'detail_url': detail_url,
    } 
    return product


@timing_val
def main():
    cant_words = len(key_medicines)
    print("---Empieza proceso de recolección ---")
    print(f"  {cant_words} medicinas para buscar")
    print("Obteniendo cookies")
    response = session.get('https://www.farmaciasanpablo.com.mx/', headers=headers)
    base_url = 'https://api.farmaciasanpablo.com.mx/rest/v2/fsp/products/search?fields=products(basePrice(FULL)%2CgtmProperties(FULL)%2CcategoryRestricted%2CadditionalDescription%2Cimages(FULL)%2CpotentialPromotions(FULL)%2CisApegoProduct%2Cprice(FULL)%2CapegoMechanic(FULL)%2Curl%2Ccategories(FULL)%2CfspMetaTitle%2CfspMetaDescription%2CfspMetaKeywords%2Ccode%2Cname%2Csummary%2Cconfigurable%2CconfiguratorType%2Cmultidimensional%2Cprice(FULL)%2Cimages(DEFAULT)%2Cstock(FULL)%2CaverageRating%2CvariantOptions)%2Cfacets%2Cbreadcrumbs%2Cpagination(DEFAULT)%2Csorts(DEFAULT)%2CfreeTextSearch%2CcurrentQuery&'
    #Itera las medicinas

    medicinas_sin_resultados = 0
    for medicine in key_medicines:
        time.sleep(random.randint(4, 8))
        print(f"\nObteniendo productos para {medicine}")

        try:
            productos = []
            for page in range(0, 3):
                med_url = f'query={medicine}&currentPage={page}&pageSize=36&lang=es_MX&curr=MXN'
                url = base_url + med_url
                response = session.get(url=url, headers=headers)
                resp = response.json()

                coincidences = resp['pagination']['totalResults']
                #total_pags = resp['pagination']['totalPages']
                products = resp['products']

                if page == 0:
                    print(f" Se encontraron {coincidences} coincidencias para {medicine}")

                if int(coincidences) == 0:
                    medicinas_sin_resultados += 1
                    break

                for prod in products:
                    aditional = prod['additionalDescription']
                    descripcion = prod['name'] + " " + aditional
                    marca = ""

                    apego_mec = prod.get('apegoMechanic')
                    promotion = apego_mec['mechanic'] if apego_mec else ""

                    detail_url = prod['url']

                    especial_promotion = prod['potentialPromotions']
                    esp_prom = especial_promotion[0].get('description')
                    if esp_prom:
                        promotion = esp_prom if not promotion else promotion + " --> " + esp_prom

                    price = prod['price']['value']
                    precio_descontado = prod['basePrice']['value']
                    if price != precio_descontado:
                        descuento = (precio_descontado*100)/price
                        descuento = round(abs(descuento-100), 2)
                        descuento = str(descuento) + "%"
                    else:
                        descuento = ''
                        precio_descontado =  ''

                    peso, presentacion, forma_farmacologica = get_concentracion_from_description(descripcion)

                    product = clean_product_strings(medicine, descripcion, peso, presentacion, forma_farmacologica, 
                                        marca, str(price), '', str(precio_descontado), descuento, promotion, 
                                        today, detail_url)
                    productos.append(product)

                cant_prods = len(productos)
                #Si hay más productos agregados en total que el número de resultados para la busqueda quiere decir que se acabó la páginación
                if cant_prods >=  coincidences or len(products) < 36:
                    print(f" Terminó la páginación, {cant_prods} productos extraidos de {coincidences} coincidencias")
                    break
                else:
                    #print(f"  {cant_prods} productos extraidos de la pág {page+1}")
                    time.sleep(random.randint(6,12))

            cant_prods_final = len(productos)
            if cant_prods_final >0:
                print_v(f"Agregando {cant_prods_final} productos a la base de datos")
                df = pd.DataFrame(productos)
                df.to_csv('precios.csv', index=False, header=False, encoding='utf-8', mode='a')
            else:
                print_w(f"  No se encontraron productos <---")

        except Exception as e:
            print_e(f"  Falló otención de {medicine},\n{e}")


    print(f"---Termino el proceso de raspado---")
    print(f"  {medicinas_sin_resultados} medicinas sin resultados de {cant_words}")


if __name__ == "__main__":
    print(datetime.today().strftime("%d/%m/%Y %H:%M:%S"))
    main()
    print(datetime.today().strftime("%d/%m/%Y %H:%M:%S"))