import pandas as pd

#CUIDADO ESTO ES PARA REFERENCIA, EJECUTAR ESTE SCRIPT PUEDE BORRAR ARCHIVOS YA CON INFORMACIÓN.
df = pd.DataFrame(columns=['medicamento', 'descripcion', 'peso', 'presentacion', 'forma_farmacologica', 
                           'marca', 'precio', 'max_price', 'precio descontado', 'descuento', 'promotion', 'fuente', 
                           'scrapping_day', 'detail_url'])

df.to_csv('precios.csv', index=False, encoding='utf-8', header=True)


