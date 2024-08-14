import re

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


pruebas = [
    'kitoscell gel, 30 gr.', #4
    'kitoscell lp 600 mg, 90 tabletas.',# 2
    'pulmicort turbuhaler 100 mcg polvo para inhalación, 200 dosis.',# 2
    'seretide diskus polvo 50mcg/500mcg, 60 dosis.',# 1
    'fosfocil 250mg/5ml suspension, 60 ml.',# ???
    'pulmicort 0.125mg/ml suspension para nebulización 5 ampolletas, 2 ml c/u.',# 3
    'fosfocil solución infantil inyectable, 0.5 gr.',#4
    'fosfocil gu 3 gr, 1 sobre adulto granulado.',# ?
    'fosfocil 1 gr solución inyectable intravenosa, 1 pz.',
    'bactrim 200mg/40mg/5ml, suspensión 100 ml.',# ?
    'bactrim f 800mg/160mg, 15 tabletas.',# 1
    'clexane 80 mg solución inyectable, 2 jeringas con 0.8 ml c/u.',# 2  
    'virlix 1mg/ml solucion infantil, 60 ml.',
    'trulicity 0.75mg/0.5ml solucion inyectable 2 plumas precargadas.',#???
    'trulicity 1.5mg/0.5ml solucion inyectable pluma precargada, 2 pzas de dosis unica c/u.',#???
    'vannair 80mcg/4.5mcg, aerosol bucal dispositivo inhalador con 120 dosis.',#??
    'atrovent suspension aerosol, 10 ml (11.22gr).',
    'fosfocil gu 3 gr, 1 sobre adulto granulado.',#??
    'nubrenza 4mg/24h con 14 parches.',#?
    'voltaren 24h 15 mg, 5 parches.',
    'atrovent 250mcg/ml, 20 ml.',#?
    'allegra d tratamiento para la alergia y congestion nasal antihistaminico, 10 tabletas.'
]
# ? DOSIS, 

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


print(
    expresion_a,"\n",
    expresion_b,"\n",
    expresion_c,"\n",
    expresion_d,"\n",
    expresion_e,"\n",
    expresion_f,"\n",
    expresion_g,"\n",
    "\n"
    )

for desc_comer in pruebas:
    desc_comer = normalizar(desc_comer)

    #seretide diskus polvo 50mcg/500mcg, 60 dosis.' -4
    match = re.search(expresion_a, desc_comer)
    if match:
        info = match.group()
        print("tipo 1 ",info)

        regex = cant_flot+unidad_concentracion + "/" + cant_flot + unidad_concentracion
        peso = re.search(regex, info)
        peso = peso[0]
        #print(peso)

        regex = cant_ent + espacios + forma_farma
        cantidad_forma_farma = re.search(regex, info)
        cantidad = cantidad_forma_farma[0].split(" ")[0]
        forma_farmacologica = cantidad_forma_farma[0].split(" ")[1]
        #print(cantidad)
        #print(forma_farmacologica)
        print("\n")
        continue

    # 'clexane 80 mg solución inyectable, 2 jeringas con 0.8 ml c/u.' -4
    match = re.search(expresion_c, desc_comer)
    if match:
        info = match.group()
        print("tipo 3 ",info)
        regex = cant_flot + espacios + unidad_concentracion
        peso = re.search(regex, info)
        peso = peso[0]
        #print(peso)

        regex = cant_ent + espacios + forma_farma
        cantidad_forma_farma = re.search(regex, info)
        cantidad = cantidad_forma_farma[0].split(" ")[0]
        forma_farmacologica = cantidad_forma_farma[0].split(" ")[1]
        #print(cantidad)
        #print(forma_farmacologica)

        print("\n")
        continue
    
    # 'kitoscell lp 600 mg, 90 tabletas.' -4
    match = re.search(expresion_b, desc_comer)
    if match:
        info = match.group()
        print("tipo 2 ",info)
        regex = cant_flot + espacios + unidad_concentracion
        peso = re.search(regex, info)
        peso = peso[0]
        #print(peso)

        regex = cant_ent + espacios + forma_farma
        cantidad_forma_farma = re.search(regex, info)
        cantidad = cantidad_forma_farma[0].split(" ")[0]
        forma_farmacologica = cantidad_forma_farma[0].split(" ")[1]
        #print(cantidad)
        #print(forma_farmacologica)

        print("\n")
        continue

    # 'fosfocil 1 gr solución inyectable intravenosa, 1 pz.' -3 o -4
    match = re.search(expresion_e, desc_comer)
    if match:
        info = match.group()
        print("tipo 5 ",info)
        regex = cant_flot + espacios + unidad_concentracion 
        peso = re.search(regex, info)
        peso = peso[0]
        #print(peso)

        regex = forma_farma
        forma_farmacologica = re.search(regex, info).group()
        #print(forma_farmacologica)

        match = re.search("\d{1,3}\s*(pz|pzas|piezas)", desc_comer)
        if match:
            pzas = re.search("\d{1,3}", info)[0]
            #print(pzas)

        print("\n")
        continue
    
    # 'kitoscell gel, 30 gr.' -3 
    match = re.search(expresion_d, desc_comer)
    if match:
        info = match.group()
        print("tipo 4 ",info)
        regex = cant_flot + espacios + unidad_concentracion
        peso = re.search(regex, info)
        peso = peso[0]
        #print(peso)

        regex = forma_farma
        forma_farmacologica = re.search(regex, info)[0]
        #print(forma_farmacologica)

        print("\n")
        continue
    
    # 'allegra d tratamiento para la alergia y congestion nasal antihistaminico, 10 tabletas.' -2
    match = re.search(expresion_f, desc_comer)
    if match:
        info = match.group()
        print("tipo 6 ", info)
        regex = cant_ent + espacios + forma_farma
        cantidad_forma_farma = re.search(regex, info)
        cantidad = cantidad_forma_farma[0].split(" ")[0]
        forma_farmacologica = cantidad_forma_farma[0].split(" ")[1]
        print(cantidad)
        print(forma_farmacologica)

        print("\n")
        continue
    
    #'atrovent 250mcg/ml, 20 ml.' -2
    match = re.search(expresion_g, desc_comer)
    if match:
        info = match.group()
        print("tipo 7 ",info)
        regex = cant_flot + espacios + unidad_concentracion
        peso = re.search(regex, info)
        peso = peso[0]
        print(peso)

        print("\n")
        continue

    print("->",desc_comer,"\n")
