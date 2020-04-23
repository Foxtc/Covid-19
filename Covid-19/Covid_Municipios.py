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
infetados = pd.read_excel('InfetadosCovid.xlsx', parse_dates=['Data'],
                          sep='\t', encoding='utf-8')

# Load counties of Portugal and fips code
municipio_df = pd.read_csv('portugal_municipios.csv', sep=',',
                           encoding='utf-8')

file_geo = gpd.read_file('portugal_municipios.geojson')

file_geo_guimaraes = gpd.read_file('/ContinenteConcelhos.geojson')

# %% Fill empty cells
infetados['Felgueiras'][3] = 24
infetados['Funchal'][2] = 10
infetados['Funchal'][3] = 10
infetados['Santarém'][6] = 22
infetados['Cartaxo'][8] = 9
infetados['Câmara de Lobos'][2] = 3
infetados['Câmara de Lobos'][3] = 3
infetados['Lagoa'][2] = 3
infetados['Lagoa'][5] = 3
infetados['Lagoa'][6] = 3
infetados['Lagoa'][11] = 3
infetados['Ilha da Madeira'][4:25] = 20
infetados['Amares'][3] = 6
infetados['Castro Daire'][7] = 4
infetados['Baião'][8] = 4
infetados['Peniche'][7] = 3
infetados['Ponte de Lima'][7:11] = 5
infetados['Porto Santo'][7] = 3
infetados['Sever do Vouga'][7:11] = 3
infetados['Torres Novas'][5] = 3
infetados['Torres Novas'][7:10] = 4
infetados['Ilha de São Jorge'][4:25] = 7
infetados['Cantanhede'][14] = 22
infetados['Ilha Terceira'][4:25] = 6
infetados['Ilha de São Miguel'][4:25] = 5
infetados['Lagos'][3] = 4
infetados['Lagos'][4] = 4
infetados['Lagos'][7:12] = 3
infetados['Ilha do Faial'][4:25] = 3
infetados['Ilha do Pico'][4:25] = 3
infetados['Almeida'][5] = 3
infetados['Almeida'][7:16] = 6
infetados['Torre de Moncorvo'][5] = 3
infetados['Torre de Moncorvo'][7:12] = 3
infetados['Caldas da Rainha'][7:16] = 8
infetados['Ponta Delgada'][7:22] = 7
infetados['Angra do Heroismo'][7:25] = 5
infetados['Vila Nova de Foz Côa'][7:14] = 19
infetados['Abrantes'][7:15] = 7
infetados['Trancoso'][8:15] = 3
infetados['Seia'][7:16] = 4
infetados['Alcanena'][7:15] = 3
infetados['Azambuja'][7:21] = 3
infetados['Mortágua'][11:23] = 3
infetados['Carregal do Sal'][11:14] = 3
infetados['Figueiró dos Vinhos'][11:13] = 3
infetados['Gouveia'][11:16] = 3
infetados['Oliveira do Hospital'][14:16] = 3
infetados['Portalegre'][17:21] = 3
infetados['Bombarral'][17:20] = 3
infetados['Guarda'][2:6] = 3

infetados = infetados.fillna(0)

infetados.columns = infetados.columns.str.rstrip()

# %% Transpose dataframe to add more counties later
transpose_infetados = infetados.set_index(['Data']).stack().reset_index()
transpose_infetados = transpose_infetados.rename({'level_1': 'Local', 0: 'Infetados'}, axis=1)

# Remove the extra space
transpose_infetados['Local'] = transpose_infetados['Local'].str.rstrip()

# %% Get only the the county name and fips
# Remove the islands
municipio_df = municipio_df[municipio_df['name_1'] != 'Azores']
municipio_df = municipio_df[municipio_df['name_1'] != 'Madeira']

fips = municipio_df[['name_2', 'cartodb_id']]
fips = fips.rename({'name_2': 'Local'}, axis=1)

# %% Complete the counties
transpose_infetados['Data'] = transpose_infetados['Data'].dt.strftime('%m-%d')
transpose_infetados['Data'] = transpose_infetados['Data'].astype(str)

local_uniques = transpose_infetados.groupby('Local').size().reset_index(name='Count')
check_local_notin_municipios = local_uniques[~(local_uniques['Local'].isin(fips['Local']))].reset_index()

fips_transpose_infetados = fips.merge(transpose_infetados, how='left')
to_add = fips_transpose_infetados[fips_transpose_infetados['Data'].isna()]
to_add = to_add.iloc[:, 0:2]
to_add = to_add.T

to_add.columns = to_add.iloc[0]
to_add = to_add.drop(to_add.index[0])

infetados = infetados.join(to_add)
infetados = infetados.fillna(0)

# %% Transpose the dataset
infetados['Data'] = infetados['Data'].dt.strftime('%Y-%m-%d')
inf_transp = infetados.T
inf_transp.columns = inf_transp.iloc[0]
inf_transp = inf_transp.drop(inf_transp.index[0])
inf_transp = inf_transp.reset_index()
inf_transp = inf_transp.rename({'index': 'Local'}, axis=1)
inf_transp[inf_transp.columns[1:26]] = inf_transp[inf_transp.columns[1:26]].astype(int)

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
df_join = df_join.iloc[:, 9:40]
df_join = df_join[df_join['name_1'] != 'Azores']
df_join = df_join[df_join['name_1'] != 'Madeira']
df_join = df_join.iloc[:, 3:]
df_join.head()
df = pd.DataFrame(df_join)

# %% Visualization of Portugal without the islands
values = '2020-04-10'

# set the value range for the choropleth
vmin, vmax = 1, 1020

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
    vmin, vmax = 1, 1020

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

    filepath = os.path.join('/Users/taniacarvalho/Desktop/Tek/Covid-19/', day + '.png')
    chart = plot.get_figure()
    chart.savefig(filepath)


# %% Generate a gif
frames = []
imgs = glob.glob("/Users/taniacarvalho/Desktop/Tek/Covid-19/*.png")

imgs = natsort.natsorted(imgs)

for i in imgs:
    new_frame = Image.open(i)
    frames.append(new_frame.copy())

images = list(map(lambda filename: imageio.imread(filename), imgs))

imageio.mimsave(os.path.join('/Users/taniacarvalho/Desktop/Tek/Covid-19/mapa.gif'), images, fps=1)

optimize("/Users/taniacarvalho/Desktop/Tek/Covid-19/mapa.gif")

# gifsicle -O3 old.gif -o new.gif


