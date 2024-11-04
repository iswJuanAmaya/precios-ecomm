import requests
from lxml import html
from datetime import datetime
import re
import os
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
    'OPENVAS', 'EXFORGE', 'APROVASC', 'BICARTIAL', 'DUOALMETEC', 'MAXOPRESS', 
    'PRADAXAR', 'XARELTO', 'ELICUIS', 'CLEXANE', 'COUMADIN', 'SINTROM', 'FRAXIPARINE'
] 
key_medicines = [i.lower() for i in key_medicines]
#key_medicines = ["bloqueador", "papilla", "electrolito", "jugo", "loratadina", "sildenafil", "crema humectante", "labello", "tinte", "repelente", "laminitas", "galleta"]
today = datetime.today().strftime("%d/%m/%Y")
session = requests.Session()
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
    forma_farma = '(comprimidos|ampolletas|inyectable|suspension|tabletas|capsulas|solucion|jeringas|capsula|aerosol|parches|sobre|polvo|dosis|vial|caps|tabl|amp|tab|gel|ud)'
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
    expresion_h = cant_flot + espacios + "g" 

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
        peso = peso.replace(" ", "")
        return [peso, cantidad, forma_farmacologica]

    # 
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
        
        peso = peso.replace(" ", "")
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
        peso = peso.replace(" ", "")
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
        peso = peso.replace(" ", "")
        return [peso, "", ""]

    # Kitoscell Gel 10 g
    match = re.search(expresion_h, desc_comer)
    if match:
        peso = match.group()
        peso = peso.replace(" ", "")
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
        'fuente':'Farmacias Del Ahorro',
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
    session.get('https://www.fahorro.com/', headers=headers)
    
    promos_per_image = {
        "3_1_1.png": "Acumula 3 y llevate uno gratis",
        "3_x_1.png": "3 x 1",
        "2_x_75.png": "2 x 75",
        "2_1_2.png": "Acumula 2 y llevate uno gratis",
        "Group_1_4_.png": "Acumula 12 y llevate 4 gratis",
        "50_off.png": "50% de descuento",
        "25_off.png": "25% de descuento",
        "2x42.png": "2x42",
        "2x55.png": "2x55",
        "3x60.png": "3x60",
        "Label_70__1.png": "70% de descuento",
        "4_1_2.png": "Acumula 4 y llevate 1 gratis",
        "5_1_1.png": "Acumula 5 y llevate 1 gratis",
        "2da_al_50.png": "50% de descuento en la segunda pieza",
        "2_x_52_1.png": "2x52",
        "40_off.png": "40% de descuento",
        "15desc.png": "15% de desc",
        "Label_2X_35.png": "label",
        "2_x_25.png": "2x25",
        "Label_2X_34.png": "2x34",
        "Label_2X_36.png": "2x36",
        "20desc.png": "20% de desc",
        "Label_2x_30_2.png": "2x30",
        "30_off.png": "30% de desc",
        "3_x_50.png": "3x50",
        "6_2_1.png": "acumula 6 y llevate 2 gratis",
        "10_off.png":"10% de descuento"
    }
    relacion_promos = list(promos_per_image.keys())
    
    
    #Itera las medicinas
    medicinas_sin_resultados = 0
    for medicine in key_medicines:
        time.sleep(random.randint(4, 8))
        print(f"\nObteniendo productos para {medicine}")

        try:
            params = {
                'q': medicine,
                'product_list_limit': '90',
            }
            response = session.get('https://www.fahorro.com/catalogsearch/result/index/', params=params, headers=headers)
            html_source = html.fromstring(response.text)
            productos_tree =  html_source.xpath('//ol[contains(@class, "product-items")]/li')
            cant_prods = len(productos_tree)
            if cant_prods > 85:
                print_e("Más de 85")
            if cant_prods == 0:
                print_w("No se encotraron productos para esta medicina.")
                medicinas_sin_resultados += 1
                continue
            
            productos = []
            for prod_tree in productos_tree:
                descripcion = prod_tree.xpath('.//a[@class="product-item-link"]/text()')[0]
                marca = ''
                detail_url = prod_tree.xpath('.//a[@class="product-item-link"]/@href')[0] 

                #Busca imagen con promoción, 
                try:
                    image_url = prod_tree.xpath('.//div[contains(@style,"background:url")]/@style')[0].split("'")[1]
                    image_name = image_url.rsplit("/",1)[1]
                    if image_name in relacion_promos:
                        promotion = promos_per_image[image_name]
                    else:
                        print_e(f"Imagen {image_name} no ha sido agregada como promocion.")
                        imagenes = os.listdir('./images')
                        if image_name not in imagenes:
                            resp = session.get(image_url)
                            with open(f"./images/{image_name}", "wb") as img:
                                img.write(resp.content)
                            
                        
                except:
                    promotion = ""
                
                final_price = prod_tree.xpath('.//span[@data-price-type="finalPrice"]/span/text()')
                old_price = prod_tree.xpath('.//span[@data-price-type="oldPrice"]/span/text()')
                if old_price:
                    precio = old_price[0].replace("$", "").replace(",", "")
                    precio_descontado = final_price[0].replace("$", "").replace(",", "")
                    descuento = (float(precio_descontado)*100)/float(precio)
                    descuento = round(abs(descuento-100), 2)
                    descuento = str(descuento) + "%"
                else:
                    precio = final_price[0].replace("$", "").replace(",", "")
                    precio_descontado = ""
                    descuento = "" 
                
                peso, presentacion, forma_farmacologica = get_concentracion_from_description(descripcion)

                product = clean_product_strings(medicine, descripcion, peso, presentacion, forma_farmacologica, 
                                    marca, precio, '', precio_descontado, descuento, promotion, today, detail_url)
                productos.append(product)

            cant_prods_final = len(productos)
            if cant_prods_final >0:
                print_v(f"Agregando {cant_prods_final} productos a la base de datos")
                df = pd.DataFrame(productos)
                df.to_csv('precios.csv', index=False, header=False, encoding='utf-8', mode='a')
            else:
                print_w(f"No se encontraron productos <---")

        except Exception as e:
            print_e(f"  Falló otención de {medicine},\n{e}")


    print(f"---Termino el proceso de raspado---")
    print(f"  {medicinas_sin_resultados} medicinas sin resultados de {cant_words}")


if __name__ == "__main__":
    print(datetime.today().strftime("%d/%m/%Y %H:%M:%S"))
    main()
    print(datetime.today().strftime("%d/%m/%Y %H:%M:%S"))