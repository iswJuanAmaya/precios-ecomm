import requests
from lxml import html
from datetime import datetime
import re
import time
import random
import pandas as pd
from colorama import Fore
import os 

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
    'PRADAXAR', 'PRADAXAR,', 'XARELTO', 'ELICUIS', 'CLEXANE', 'COUMADIN', 'SINTROM', 'FRAXIPARINE'
]
key_medicines = [i.lower() for i in key_medicines]
today = datetime.today().strftime("%d/%m/%Y")
session = requests.Session()
if os.name != 'nt':
    print("Como no está en windows se inicializa proxy")
    proxies = {
        'http': 'http://sp072m4oql:bSx81k=m4Gony4PoNb@mx.smartproxy.com:20004',
        'https': 'https://sp072m4oql:bSx81k=m4Gony4PoNb@mx.smartproxy.com:20002',
    }
    session.proxies.update(proxies)

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'es-419,es;q=0.9',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}


def timing_val(func):
    def wrapper(*arg, **kw):
        t1 = time.time()
        func(*arg, **kw)
        t2 = time.time()
        segs = int(t2 - t1)
        print(f"tardó {segs} segs...")
        return segs
    return wrapper


def print_e(msg):
    print(Fore.RED+ msg +Fore.RESET)


def print_w(msg):
    print(Fore.YELLOW+ msg +Fore.RESET)


def print_v(msg):
    print(Fore.GREEN+ msg +Fore.RESET)


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
                          marca, price, max_price, promotion, today, detail_url):
    
    medicine = medicine.strip().replace("\t","").replace("\n", "")
    descripcion = descripcion.strip().replace("\t","").replace("\n", "")
    marca = marca.strip().replace("\t","").replace("\n", "")
    price = price.strip().replace("\t","").replace("\n", "")
    max_price = max_price.strip().replace("\t","").replace("\n", "")
    promotion = promotion.strip().replace("\t","").replace("\n", "")
    return  {
        'medicamento': medicine,
        'descripcion': descripcion,
        'peso':peso, 
        'presentacion':presentacion,
        'forma_farmacologica':forma_farmacologica,
        'marca': marca,
        'price': price,
        'max_price': max_price,
        'precio descontado': '',
        'descuento': '',
        'promotion': promotion,
        'fuente':'Farmacias Guadalajara',
        'scrapping_day': today,
        'detail_url': detail_url,
    } 


@timing_val
def main():
    cant_words = len(key_medicines)
    print("---Empieza proceso de recolección ---")
    print(f"  {cant_words} medicinas para buscar")

    print("Obteniendo cookies")
    response = session.get('https://www.farmaciasguadalajara.com/', headers=headers)

    #Itera las medicinas
    medicinas_sin_resultados = 0
    for medicine in key_medicines:
        productos = []
        time.sleep(random.randint(4, 8))
        print(f"\nObteniendo productos para {medicine}")

        #Obtiene número de coincidencias.
        params = {
            'categoryId': '',
            'storeId': '10151',
            'searchType': '1001',
            'catalogId': '10052',
            'langId': '-24',
            'sType': 'SimpleSearch',
            'resultCatEntryType': '2',
            'showResultsPage': 'true',
            'searchSource': 'Q',
            'pageView': '',
            'beginIndex': '0',
            'pageSize': '20',
            'searchTerm': medicine,
        }
        headers['referer'] = 'https://www.farmaciasguadalajara.com/'
        try:
            response = session.get('https://www.farmaciasguadalajara.com/SearchDisplay', 
                            params=params, headers=headers)
        except Exception as e:
            print_e("Falló en requests principal para obtener el número de resultados")
            medicinas_sin_resultados += 1
            continue
        

        html_source = html.fromstring(response.text)
        #Busca el número de coincidencias(productos encontrados) dada la busqueda de la medicina
        try:
            coincidences = int(html_source.xpath('.//span[contains(@id,"searchTotalCount")]/text()')[0].split(" ")[0])
        except:
            #Sí no encuentra coincidencias puede deberse a que cuando hay un solo resultado en lugar
            #de mandarte a la página de resultados te manda a la página del producto
            try:
                print("no se encontraron coincidencias, se busca redirección de producto unico.")
                # el resultado de la respuesta es un html con una funcion de redirección.
                #se extrae la url de dicha redirección y se visita 
                redirect_text = html_source.xpath('//script[contains(text(),"Redirect")]/text()')[0]
                redirect_url = redirect_text.split('Redirect(')[1].split('"')[3]
                if "www.farmaciasguadalajara.com" not in redirect_url:
                    print_w("ERROR No se encontró un redirect de producto unico")
                    medicinas_sin_resultados += 1
                    continue 
                resp = session.get(redirect_url, headers=headers, timeout=20)
                html_source = html.fromstring(resp.text)
                detail_url = redirect_url
                descripcion = html_source.xpath('//div[contains(@id,"productFull")]//h1[@id="fgProductName"]/text()')[0]
                price = html_source.xpath('//div[contains(@id,"productFull")]//span[contains(@id,"offerPrice")]/text()')[0]
                marca = ''
                promotion = ''
                try:
                    max_price = html_source.xpath('//div[contains(@id,"productFull")]//span[contains(@id,"listPrice")]/text()')[0]
                except:
                    max_price = ""
                peso, presentacion, forma_farmacologica = get_concentracion_from_description(descripcion)
                product = clean_product_strings(medicine, descripcion, peso, presentacion, forma_farmacologica, 
                                                marca, price, max_price, promotion, today, detail_url)
                
                productos.append(product)
                coincidences = 1
            except:
                print_e("ERROR No se encontraron coincidencias ni redirecciones")
                medicinas_sin_resultados += 1
                continue

        print(f" Se encontraron {coincidences} coincidencias para {medicine}")
        if coincidences == 0:
            print_w("No se encotraron productos para esta medicina.")
            medicinas_sin_resultados += 1
            continue

        #Actualizo hedaers para /ProductListingView?
        headers['x-requested-with'] = 'XMLHttpRequest'
        headers['referer'] = 'https://www.farmaciasguadalajara.com/SearchDisplay'
        for i in range(0,351, 50):
            print("  Extrayendo productos...")

            #Comrpobación para prueba
            cant_prods = len(productos)
            if cant_prods == 1:
                break
            
            try:
                # Trae lista de productos
                begin_index = cant_prods
                product_begin_index = cant_prods 
                url = f'https://www.farmaciasguadalajara.com/ProductListingView?top_category2=&top_category3=&facet=&searchTermScope=&top_category4=&top_category5=&searchType=&filterFacet=&resultCatEntryType=2&sType=SimpleSearch&top_category=&gridPosition=&ddkey=ProductListingView&metaData=&ajaxStoreImageDir=%2Fwcsstore%2FFGSAS%2F&advancedSearch=&categoryId=&categoryFacetHierarchyPath=&searchTerm={medicine}&emsName=&filterTerm=&manufacturer=&resultsPerPage=80&disableProductCompare=ture&parent_category_rn=&catalogId=10052&langId=-24&enableSKUListView=false&storeId=10151&contentBeginIndex=0&beginIndex={begin_index}&productBeginIndex={product_begin_index}&orderBy=&pageSize=80&x_pageType=[Ljava.lang.String;@b32cc07a&x_noDropdown=true'
                response = session.get(url=url, headers=headers,)

                #Extrae producto y lo agrega a la lista
                html_source = html.fromstring(response.text)
                elements = html_source.xpath('//div[@class="product"]')
                for element in elements:
                    detail_url = element.xpath('.//div[@class="product_info"]/div/a/@href')[0].strip()
                    descripcion = element.xpath('.//div[@class="product_info"]/div/a/text()')[1].strip().lower()
                    marca = element.xpath('.//div[@class="product_info"]/div/a/b/text()')[0].strip().lower()
                    price = element.xpath('.//div[@class="product_info"]//span[contains(@id,"offerPrice")]/text()')[0].strip()
                    try:
                        max_price = element.xpath('.//div[@class="product_info"]//span[contains(@id,"listPrice")]/text()')[0].strip()
                    except:
                        max_price = ""
                    try:
                        promotion = element.xpath('.//div[contains(@class,"plp-promotion")]/span/text()')[0].strip()
                    except:
                        promotion = ""
                    
                    peso, presentacion, forma_farmacologica = get_concentracion_from_description(descripcion)
                    product = clean_product_strings(medicine, descripcion, peso, presentacion, forma_farmacologica, 
                                                    marca, price, max_price, promotion, today, detail_url)
                    productos.append(product)
                
                cant_prods = len(productos)

                #Si hay más productos agregados en total que el número de resultados para la busqueda quiere decir que se acabó la páginación
                if cant_prods >=  coincidences or len(elements) < 50:
                    print(f" Terminó la páginación, {cant_prods} productos extraidos de {coincidences} coincidencias")
                    break
                else:
                    print(f"  {cant_prods} productos extraidos")
                    time.sleep(random.randint(6,12))

            except Exception as e:
                print_e(f"  Falló\n{e}")

        cant_prods_final = len(productos)
        if cant_prods_final >0:
            print_v(f"Agregando {cant_prods_final} productos a la base de datos")
            df = pd.DataFrame(productos)
            df.to_csv('precios.csv', index=False, header=False, encoding='utf-8', mode='a')
        else:
            print_e(f"No se encontraron productos <---")

    print(f"---Termino el proceso de raspado---")
    print(f"  {medicinas_sin_resultados} medicinas sin resultados de {cant_words}")


if __name__ == "__main__":
    print(datetime.today().strftime("%d/%m/%Y %H:%M:%S"))
    main()
    print(datetime.today().strftime("%d/%m/%Y %H:%M:%S"))