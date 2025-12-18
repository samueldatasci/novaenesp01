# Add copyright
### # Autoscale Y
# Color schema
# X ticks
# Title
# Message below
# ### Add: COVID AC/DC; Region
# Exception handling; default to safe params
# Save choices to disk
# Logo




import streamlit as st
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
#import matplotlib.colors as mcolors
import math

#from ChartUtils import chart
from appnovaenesfuncs import *

import os
import locale

import logging
import datetime


main_title="Data Research meetup by MagIC, 3rd edition"


# Configure logging (Place this at the top of your script or in your main app file)
# This creates a file 'chart_usage.log' and appends new entries to it.
logging.basicConfig(
    filename='code/logs/chart_usage.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)



# Set locale for number formatting if needed (example: US format)
try:
    locale.setlocale(locale.LC_ALL, 'pt_PT')
except:
    pass # Fallback if locale is not found


# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Data Research meetup by MagIC, 3rd edition", layout="wide", )

st.set_page_config(
    #page_icon="🧊",
    #layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.logo("code/images/IMS25_horizontal__negativo_rgb.png")

# --- 1. LOAD DATA & FUNCTIONS ---
@st.cache_data
def load_data():
	
    logging.info("Loading data.")

    #file_path = "../data/parquet/dfAllFase1.parquet.gzip" 
    #file_path = "../data/feather/shortdf.feather" 
    file_path = "data/feather/shorterdf.feather" 

    return pd.read_feather(file_path)
    # try:
    #     #return pd.read_parquet(file_path)
    #     return pd.read_feather(file_path)
    # except FileNotFoundError:
    #     # Fallback for testing if you haven't put your file in yet
    #     st.warning("Data File not found.")
    #     return




def buildChart(data, xvar, yvar, zvar, yop, filters, charttype="line", title = None, xlabel="", ylabel="", colormap='NOVAIMS'):
   

	xlabel = None
	xlimit=None
	xAxisScale=None
	xAxisScaleSymbol=None
	ylimit=None
	yAxisScale=None
	yAxisScaleSymbol=None
	zlabel=None
	xticks=None
	yticks=None


	if zvar == "None":
		zvar = None
	elif zvar == "Nuts2":
		zvar = "DescrNuts2"
	elif zvar == "Pub/Priv":
		zvar = "PubPriv"
	elif zvar == "Ano":
		zvar = "ano"
	elif zvar == "Exam":
		zvar = "DescrExameAbrev"

		
	if zvar is None:
		legend = False
	else:
		legend = True

	dfx = prepdata( data, xvar=xvar, yvar=yvar, yop=yop, zvar=zvar, filters=filters)


	xAxisScale=None
	xAxisScaleSymbol=None

	if xvar == "Class_Exam":
		xlimit = (0, 20)
		xticks = list(range(0, 21))

	elif xvar == "ano":
		xlimit = (2015, 2024)
		tmpxmin = dfx[xvar].min()
		tmpxmax = dfx[xvar].max()
		xlimit = (tmpxmin, tmpxmax)
		xticks = list(range(tmpxmin, tmpxmax+1))

	else:
		xlimit = None
		xticks = None


	tmpymin = dfx["val"].min()
	tmpymax = dfx["val"].max()

	# st.warning(f"Y min/max before autoscale: {tmpymin} / {tmpymax}")

	if tmpymax > 10000:
		yAxisScale=1/1000
		yAxisScaleSymbol=" k"

	if tmpymax <= 20:
		tmpymax = min( 20, math.ceil(tmpymax + 0.3))
		tmpymin = max( 0, math.floor(tmpymin - 0.3))
		ylimit = (tmpymin, tmpymax)
	else:
		ylimit = (0, None)




	if dfx.shape[0] == 0:
		st.write("No data selected. Review the filter conditions.")
		return ""

	yvar="val"

	# Prep Chart
	

	fig = chart(kind=charttype, df=dfx, stacked=False, normalize=False, \
		xvar=xvar, xlabel = xlabel, xlimit=xlimit, xAxisScale=xAxisScale, xAxisScaleSymbol=xAxisScaleSymbol, \
		yvar=yvar, ylabel=ylabel, ylimit=ylimit, yAxisScale=yAxisScale, yAxisScaleSymbol=yAxisScaleSymbol, \
		zvar=zvar, zlabel = "", \
		title=title, \
		grid=True, colormap=colormap, legend=legend, xticks=xticks, yticks=None, figsize=(8,4.5), \
		dots = [])

	st.pyplot(fig)

	return


data = load_data()


# --- 2.1 CONFIG UI (CHART OPTIONS) ---
st.sidebar.header("Chart:")


motif = st.sidebar.selectbox("Motif", ["Count per grade", "Count per year", "Count per exam", "Count per region", "Mean grade per year", "Mean grade per exam", "Mean grade per region"])
series = st.sidebar.selectbox("Series", ["None", "Covid", "Ano", "Sexo", "Pub/Priv", "Nuts2", "Exam"])
norx = st.sidebar.checkbox(key="Norm", label="Normalize", value=False, help="Normalize counts to relative frequencies.", disabled = ( series == "None" or motif[0:15] == "Mean grade per ") )


# --- 2.2 SIDEBAR UI (FILTERS) ---
st.sidebar.header("Filters:")
Covid = st.sidebar.selectbox("Before/After COVID", ["All", "Before", "After"])
ano = st.sidebar.selectbox("Year", ["All", 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024])
Sexo = st.sidebar.selectbox("Gender", ["All", "M", "F"])
PubPriv = st.sidebar.selectbox("Pub/Priv", ["All", "PRI", "PUB"])
DescrNuts2 = st.sidebar.selectbox("DescrNuts2", ["All", "Norte", "AM Lisboa", "Centro", "Alentejo", "Algarve", "RA Madeira", "RA Açores", "Estrangeiro"])
DescrExameAbrev = st.sidebar.selectbox("Exam", ["All", "Português", "Bio", "Matemática", "FQ", "Geogr", "Hist", "Filos", "Economia", "MACS", "Geom Descr"])
CourseType = st.sidebar.selectbox("Course Type", ["All", "Cient-Human", "Profiss", "Recorrente", "Equival", "Artísticos"])


# --- 2.3 LAYOUT ---
st.sidebar.header("Layout:")

colmaps = ["NOVAIMS", "viridis", "plasma", "inferno", "magma", "cividis", "tab10", "Set1", "Set2", "Set3", "Pastel1", "Pastel2", "Paired", "Accent"]
colormap = st.sidebar.selectbox("Color Map", colmaps, index=0)


st.info("Data source: ENES - Exames Nacionais do Ensino Secundário (Ministério da Educação, Portugal). Data processed by MagIC - Master in Data Science, NOVA IMS.")
st.info(colormap)


# --- 3. MAIN AREA ---
st.title(body=main_title, anchor=False)
#st.markdown("Adjust the filters on the left to explore the dynamics of education data.")


filters = {}
filters["Covid"] = Covid
filters["ano"] = ano
filters["Sexo"] = Sexo
filters["PubPriv"] = PubPriv
filters["DescrNuts2"] = DescrNuts2
filters["DescrExameAbrev"] = DescrExameAbrev
filters["DescrSubtipoCurso"] = CourseType

yvar = None

#st.warning(f"Building chart: {motif} | Series: {series} | Normalize: {norx}")

logging.info(f"Building chart with motif: {motif}, series: {series}, normalize: {norx}, filters: {filters}")

xlabel = ""
ylabel = ""

if motif[0:10] == "Count per ":

	yvar = None

	if motif == "Count per grade":
		xvar = "Class_Exam"
		xlabel = "Exam grade"
		title = "Distribution of exam grades"
	elif motif == "Count per year":
		xvar = "ano"
		xlabel = "Year"
		title = "Distribution of exams per year"
	elif motif == "Count per exam":
		xvar = "DescrExameAbrev"
		xlabel = "Exam"
		title = "Distribution of exams per exam"
	elif motif == "Count per region":
		xvar = "DescrNuts2"
		xlabel = "Nut II Region"
		title = "Distribution of exams per region"

	if series == "None":
		# st.warning("MagIC in progress...")
		zvar = None
		yop = "count"
	else:
		zvar = series
		if norx:
			yop = "count normalized"
			ylabel = "Number of exams (norm.)"
			title += " (normalized)"
		else:
			yop = "count"
			ylabel = "Number of exams"

elif motif[0:15] == "Mean grade per ":

	yvar = "Class_Exam"
	yop = "mean"
	ylabel = "Mean grade"

	if motif == "Mean grade per year":
		xvar = "ano"
		xlabel = "Year"
		title = "Distribution of mean grades per year"
	elif motif == "Mean grade per region":
		xvar = "DescrNuts2"
		xlabel = "Nut II Region"
		title = "Distribution of mean grades per region"
	elif motif == "Mean grade per exam":
		xvar = "DescrExameAbrev"
		xlabel = "Exam"
		title = "Distribution of mean grades per exam"

	if series == "None":
		zvar = None
	else:
		zvar = series
else:
	st.error("Select a valid combination of motif and series.")




if xvar is None:
	st.warning("Select a valid combination of motif and series.")
else:
	if xvar in ["ano", "Class_Exam"]:
		charttype="line"
	else:
		# "DescrExameAbrev", "DescrNuts2"
		charttype="bar"
	fig = buildChart( data, xvar, yvar, zvar, yop, filters, charttype=charttype, title=title, xlabel=xlabel, ylabel=ylabel, colormap=colormap )


# Display the plot

# st.divider()



