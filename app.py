# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 17:40:44 2020

@author: DELL
"""

from flask import Flask, render_template
import pandas as pd
import numpy as np

positivos = 1000
negativos = 2000
defunciones = 20

#covid = pd.read_csv('http://187.191.75.115/gobmx/salud/datos_abiertos/datos_abiertos_covid19.zip', encoding="ISO-8859-1") #auto

##covid = pd.read_csv('https://github.com/Luisbaduy97/COVID-YUCATAN/blob/master/historical_db/200613COVID19MEXICO.csv?raw=true', encoding="ISO-8859-1") # manual

covid = pd.read_csv('historical_db/200618COVID19MEXICO.csv', encoding="ISO-8859-1") # manual


coords = pd.read_csv('coordinates/coordenadas.csv')
yuc_coords = coords[coords['Num_Ent'] == 31]

d = {n:m for n, m in zip(yuc_coords.Num_Mun, yuc_coords.Municipio)}
numb = [1,2,3]
diag = ['Positivo', 'Negativo', 'Por confirmar']
d2 = {n2:m2 for n2, m2 in zip(numb, diag)}


yucatan = covid[covid['ENTIDAD_RES'] == 31]



yuc2 = yucatan.groupby(by=['MUNICIPIO_RES'])['RESULTADO'].value_counts()

yuc2 = pd.Series(yuc2.values, index = yuc2.index).reset_index().rename(columns={0: 'SUMA'})

#yuc2['MUNICIPIO_RES'] = yuc2['MUNICIPIO_RES'].replace(999,50) #Los no especificado los pongo en Mérida

yuc2 = yuc2[yuc2['MUNICIPIO_RES'] != 999] #Quito a los no especificados

yuc2['MUNICIPIO'] = [d.get(m) for m in yuc2['MUNICIPIO_RES'].values.tolist()]
yuc2['RESULTADO2'] = [d2.get(m) for m in yuc2['RESULTADO'].values.tolist()]



muni = np.unique(yuc2['MUNICIPIO'])

pos = []
neg = []
conf = []
for i in muni:
    prov1 = yuc2[(yuc2['MUNICIPIO'] == i) & (yuc2['RESULTADO2'] == 'Positivo')]
    prov2 = yuc2[(yuc2['MUNICIPIO'] == i) & (yuc2['RESULTADO2'] == 'Negativo')]
    prov3 = yuc2[(yuc2['MUNICIPIO'] == i) & (yuc2['RESULTADO2'] == 'Por confirmar')]
    if len(prov1['SUMA'].values.tolist()) == 0:
        pos.append(0)
    else:
        pos.append(prov1['SUMA'].iloc[0])
    if len(prov2['SUMA'].values.tolist()) == 0:
        neg.append(0)
    else:
        neg.append(prov2['SUMA'].iloc[0])
    if len(prov3['SUMA'].values.tolist()) == 0:
        conf.append(0)
    else:
        conf.append(prov3['SUMA'].iloc[0])


lat = {v:t for v, t in zip(yuc_coords.Municipio, yuc_coords.lat)}
lon = {v:t for v, t in zip(yuc_coords.Municipio, yuc_coords.lon)}
lat_muni = [lat.get(v) for v in muni]
lon_muni = [lon.get(v) for v in muni]
#dataf =

data_f = pd.DataFrame()
data_f['Municipio'] = muni
data_f['Positivos'] = pos
data_f['Negativos'] = neg
data_f['Por confirmar'] = conf
data_f['Latitud'] = lat_muni
data_f['Longitud'] = lon_muni
data_f['Tamaño'] = np.asarray(pos) + 100


##margin={"r":200,"t":0,"l":200,"b":100}


# fig = px.scatter_mapbox(data_f, lat="Latitud", lon="Longitud", hover_name="Municipio",color='Positivos', color_continuous_scale=px.colors.diverging.Portland, zoom=7, height=500, size='Tamaño', hover_data=["Positivos", "Negativos", "Por confirmar"],center={'lat':lat.get('Mérida'), 'lon':lon.get('Mérida')})
# fig.update_layout(mapbox_style="open-street-map")
# #fig.update_layout(template = 'plotly_dark', title = 'Mapa de casos en Yucatán')
# fig.update_layout(template = 'plotly_dark')

sexo_dict = {1:'Mujer', 2:'Hombre', 3:'No especificado'}

cols = ['NEUMONIA', 'DIABETES', 'EPOC', 'INMUSUPR', 'ASMA', 'HIPERTENSION', 'CARDIOVASCULAR', 'OBESIDAD','RENAL_CRONICA', 'OTRA_COM', 'OTRO_CASO', 'SEXO', 'RESULTADO']
##yucatan[cols]
#yuc3 = yucatan[cols]
yuc3 = pd.DataFrame(data=yucatan[cols].values, columns =cols)
sex = [sexo_dict.get(v) for v in yuc3['SEXO'].values.tolist()]
yuc3['Gender'] = np.asarray(sex)


data3 = yuc3[yuc3['RESULTADO'] == 1]
neumonia = data3[data3['NEUMONIA'] == 1]
diabetes = data3[data3['DIABETES'] == 1]
epoc = data3[data3['EPOC'] == 1]
hiper = data3[data3['HIPERTENSION'] == 1]
ob = data3[data3['OBESIDAD'] == 1]
car = data3[data3['CARDIOVASCULAR'] == 1]
asma = data3[data3['ASMA'] == 1]
inmu = data3[data3['INMUSUPR'] == 1]



####################################
fi = yucatan[(yucatan['RESULTADO'] == 1) & (yucatan['FECHA_INGRESO'] != '9999-99-99')]
fi['SEX'] = [sexo_dict.get(v) for v in fi['SEXO'].values.tolist()]
fi2 = fi.groupby(['FECHA_INGRESO'])['RESULTADO'].value_counts()
fii = pd.Series(fi2.values, index = fi2.index).reset_index().rename(columns={0: 'SUMA'})
fii['ACUMULADO'] = fii['SUMA'].cumsum() #acumulado de casos positivos


#acumalo de casos negativos
ni = yucatan[(yucatan['RESULTADO'] == 2) & (yucatan['FECHA_INGRESO'] != '9999-99-99')]
ni['SEX'] = [sexo_dict.get(v) for v in ni['SEXO'].values.tolist()]
ni2 = ni.groupby(['FECHA_INGRESO'])['RESULTADO'].value_counts()
nii = pd.Series(ni2.values, index = ni2.index).reset_index().rename(columns={0: 'SUMA'})
nii['ACUMULADO'] = nii['SUMA'].cumsum() #acumulado de casos negativos


muertos = fi[fi['FECHA_DEF'] != '9999-99-99'].shape[0]
sospechosos = data_f['Por confirmar'].sum()
acu_datos_pos = fii['ACUMULADO'].values.tolist()
acu_fechas_pos = fii['FECHA_INGRESO'].values.tolist()
acu_datos_neg = nii['ACUMULADO'].values.tolist()
acu_fechas_neg = nii['FECHA_INGRESO'].values.tolist()
#######################################
data_positivos = pd.DataFrame()
data_positivos['Positivos'] = acu_datos_pos
data_positivos['Fecha_positivos'] = acu_fechas_pos
data_negativos = pd.DataFrame()
data_negativos['Negativos'] = acu_datos_neg
data_negativos['Fecha_negativos'] = acu_fechas_neg


fecha_final = data_positivos['Fecha_positivos'].values.tolist()[-1]
date = np.array(fecha_final, dtype=np.datetime64)
date_p = date - np.arange(data_negativos.shape[0])
date_p = np.flip(date_p)
fechas = pd.DataFrame()
fechas['Fecha'] = date_p
fecha = fechas['Fecha'].dt.strftime("%Y-%m-%d").values.tolist()
del fechas

posi = []
negs = []

plot_pos = pd.DataFrame()
plot_pos['Positivos'] = np.flip(data_positivos['Positivos'].values)
plot_neg = pd.DataFrame()
plot_neg['Negativos'] = np.flip(data_negativos['Negativos'].values)
plot_neg['Fecha'] = np.flip(np.asarray(fecha))
plotting = pd.DataFrame()
plotting = pd.concat([plot_pos,plot_neg], ignore_index=True, axis=1)
plotting.columns = ['Positivos', 'Negativos', 'Fecha']
plotting = plotting.fillna(0)
plotting = plotting.sort_values(by = 'Fecha')

muni = data_f['Municipio'].values.tolist()
posi = data_f['Positivos'].values.tolist()
neg = data_f['Negativos'].values.tolist()
conf = data_f['Por confirmar'].values.tolist()
lat = data_f['Latitud'].values.tolist()
long = data_f['Longitud'].values.tolist()
tam = data_f['Tamaño'].values.tolist()

 
# creates a Flask application, named app
app = Flask(__name__)

# a route where we will display a welcome message via an HTML template
@app.route("/")
def hello():
    message = {
    'positivos': {'positivo_total':fii['ACUMULADO'].values.tolist()[-1],
                  'positivo_array':plotting['Positivos'].values.tolist()},
    'negativos':{'negativo_total' : nii['ACUMULADO'].values.tolist()[-1],
                 'negativo_array':plotting['Negativos'].values.tolist()},
    'fechas': plotting['Fecha'].values.tolist(),
    'defunciones':muertos,
    'confirmar':sospechosos,
    'muni':muni,
    'posi': posi,
    'neg': neg,
    'conf': conf,
    'lat': lat,
    'lon': long,
    'tam': tam}
    
    return render_template('index.html', message=message)

# run the application
#if __name__ == "__main__":
#    app.run(debug=True)

if __name__ == "__main__":
    app.run()


## gunicorn
#app = app.server

