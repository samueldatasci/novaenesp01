import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import locale
import pandas as pd


from ChartUtils import *


import streamlit as st
import smtplib
from email.message import EmailMessage
import os






def send_email_with_plot(user_email, image_path):
    """
    Sends the plot via SMTP (e.g., Gmail).
    """
    sender_email = "samuel.santos.magic"  # TODO: Update this
    sender_password = "Samue.54321"  # TODO: Update this
    
    msg = EmailMessage()
    msg['Subject'] = "Here is the Education Data Chart you requested"
    msg['From'] = sender_email
    msg['To'] = user_email
    msg.set_content("Hello,\n\nAttached is the chart we generated during the poster session.\n\nBest regards,\n[Your Name]")

    with open(image_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(image_path)
    
    msg.add_attachment(file_data, maintype='image', subtype='png', filename=file_name)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False


def prepdata(df=None, xvar="Class_Exam", yvar=None, yop="count", zvar=None, kind="line", filters={}):
    
    dfRet = df.copy()

    # 1. Filter Data
    if filters:
        for key, val in filters.items():
            if val != "All":
                dfRet = dfRet[dfRet[key] == val]

    # --- NEW LOGIC: Limit Z-variable to Top 10 ---
    if zvar:
        # Get count of unique categories in Z
        unique_z_count = dfRet[zvar].nunique()
        
        # Only run this logic if we actually need to filter
        if unique_z_count > 10:
            # 1. Define 'top_z' (The top 10 categories)
            top_z = dfRet[zvar].value_counts().nlargest(10).index
            
            # 2. Filter using 'top_z'. 
            # CRITICAL: This line must be INDENTED inside this 'if' block.
            dfRet = dfRet[dfRet[zvar].isin(top_z)]
            
            print(f"Limiting '{zvar}' to top 10 categories out of {unique_z_count}.")

    # 2. Define Grouping Columns
    group_cols = [xvar]
    if zvar:
        group_cols.append(zvar)

    # 3. Aggregation Logic
    if yvar is None:
        # Count rows
        dfRet = dfRet.groupby(group_cols, dropna=False).size().reset_index(name='val')

        if yop == "count normalized":
            if zvar:
                # Re-balance based on max class size
                z_class_totals = dfRet.groupby(zvar)['val'].transform('sum')
                max_class_size = z_class_totals.max()
                dfRet['val'] = dfRet['val'] * (max_class_size / z_class_totals)
            else:
                # Percentage
                total_by_x = dfRet.groupby(xvar)['val'].transform('sum')
                dfRet['val'] = dfRet['val'] / total_by_x

    else:
        # Aggregate values (mean, median, etc.)
        grouped = dfRet.groupby(group_cols, dropna=False)

        if yop == "mean":
            dfRet = grouped.agg(val=(yvar, 'mean')).reset_index()
        elif yop == "median":
            dfRet = grouped.agg(val=(yvar, 'median')).reset_index()
        elif yop == "sum":
            dfRet = grouped.agg(val=(yvar, 'sum')).reset_index()

    return dfRet



def xPrepdata( df, xvar="Class_Exam", yvar=None, yop="count", zvar=None, zmaxclasses=8, kind="line", filters={}):
	'''
	Prepares data for plotting by filtering, grouping, and aggregating.

    :param df: Input DataFrame
    :param xvar: Column for X-axis (grouping)
    :param yvar: Column for Y-axis (value to aggregate). If None, operations assume counting rows.
    :param yop: Operation ["count",
							requires zvar: "count normalized",
							requires a yvar: "mean", "median", "sum"]
    :param zvar: Column for Z-axis (secondary grouping/stacking). Optional.
    :param kind: Chart kind (unused in this specific data prep logic, but good for context)
    :param filters: Dict of {column_name: value} to filter before processing.
	:param zmaxclasses: Maximum number of series. Limit to that number.
	'''
	
	if xvar == "None" or xvar == "":
		xvar = None
	
	if yvar == "None" or yvar == "":
		yvar = None
	
	if zvar == "None" or zvar == "":
		zvar = None
	
	dfRet = df.copy()

	# 1. Filter Data
	if filters:
		for key, val in filters.items():
			if val != "All":
				dfRet = dfRet[dfRet[key] == val]



# --- NEW LOGIC: Limit Z-variable to Top zmaxclasses ---
	if not zvar is None:
		# Get count of unique categories in Z
		unique_z_count = dfRet[zvar].nunique()

		if unique_z_count > zmaxclasses:
			# 1. Identify the top zmaxclasses most frequent categories in Z based on row count
			top_z = dfRet[zvar].value_counts().nlargest(zmaxclasses).index

			# 2. Filter the dataframe to keep only rows belonging to these top zmaxclasses
			dfRet = dfRet[dfRet[zvar].isin(top_z)]

			# Optional: Print info for verification
			print(f"Note: '{zvar}' has {unique_z_count} categories. Limiting to top {zmaxclasses}.")





	# 2. Define Grouping Columns
	group_cols = [xvar]
	if zvar:
		group_cols.append(zvar)


# 3. Aggregation Logic
    
    # CASE A: yvar is None (We are counting rows)
	if yvar is None:


		if yop == "count":
			# We group by the X (and Z) columns and count the size
			# We use 'size' to count rows even if data is missing, which is safer for frequency
			dfRet = dfRet.groupby(group_cols, dropna=False).size().reset_index(name='val')

		# If normalization is requested (Percentage of Total per X)
		if yop == "count normalized":


			dfRet = dfRet.groupby(group_cols, dropna=False).size().reset_index(name='val')


			# Scenario 1: We have groups (zvar) and want to re-balance them (Your request)
			if zvar:
				# 1. Calculate the total count for each Z class (e.g., Total Males, Total Females)
				# We use transform to keep the shape of the dataframe aligned
				z_class_totals = dfRet.groupby(zvar)['val'].transform('sum')

				# 2. Find the size of the largest class
				max_class_size = z_class_totals.max()

				# 3. Apply the ratio: val * (Max_Size / Current_Class_Size)
				# Example: If Max=100 and Males=50, Males get multiplied by 2.
				dfRet['val'] = dfRet['val'] * (max_class_size / z_class_totals)


			# # Calculate total per X (ignoring Z)
			# total_by_x = dfRet.groupby(xvar)['val'].transform('sum')
			# dfRet['val'] = dfRet['val'] / total_by_x

	# CASE B: yvar exists (We are aggregating values, e.g., Grade, Age)
	else:
		# Note: We do NOT do dfRet.groupby(...)[yvar]. We stay on the DataFrame
		# to use the named aggregation syntax.
		grouped = dfRet.groupby(group_cols, dropna=False)

		if yop == "mean":
			dfRet = grouped.agg(val=(yvar, 'mean')).reset_index()

		elif yop == "median":
			dfRet = grouped.agg(val=(yvar, 'median')).reset_index()

		elif yop == "sum":
			dfRet = grouped.agg(val=(yvar, 'sum')).reset_index()



	return dfRet





def chart(kind="line", df=None, stacked=False, normalize=False, \
	xvar=None, xlabel = '', xlimit=None, xAxisScale=None, xAxisScaleSymbol=None, \
	yvar='count', ylabel='Number of exams', ylimit=(0, None), yAxisScale=None, yAxisScaleSymbol=None, \
	zvar=None, zlabel = "", \
	title=None, grid=True, colormap='NOVAIMS', legend=True, xticks=None, yticks=None, figsize=(8,4.5), \
	dots = []):
	'''Minimum parameters: chart(kind="line", df=dataframe, xvar='Class_Exam')'''
	# Pivot the DataFrame to create the data for the stacked bar chart


	if xvar == "None" or xvar == "":
		xvar = None
	
	if yvar == "None" or yvar == "":
		yvar = None
	
	if zvar == "None" or zvar == "":
		zvar = None


	if zvar is None:
		if yvar == None:
			df_grouped = df.groupby(xvar).size().reset_index(xvar)
		else:
			df_grouped = df.groupby(xvar)[yvar].sum().reset_index(xvar)

	else:
		if yvar is None:
			df_grouped = df.groupby(xvar)[zvar].value_counts(normalize=normalize).unstack(zvar)
			df_grouped = df_grouped.reset_index()
		else:
			df_grouped = df.groupby([xvar,zvar])[yvar].sum().unstack(zvar)
			df_grouped = df_grouped.reset_index(xvar)
		


	if kind in ['bar', 'barh']:
		# only difference is that we're setting the width of each bar to 0.8
		ax = df_grouped.plot(kind=kind, stacked=stacked, \
				x=xvar, xlabel=xlabel, xlim=xlimit, \
				ylim=ylimit, ylabel=ylabel, \
				colormap=colormap, figsize=figsize, title=title, rot=0, fontsize=12, legend=legend, width = 0.8,
				ax=None, subplots=False, xticks=xticks, yticks=yticks)
		# 		y=yvar,
			
	else:
		ax = df_grouped.plot(kind=kind, stacked=stacked, \
				x=xvar, xlabel=xlabel, xlim=xlimit, \
				ylim=ylimit, ylabel=ylabel, \
				colormap=colormap, figsize=figsize, title=title, rot=0, fontsize=12, legend=legend,
				ax=None, subplots=False, xticks=xticks, yticks=yticks)
		

	fig = ax.figure

	if legend:
		plt.legend(title = zlabel)

	if isinstance(grid, bool):
		if grid == True:
			plt.grid(True)
		else:
			plt.grid(False)
	elif isinstance(grid, str):
		grid = grid.lower()
		if 'x' in grid and 'y' in grid:
			plt.grid(True)
		elif 'x' in grid:
			plt.xaxis.grid(which='major')
		elif 'y' in grid:
			plt.yaxis.grid(which='major')
		else:
			plt.grid(False)
	
	if not xAxisScale is None or not xAxisScaleSymbol is None:
		if xAxisScale is None:
			xAxisScale = 1
		if xAxisScaleSymbol is None:
			xAxisScaleSymbol = ''
		ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{x*xAxisScale:,.0f}{xAxisScaleSymbol}' ))

	if not yAxisScale is None or not yAxisScaleSymbol is None:
		if yAxisScale is None:
			yAxisScale = 1
		if yAxisScaleSymbol is None:
			yAxisScaleSymbol = ''
		ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{x*yAxisScale:,.0f}{yAxisScaleSymbol}' ))

	if kind == "line":
		
		# Show datapoint for 95 and 94, with number of exams and the datapoint value
		for dot in dots:
			dotx = dot[0]
			dotalign = dot[1]
			dotcolor = dot[2]
			dot_marker = dot[3]
			dot_marker_size = dot[4]
			try:
				doty = df[xvar].value_counts().sort_index()[dotx]

			except KeyError as ke:
				doty = 0

			dotlabel = "{:.1f}".format(dotx) + ": " + locale.format_string("%d", doty, grouping=True)
			plt.scatter(dotx, doty, color=dot[2], marker=dot_marker, s=dot_marker_size)
			if dotalign == 'left':
				dotx = dotx + 0.1
			elif dotalign == 'right':
				dotx = dotx - 0.1
				
			plt.text(dotx, doty, dotlabel, horizontalalignment=dotalign, color=dot[2], bbox=dict(facecolor='white', edgecolor='None', pad=0.1))

	
	return fig





