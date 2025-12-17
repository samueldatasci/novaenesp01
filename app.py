# Add copyright
# Autoscale Y
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

from ChartUtils import chart
from appfuncs import *

import os
import locale

import logging
import datetime

# Configure logging (Place this at the top of your script or in your main app file)
# This creates a file 'chart_usage.log' and appends new entries to it.
logging.basicConfig(
    filename='logs/chart_usage.log', 
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
st.set_page_config(page_title="Interactive Education Data", layout="wide", )

st.logo("IMS_LogoHorizontal_positivo.png")

# --- 1. LOAD DATA & FUNCTIONS ---
@st.cache_data
def load_data():
	
    #file_path = "../data/parquet/dfAllFase1.parquet.gzip" 
    file_path = "../data/feather/shortdf.feather" 

    try:
        #return pd.read_parquet(file_path)
        return pd.read_feather(file_path)
    except FileNotFoundError:
        # Fallback for testing if you haven't put your file in yet
        st.warning("Data File not found.")
        return




def buildChart(data, xvar, yvar, zvar, yop, filters):
   
	title=""

	if zvar == "None":
		zvar = None
	elif zvar == "Nuts2":
		zvar = "DescrNuts2"
	elif zvar == "Pub/Priv":
		zvar = "PubPriv"
	elif zvar == "Ano":
		zvar = "ano"
	elif zvar == "Exam":
		zvar = "DescrExamAbrev"

		
	if zvar is None:
		legend = False
	else:
		legend = True

	dfx = prepdata( data, xvar=xvar, yvar=yvar, yop=yop, zvar=zvar, filters=filters)



	if xvar == "ClassExam":
		xlimit = (0, 20)
	else:
		xlimit = None




	if dfx.shape[0] == 0:
		st.write("No data selected. Review the filter conditions.")
		return ""

	yvar="val"

	# Prep Chart

	fig = chart(kind="line", df=dfx, stacked=False, normalize=False, \
		xvar=xvar, xlabel = 'Classification', xlimit=None, xAxisScale=None, xAxisScaleSymbol=None, \
		yvar=yvar, ylabel='Number of exams', ylimit=(0, None), yAxisScale=None, yAxisScaleSymbol=None, \
		zvar=zvar, zlabel = "", \
		title=title, grid=True, colormap='NOVAIMS', legend=legend, xticks=None, yticks=None, figsize=(8,4.5), \
		dots = [])

	st.pyplot(fig)

	return


data = load_data()


# --- 2.1 CONFIG UI (CHART OPTIONS) ---
st.sidebar.header("Variables:")


motif = st.sidebar.selectbox("Motif", ["Exams p/grade", "Exams p/grade (norm)", "Mean grade p/year", "Median grade p/year"])
#xvar = st.sidebar.selectbox("Axis (X)", ["Class_Exam", "ano"])  # DescrExamAbrev
#yop  = st.sidebar.selectbox("Metric (Y)", ["count", "count normalized", "mean grade", "median grade"])
zvar = st.sidebar.selectbox("Series (Z)", ["None", "Covid", "Ano", "Sexo", "Pub/Priv", "Nuts2", "Exam"])


# --- 2.2 SIDEBAR UI (FILTERS) ---
st.sidebar.header("Filters:")
Covid = st.sidebar.selectbox("Before/After COVID", ["All", "Before", "After"])
ano = st.sidebar.selectbox("Year", ["All", 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024])
Sexo = st.sidebar.selectbox("Gender", ["All", "Boys", "Girls"])
PubPriv = st.sidebar.selectbox("Pub/Priv", ["All", "PRI", "PUB"])
# DescrNuts2 = st.sidebar.selectbox("DescrNuts2", ["All", "Norte", "AM Lisboa", "Centro", "Alentejo", "Algarve", "RA Madeira", "RA Açores", "Estrangeiro"])
DescrExameAbrev = st.sidebar.selectbox("Exam", ["All", "Português", "Biologia e Geologia", "Matemática A", "Física e Química A", "Geografia A", "História A", "Filosofia", "Economia A", "Matemática Aplic. às Ciências Soc.", "Geometria Descritiva A", "Inglês"])



# --- 3. MAIN AREA ---
st.title("Interactive Education Analysis")
#st.markdown("Adjust the filters on the left to explore the dynamics of education data.")


filters = {}
filters["Covid"] = Covid
filters["ano"] = ano
filters["Sexo"] = Sexo
filters["PubPriv"] = PubPriv
#filters["DescrNuts2"] = DescrNuts2
filters["DescrExameAbrev"] = DescrExameAbrev

yvar = None

if motif == "Exams p/grade (norm)":
	if zvar == "None" or zvar is None:
		st.warning("Normalization only applies when there are several series. Removing normalization.")
		motif == "Exams p/grade"
		xvar = "Class_Exam"
		yop = "count"
	else:
		xvar = "Class_Exam"
		yop = "count normalized"

if motif == "Exams p/grade":
	xvar = "Class_Exam"
	yop = "count"


if motif in ["Mean grade p/year", "Median grade p/year"]:
	if zvar == "Ano":
		st.warning("Cannot use 'Ano' as series when motif is 'Exams p/grade' or 'Exams p/grade (norm)'. Setting series to None.")
		zvar = None
	else:
		if motif == f"Mean grade p/year":
			xvar = "ano"
			yop = "mean"
		elif motif == f"Median grade p/year":
			xvar = "ano"
			yop = "median"


fig = buildChart( data, xvar, yvar, zvar, yop, filters)

# Display the plot

# st.divider()

