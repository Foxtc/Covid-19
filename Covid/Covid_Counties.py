import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors
import os
import glob
from PIL import Image
import natsort
from shapely.geometry.multipolygon import MultiPolygon
from pygifsicle import optimize
import imageio

# %% Load data

infected = pd.read_excel('~/InfetadosCovid.xlsx', parse_dates=['Data'],
                          sep='\t', encoding='utf-8')

# Load counties of Portugal and fips code
county_df = pd.read_csv('~/portugal_municipios.csv', sep=',',
                           encoding='utf-8')

file_geo = gpd.read_file('~/portugal_municipios.geojson')

file_geo_guimaraes = gpd.read_file('~/ContinenteConcelhos.geojson')

population = pd.read_excel('~/PORDATA_Média-anual.xlsx', sheet_name="Quadro",
                          sep='\t', encoding='utf-8')

# %% Fill empty cells
infected['Felgueiras'][3] = 24
infected['Funchal'][2] = 10
infected['Funchal'][3] = 10
infected['Santarém'][6] = 22
infected['Cartaxo'][8] = 9
infected['Câmara de Lobos'][2] = 3
infected['Câmara de Lobos'][3] = 3
infected['Lagoa'][2] = 3
infected['Lagoa'][5] = 3
infected['Lagoa'][6] = 3
infected['Lagoa'][11] = 3
infected['Ilha da Madeira'][4:33] = 20
infected['Amares'][3] = 6
infected['Castro Daire'][7] = 4
infected['Baião'][8] = 4
infected['Peniche'][7] = 3
infected['Ponte de Lima'][7:11] = 5
infected['Porto Santo'][7] = 3
infected['Sever do Vouga'][7:11] = 3
infected['Torres Novas'][5] = 3
infected['Torres Novas'][7:10] = 4
infected['Ilha de São Jorge'][4:33] = 7
infected['Cantanhede'][14] = 22
infected['Ilha Terceira'][4:33] = 6
infected['Ilha de São Miguel'][4:33] = 5
infected['Lagos'][3] = 4
infected['Lagos'][4] = 4
infected['Lagos'][7:12] = 3
infected['Ilha do Faial'][4:33] = 3
infected['Ilha do Pico'][4:33] = 3
infected['Almeida'][5] = 3
infected['Almeida'][7:16] = 6
infected['Torre de Moncorvo'][5] = 3
infected['Torre de Moncorvo'][7:12] = 3
infected['Caldas da Rainha'][7:16] = 8
infected['Ponta Delgada'][7:22] = 7
infected['Angra do Heroismo'][7:34] = 5
infected['Vila Nova de Foz Côa'][6] = 0
infected['Abrantes'][7:15] = 7
infected['Trancoso'][8:15] = 3
infected['Seia'][7:16] = 4
infected['Alcanena'][7:15] = 3
infected['Azambuja'][7:21] = 3
infected['Mortágua'][11:23] = 3
infected['Carregal do Sal'][11:14] = 3
infected['Figueiró dos Vinhos'][11:13] = 3
infected['Gouveia'][11:16] = 3
infected['Oliveira do Hospital'][14:16] = 3
infected['Portalegre'][17:21] = 3
infected['Bombarral'][17:20] = 3
infected['Guarda'][2:6] = 3
infected['Sintra'][2:4] = 43
infected['Castro Daire'][4] = 4
infected['Sines'][28:33] = 3
infected['Óbidos'][31:33] = 3
infected['Monchique'][33] = 3
infected['Santa Marta de Penaguião'][29:33] = 3

infected = infected.fillna(0)

infected.columns = infected.columns.str.rstrip()

infected = infected.rename({'Data': 'Date'}, axis=1)
# %% Transpose dataframe to add more counties later
transpose_infected = infected.set_index(['Date']).stack().reset_index()
transpose_infected = transpose_infected.rename({'level_1': 'Local', 0: 'NInfected'}, axis=1)

# Remove the extra space
transpose_infected['Local'] = transpose_infected['Local'].str.rstrip()

# %% Get only the the county name and fips
# Remove the island
county_df = county_df[county_df['name_1'] != 'Azores']
county_df = county_df[county_df['name_1'] != 'Madeira']

fips = county_df[['name_2', 'cartodb_id']]
fips = fips.rename({'name_2': 'Local'}, axis=1)

# %% Complete the counties
transpose_infected['Date'] = transpose_infected['Date'].dt.strftime('%m-%d')
transpose_infected['Date'] = transpose_infected['Date'].astype(str)

local_uniques = transpose_infected.groupby('Local').size().reset_index(name='Count')
check_local_notin_municipios = local_uniques[~(local_uniques['Local'].isin(fips['Local']))].reset_index()

fips_transpose_infected = fips.merge(transpose_infected, how='left')
to_add = fips_transpose_infected[fips_transpose_infected['Date'].isna()]
to_add = to_add.iloc[:, 0:2]
to_add = to_add.T

to_add.columns = to_add.iloc[0]
to_add = to_add.drop(to_add.index[0])

infected = infected.join(to_add)
infected = infected.fillna(0)

# %% Transpose the dataset
infected['Date'] = infected['Date'].dt.strftime('%Y-%m-%d')
inf_transp = infected.T
inf_transp.columns = inf_transp.iloc[0]
inf_transp = inf_transp.drop(inf_transp.index[0])
inf_transp = inf_transp.reset_index()
inf_transp = inf_transp.rename({'index': 'Local'}, axis=1)
inf_transp[inf_transp.columns[1:34]] = inf_transp[inf_transp.columns[1:34]].astype(int)

# %% Remove islands
# inf_transp = inf_transp[inf_transp['Local'] != 'Ponte de Sôr']
inf_transp = inf_transp[inf_transp['Local'] != 'Ponta do Sol']
inf_transp = inf_transp[inf_transp['Local'] != 'Funchal']
inf_transp = inf_transp[inf_transp['Local'] != 'Ilha da Madeira']
inf_transp = inf_transp[inf_transp['Local'] != 'Horta']
inf_transp = inf_transp[inf_transp['Local'] != 'Vila da Praia da Vitória']
inf_transp = inf_transp[inf_transp['Local'] != 'Madalena']
inf_transp = inf_transp[inf_transp['Local'] != 'Porto Santo']
inf_transp = inf_transp[inf_transp['Local'] != 'São Roque do Pico']
inf_transp = inf_transp[inf_transp['Local'] != 'Calheta']

# %% First visualization
file_geo.plot()
plt.show()

# %% Add Tavira e Guimarãess polygon to file_geo
tavira = file_geo_guimaraes[file_geo_guimaraes['Concelho'] == 'TAVIRA']
tavira['Concelho'] = 'Tavira'
tavira = pd.DataFrame(tavira)

guimaraes = file_geo_guimaraes[file_geo_guimaraes['Concelho'] == 'GUIMARÃES']
guimaraes['Concelho'] = 'Guimarães'
guimaraes = pd.DataFrame(guimaraes)

file_geo_ex = pd.DataFrame(file_geo)

file_geo_ex.loc[307] = ['None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', tavira['Concelho'][114], 'None',
                        'None', 'None', tavira['geometry'][114]]

file_geo_ex.loc[308] = ['None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', guimaraes['Concelho'][40],
                        'None', 'None', 'None', guimaraes['geometry'][40]]

file_geo_ex['geometry'][307] = MultiPolygon([file_geo_ex['geometry'][307]])
file_geo_ex['geometry'][308] = MultiPolygon([file_geo_ex['geometry'][308]])
local_geo = gpd.GeoDataFrame(file_geo_ex)


# %% Prepare geodata to the visualization
df_join = local_geo.merge(inf_transp, how='inner', left_on="name_2", right_on="Local")
df_join = df_join.iloc[:, 9:47]
df_join = df_join[df_join['name_1'] != 'Azores']
df_join = df_join[df_join['name_1'] != 'Madeira']
df_join = df_join.iloc[:, 3:]
df_join.head()
df = pd.DataFrame(df_join)

# %% Visualization of Portugal without the islands
values = '2020-04-24'

# set the value range for the choropleth
vmin, vmax = 1, 1350

fig = plt.figure(figsize=(30, 35))
ax = fig.add_subplot(111, frame_on=False)

cmap = plt.get_cmap('Blues')

# remove the axis
ax.axis('off')

# add a title
title = '{}'.format(values)
ax.set_title(title, fontdict={'fontsize': '65', 'fontweight': '10'})

# Create colorbar as a legend
sm = plt.cm.ScalarMappable(cmap='Blues', norm=plt.Normalize(vmin=vmin, vmax=vmax))
# add the colorbar to the figure
cbar = fig.colorbar(sm, aspect=30)
cbar.ax.tick_params(labelsize=35)
# create map
df_join.plot(column=values, cmap='Blues', linewidth=0.8, ax=ax, edgecolor='0.8',
             norm=matplotlib.colors.LogNorm())
plt.show()

# %% Save all maps of registered dates to create a gif
# get unique dates
days = list(df_join.columns[2:])

for day in days:
    vmin, vmax = 1, 1350

    fig = plt.figure(figsize=(30, 35))
    ax = fig.add_subplot(111, frame_on=False)

    cmap = plt.get_cmap('Blues')

    # remove the axis
    ax.axis('off')

    # add a title
    title = '{}'.format(day)
    ax.set_title(title, fontdict={'fontsize': '65', 'fontweight': '10'})

    # Create colorbar as a legend
    sm = plt.cm.ScalarMappable(cmap='Blues', norm=plt.Normalize(vmin=vmin, vmax=vmax))
    # add the colorbar to the figure
    cbar = fig.colorbar(sm, aspect=30)
    cbar.ax.tick_params(labelsize=35)
    # create map
    plot = df_join.plot(column=day, cmap='Blues', linewidth=0.8, ax=ax, edgecolor='0.8',
                        norm=matplotlib.colors.LogNorm())

    filepath = os.path.join('~/', day + '.png')
    chart = plot.get_figure()
    chart.savefig(filepath)

# %% Generate a gif
frames = []
imgs = glob.glob("~/*.png")

imgs = natsort.natsorted(imgs)

for i in imgs:
    new_frame = Image.open(i)
    frames.append(new_frame.copy())

images = list(map(lambda filename: imageio.imread(filename), imgs))

imageio.mimsave(os.path.join('~/mapa.gif'), images, fps=1)

optimize("~/mapa.gif")

# gifsicle -O3 old.gif -o new.gif


# %% Clean dataset - population of each county
population = population.iloc[10:364, 0:4]

population.columns = population.iloc[0]
population = population.drop(population.index[0])

population = population.rename({'Âmbito Geográfico': 'Geo', 'Anos': 'Local', 2018: "Population"}, axis=1)

del population[2001]

population = population[population['Geo'] == 'Município'].reset_index(drop=True)

del population['Geo']

# %% Add population numbers to covid numbers
import numpy as np
all_data = df_join.merge(population, how='left')

all_data.loc[(all_data['Local'] == 'Ponte de Sôr'), 'Population'] = 15189

all_data_df = pd.DataFrame(all_data)
all_data.to_file("~/data_covid.shp")