Readme
  scraper que extrae información de farmacias guadalajara

@Funcionamiento 
  Entra a la página de farmacia guadalajara y dada una lista de palabras busca una por una coincidencias, 
  cada coincidencia la extrae y la guarda en el csv precios.csv

@dependencias
  requests==2.31.0
  pandas==2.1.3
  lxml==4.9.3

@Files: 
  farmacias_guadalajara.py --> Scraper de farmacias guadalajara.
  layout_csvs.py --> crea la bdd precios en la raiz del proyecto.
  precios.csv --> bdd final
