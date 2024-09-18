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
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'es-419,es;q=0.9,es-MX;q=0.8,en;q=0.7',
    # 'cookie': 'wp_ga4_customerGroup=NOT%20LOGGED%20IN; visid_incap_3088875=vDdi9bLOSqqwH5HOfCfcdlUG1mYAAAAAQUIPAAAAAABk8ChxiS77l/7j6CWmv6Rl; _omappvp=oBt5iHxht7qqQ5RdxcKEdyscvJhNQXt6WGHh2XVyscubbnisjl4lZluThnv6RvgpQYOu90AEBgoW1YMyjE4UoKYZlLG8IfF7; _gcl_au=1.1.656740851.1725302361; _ga=GA1.1.1227093177.1725302362; __spdt=8dd31c0d3c814f558b8c7c6ed3f177fe; STVID=594b93f7-537b-5b71-8052-ee56a804e65c; FPID=FPID2.3.OP0UkpQtq%2Bnmq7fmaaf0k7QI8irz8qL5%2F1%2FyLOXqXI0%3D.1725302362; FPAU=1.1.656740851.1725302361; _gtmeec=e30%3D; _fbp=fb.2.1725302362776.2006348840; PHPSESSID=a10c320bb123af7829842368e6914ce3; incap_ses_1682_3088875=b0K0duFpnyvYUGLnO6pXF86X52YAAAAAMJLu5xxAbBA4VgdjF5ikAg==; STUID=0b79bfcd-2c24-41a5-1737-24e5538092e8; form_key=ZRjCc5HqiQSfHZzB; mage-cache-storage={}; mage-cache-storage-section-invalidation={}; mage-cache-sessid=true; mage-messages=; recently_viewed_product={}; recently_viewed_product_previous={}; recently_compared_product={}; recently_compared_product_previous={}; product_data_storage={}; _clck=yicrgb%7C2%7Cfp8%7C0%7C1706; form_key=ZRjCc5HqiQSfHZzB; FPLC=sCr3jLlGPE0INRfKPQjGKRfbzuJkAoUPvMhJNkCYsZGXRZSM9ArnZRxdG08x1DrUBKEF%2BGoUHVbhul3Lbv9vI2o1ZZapp9i%2Fo%2BjVr7tnr0T7oA50famn%2FkbzHu3t2A%3D%3D; code_region=00006; _gcl_aw=GCL.1726453917.Cj0KCQjwi5q3BhCiARIsAJCfuZmENn0g1TYJNX4WbZu6Lj_3jkIZ27f7CFnGNpH4euU_K-J4zsOqLzcaAgvPEALw_wcB; FPGCLAW=GCL.1726453713.Cj0KCQjwi5q3BhCiARIsAJCfuZmENn0g1TYJNX4WbZu6Lj_3jkIZ27f7CFnGNpH4euU_K-J4zsOqLzcaAgvPEALw_wcB; nlbi_3088875=rvz5IezPTAhkZCoCfLK+9AAAAACn/kxvtVzIjVPDntjAXkOk; _ga_3YYMLE3C79=GS1.1.1726453712.5.1.1726454130.0.0.668148385; _clsk=c04e37%7C1726454130709%7C4%7C1%7Cq.clarity.ms%2Fcollect; private_content_version=e1a39ad549a3a23a72d1223b3cc5c279; cityregion=Monterrey; stateregion=Nuevo%20Le%F3n; FPGSID=1.1726453713.1726454132.G-3YYMLE3C79.6dgZzT6jgFqIP5CINWLGzg; section_data_ids={%22geolocation%22:1726454130%2C%22apptrian_facebook_pixel_matching_section%22:1726454131}',
    'referer': 'https://www.benavides.com.mx/1048340-100mg-600mg-loratadina-ambroxol',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
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
        'fuente':'Farmacias Benavides',
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
    response = session.get('https://www.benavides.com.mx/', headers=headers)
    

    #Itera las medicinas
    medicinas_sin_resultados = 0
    for medicine in key_medicines:
        time.sleep(random.randint(4, 8))
        print(f"\nObteniendo productos para {medicine}")

        try:
            url_next_page = ""
            productos = []
            for page in range(1, 4):
                if not url_next_page:
                    params = {
                        'q': medicine,
                    }
                    response = session.get('https://www.benavides.com.mx/catalogsearch/result/', params=params, headers=headers)
                else:
                    print(f"  Cambiando a pagina {page}")
                    response = session.get(url_next_page, headers=headers)

                x = html.fromstring(response.text)

                sr = x.xpath("//*[contains(text(), 'No se encontraron resultados exactos para:')]")
                srt = x.xpath("//*[contains(text(), 'No encontramos ningún resultado')]")
                if sr or srt:
                    medicinas_sin_resultados += 1
                    break

                coincidences = x.xpath('//p[@id="toolbar-amount"]/span[3]/text()')
                if not coincidences:
                    coincidences = x.xpath('//p[@id="toolbar-amount"]/span/text()')              
                if coincidences:
                    coincidences = coincidences[0]
                else:
                    if x.xpath("//div[@class='product-info-main']"):
                        print("  se encontró un único producto que coincide con la búsqueda")
                    else:
                        raise Exception("No se encontró el número de coincidencias dentro de la respuesta")

                    prom = x.xpath('//span[@name="card_promotions"]/label/text()')
                    promotion = prom[0] if len(prom)>0 else ""
                    marca = x.xpath('//span[@class="principal-title"]/text()')[0].strip()
                    desc_1 = x.xpath('//h1[@class="product-name"]/text()')[0].strip()
                    desc_2 = x.xpath('//span[@class="product-presentation"]/text()')[0].strip()
                    descripcion = desc_1 + " " + desc_2
                    detail_url = response.url
                    price_final = x.xpath('.//span[contains(@class,"price-final_price")]/span/text()')
                    if price_final:
                        price = price_final[0].replace("$", "").replace(",", "")
                        precio_descontado = ""
                        descuento = ""
                    else:
                        price = prod_elem.xpath('.//span[@data-price-type="oldPrice"]/span/text()')[0].replace("$", "").replace(",", "")
                        precio_descontado = prod_elem.xpath('.//span[contains(@class,"special-price")]/span/text()')[0].replace("$", "").replace(",", "")
                        descuento = (float(precio_descontado)*100)/float(price)
                        descuento = round(abs(descuento-100), 2)
                        descuento = str(descuento) + "%"

                    peso, presentacion, forma_farmacologica = get_concentracion_from_description(descripcion)

                    product = clean_product_strings(medicine, descripcion, peso, presentacion, forma_farmacologica, 
                                        marca, str(price), '', str(precio_descontado), descuento, promotion, 
                                        today, detail_url)
                    productos.append(product)

                    break

                if int(coincidences) == 0:
                    medicinas_sin_resultados += 1
                    break
                if page == 1:
                    print(f" Se encontraron {coincidences} coincidencias para {medicine}")
                
                products_elements = x.xpath('//ol[contains(@class,"product-items")]/li')
                for prod_elem in products_elements:
                    prom = prod_elem.xpath('.//div[@class="promotion"]/span/text()')
                    promotion = prom[0] if len(prom)>0 else ""
                    marca = prod_elem.xpath('.//div[@class="product-item-brand"]/text()')[0].strip()
                    desc_1 = prod_elem.xpath('.//div[@class="product-item-presentation"]/text()')[0].strip()
                    desc_2 = prod_elem.xpath('.//a[@class="product-item-link"]/text()')[0].strip()
                    detail_url = prod_elem.xpath('.//a[@class="product-item-link"]/@href')[0].strip()
                    descripcion = desc_1 + " " + desc_2
                    price_final = prod_elem.xpath('.//span[contains(@class,"price-final_price")]/span/text()')
                    if price_final:
                        price = price_final[0].replace("$", "").replace(",", "")
                        precio_descontado = ""
                        descuento = ""
                    else:
                        price = prod_elem.xpath('.//span[@data-price-type="oldPrice"]/span/text()')[0].replace("$", "").replace(",", "")
                        precio_descontado = prod_elem.xpath('.//span[contains(@class,"special-price")]/span/text()')[0].replace("$", "").replace(",", "")
                        descuento = (float(precio_descontado)*100)/float(price)
                        descuento = round(abs(descuento-100), 2)
                        descuento = str(descuento) + "%"

                    peso, presentacion, forma_farmacologica = get_concentracion_from_description(descripcion)

                    product = clean_product_strings(medicine, descripcion, peso, presentacion, forma_farmacologica, 
                                        marca, str(price), '', str(precio_descontado), descuento, promotion, 
                                        today, detail_url)
                    productos.append(product)

                cant_prods = len(productos)
                next_page_btn = x.xpath('//a[@class="action  next" and @title="Siguiente"]/@href')
                if next_page_btn:
                    #print(f"  {cant_prods} productos extraidos de la pág {page}")
                    url_next_page = next_page_btn[0]
                    time.sleep(random.randint(9,17))
                else:
                    print(f" Terminó la páginación, {cant_prods} productos extraidos de {coincidences} coincidencias")
                    break


            cant_prods_final = len(productos)
            if cant_prods_final >0:
                print_v(f"Agregando {cant_prods_final} productos a la base de datos")
                df = pd.DataFrame(productos)
                df.to_csv('precios.csv', index=False, header=False, encoding='utf-8', mode='a')
            else:
                print_w(f"  No se encontraron productos <---")

        except Exception as e:
            print_e(f"  Falló otención de {medicine},\n   {e}")


    print(f"---Termino el proceso de raspado---")
    print(f"  {medicinas_sin_resultados} medicinas sin resultados de {cant_words}")


if __name__ == "__main__":
    print(datetime.today().strftime("%d/%m/%Y %H:%M:%S"))
    main()
    print(datetime.today().strftime("%d/%m/%Y %H:%M:%S"))