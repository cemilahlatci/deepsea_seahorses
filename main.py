import dash
from dash import html, dcc, callback, Output, Input, State, ctx
from dash import dash_table as dtb
from dash.exceptions import PreventUpdate
import pandas as pd
import openpyxl
import plotly.express as px
import dash_bootstrap_components as dbc
from dateutil.relativedelta import relativedelta
from datetime import datetime as dt
from datetime import date, timedelta as td
import numpy as np
import dash_auth



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server


blackbold={'color': 'black', 'font-weight': 'bold'}
regions = ['City', 'District', 'Pharmacy']

df1 = pd.read_csv("data/otc_all_others.csv", low_memory=False)
df1 = df1[df1.glnno != 8680001200399] # Gebze Eczanesi 2215 sales location wrong
# minday = df1['created_at'].min()
# endday = df1['created_at'].max()
# df22 = pd.date_range(start='2022-01-01 00:00:00', end = minday )
# df23 = pd.date_range(start = endday, end = '2023-12-31 23:59:59')
# df2022 = df22.to_frame()
# df2023 = df23.to_frame()
# df2022.columns = ['created_at']
# df2023.columns = ['created_at']
# newdf = pd.concat([df2022, df1], axis=0, ignore_index=True)
# findf = pd.concat([newdf, df2023], axis=0, ignore_index=True)
# fin = findf.fillna(0)
dmap = df1[['glnno', 'Eczane adı', 'kalfaad', 'barcode', 'Ürün Adı', 'boro', 'İlçe',
            'latitude', 'longitude', 'Ana Kategori', 'Alt Kategori 1', 'Alt Kategori 2', 'Firma', 'created_at']]
df2 = dmap[['glnno', 'boro', 'İlçe', 'latitude', 'longitude', 'Ana Kategori', 'Eczane adı', 'Firma', 'barcode']]

dmapbay = dmap[dmap.Firma.str.contains('BAYER', na=False)]
by2 = dmapbay[['glnno', 'boro', 'İlçe', 'latitude', 'longitude', 'Ana Kategori', 'Eczane adı', 'Firma', 'created_at',
               'barcode']]
by2["created_at"] = pd.to_datetime(by2["created_at"]).dt.normalize()

# Sunburst
df = df1[['Ana Kategori', 'Alt Kategori 1', 'Alt Kategori 2', 'Alt Kategori 3', 'created_at']]    # use fin for production
analiz = df.groupby(by=['Ana Kategori',
                        'Alt Kategori 1',
                        'Alt Kategori 2',
                        'Alt Kategori 3'], as_index=False).agg({"created_at": pd.Series.count})
analiz =analiz.sort_values("created_at", ascending=False)
sun = px.sunburst(analiz,
                  path=['Ana Kategori', 'Alt Kategori 1', 'Alt Kategori 2', 'Alt Kategori 3'],
                  values='created_at',
                  maxdepth=2,
                  labels = {"created_at": "Adet"}
                  ).update_traces(textinfo= 'label+percent entry')  # insidetextorientation='radial'
sun.update_layout(margin=dict(t=15, l=0, r=0, b=0)) # uniformtext=dict(minsize=10, mode='show')

# datatable timetable
tdy = pd.to_datetime(date.today())
stday = tdy - td(days=151)      # to be deleted in production mode
ysdy = stday - td(days=1)       # to be replaced in production mode tdy
thwf = ysdy - td(days=ysdy.weekday())
thmf = ysdy + pd.offsets.MonthEnd(0) - pd.offsets.MonthBegin(1)
thqf = ysdy - pd.offsets.QuarterBegin(startingMonth=1)
thyf = pd.offsets.YearBegin().rollback(ysdy)
ls7d = ysdy - td(days=6)
ls14 = ysdy - td(days=13)
ls28 = ysdy - td(days=27)
frst = pd.to_datetime('2023-02-17 00:00:00')     # connect to datepicker
fren = pd.to_datetime('2023-03-17 00:00:00')     # connect to datepicker

psdy = ysdy - td(days=1)
prwf = thwf - td(days=7)
prmf = ysdy + pd.offsets.MonthEnd(0) - pd.offsets.MonthBegin(2)
prqf = thqf - pd.offsets.QuarterBegin(startingMonth=1)
prye = stday - relativedelta(years=1)
pryf = pd.offsets.YearBegin().rollback(prye)
prwe = stday - td(days=7)       # to be replaced in production mode with tdy
prme = prmf + (stday - thmf)    # to be replaced in production mode with tdy
prqe = prqf + (stday - thqf)    # to be replaced in production mode with tdy
p28s = ls28 - td(days=28)
pfrf = frst - td(days=28)

st_date = [ysdy, thwf, thmf, thqf, thyf, ls7d, ls14, ls28, frst]
en_date = [stday, stday, stday, stday, stday, stday, stday, stday, fren]
pr_st_dt = [psdy, prwf, prmf, prqf, pryf,  ls14, ls28, p28s, pfrf]
pr_en_dt = [ysdy, prwe, prme, prqe, prye, ls7d, ls14, ls28, frst]
index = ["Yesterday", "This_Week", "This_Month", "This_Quarter", "This_Year", "Last_7Days", "Last_14Days",
         "Last_28Days", "Date_Picker"]
tdf_data = {"Chosen Start Date": st_date, "Chosen End Date": en_date, "     Previous Period Start": pr_st_dt,
            "Previous Period End": pr_en_dt}
tdf = pd.DataFrame(tdf_data, index)
print(tdf)

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
                [
                    html.Img(src='assets/crossist_logo.png')
                ], width=4, className="mt-1",
            ),
        dbc.Col(html.Div("Bayer OTC Dashboard",
                         style={'fontSize': 40, }), width=4,  className="mt-3", ),
        dbc.Col(
                [
                    html.Img(src='assets/Bayer.png'),
                             ], width={"size": 1, "offset": 2}, className="mt-1"
                          ),
                ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Map Graph Filtering", className="card-title text-white bg-warning"),
                    html.P(
                        "First choose on of the options(All, City, District..."
                        "Then make a selection on 'Choose Region' section",
                        className="card text-white bg-warning mb-3",
                            ),
                             ])
            ])
                ]),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Period Monitoring", className="card-title text-white bg-success"),
                    html.P(
                        "Choose a period then group the data for better interval"
                        "Detailed data can be monitored via period section",
                        className="card text-white bg-success mb-3",
                            ),
                            ])
            ])
                    ]),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Interactive Pie Chart Category", className="card-title text-white bg-info"),
                    html.P(
                        "Main slices and sub slices can be clicked and monitored"
                        "Click the center to get back to the upper branch",
                        className="card text-white bg-info mb-3",
                            ),
                            ])
            ])
                    ]),
            ]),
    dbc.Row([

        dbc.Col([
            html.Div([
                html.Ul([
                    html.Li("Bayer", className='circle', style={'color': '#ff33ff', 'font-weight': 'bold'}),
                    html.Li("Others", className='circle', style={'color': '#636efa', 'font-weight': 'bold'}),

                        ], style={'border-bottom': 'solid 3px', 'border-color': '#f39b16', 'padding-top': '6px',
                                  'padding-bottom': '6px'}),
                    ]),
            # Region_checklist
            html.Label(children=['Region: '], style=blackbold),
            dcc.RadioItems(id='reg_choice',
                           options=[{'label': "          All", 'value': "Firma"},
                                    {'label': "          City", 'value': "boro"},
                                    {'label': "          District", 'value': "İlçe"},
                                    {'label': "          Pharmacy", 'value': "glnno"}],
                           value='boro',
                           inputStyle={"margin-left": "15px"},
                           ),
            html.Label(children=['Choose Region: '],
                       style={'color': 'black', 'font-weight': 'bold', 'padding-top': '5px'}),
            # Dynamic Dropdown
            dcc.Dropdown(options=[], id='dyn_dropdown', value=None, multi=False),
            # Category_checklist
            html.Label(children=['Category: '], style={'color': 'black', 'font-weight': 'bold', 'padding-top': '5px'}),
            dcc.RadioItems(id='cat_choice',
                           options=[{'label': str(b), 'value': b} for b in sorted(by2['Ana Kategori'].unique())],
                           value='Vitaminler',
                           ),

                ], width=2, style={'border-bottom': 'solid 3px', 'border-color': '#f39b16', 'padding-top': '2px',
                                   'padding-bottom': '6px'}
                ),
        dbc.Col([
            dcc.Graph(id='map_fig', figure={}),
            dbc.Card(id="date_input_table", style={'padding-left': '80px', "border": '0px'}, children={}),
            #
            ], width=6,),


        dbc.Col([
            dcc.Graph(id="sunburst1", figure=sun)
                                ], width=4),
            ]),
    dbc.Row([
        dbc.Col([
            html.Label(children=['Current Period: '], style={"color": 'success', 'padding-left': '2px', 'font-weight': 'bold'}),
            dbc.ButtonGroup([
                dbc.Button("Yesterday", color='success', active=True, size='md', id="Yesterday", className="me-3", n_clicks=0, style={'padding-top': '6px'}),
                dbc.DropdownMenu([
                    dbc.DropdownMenuItem("Week", id="This_Week"),
                    dbc.DropdownMenuItem("Month", id="This_Month"),
                    dbc.DropdownMenuItem("Quarter", id="This_Quarter"),
                    dbc.DropdownMenuItem("Year", id="This_Year")],
                    label="This",
                    group=True,
                    color="success",
                                ),
                dbc.DropdownMenu([
                    dbc.DropdownMenuItem("7 Days", id="Last_7Days"),
                    dbc.DropdownMenuItem("14 Days", id="Last_14Days"),
                    dbc.DropdownMenuItem("28 Days", id="Last_28Days")],
                    label="Last",
                    group=True,
                    color="success",
                                ),
                            ], vertical=True),
                html.Div(id='group_ctx', hidden=False)
                ], width=1),


        dbc.Col([
            html.Label(children=['Group By: '], style={"color": 'success', 'padding-left': '40px', 'font-weight': 'bold'}),
            dbc.ButtonGroup([
                dbc.Button("Day", color='success', active=True, size='md', id="day", className="ms-4", n_clicks=0, style={'padding-top': '6px'}),
                dbc.Button("Week", color='success', active=True, size='md', id="week", className="ms-4", n_clicks=0, style={'padding-top': '6px'}),
                dbc.Button("Month", color='success', active=True, size='md', id="month", className="ms-4", n_clicks=0, style={'padding-top': '6px'}),
                dbc.Button("Quarter", color='success', active=True, size='md', id="quarter", className="ms-4", n_clicks=0, style={'padding-top': '6px'}),
                            ], vertical=True),
            html.Div(id='container_ctx_clicked', hidden=False, style={'padding-left': '30px'})
                ], width=1, className="ms-2"),

        dbc.Col([
            dbc.Card(id='datatable_id', style={'padding-left': '72px', "border": '0px'}, children={}),
            ], width=5, className="mt-2"),
                 ]),
                            ])

    # dbc.Row([
    #    dbc.Col([
    #        dcc.DatePickerRange(
    #                    id="datepicker",
    #                    min_date_allowed="2022-02-13 00:00:00",
    #                    max_date_allowed="2023-06-15 23:59:59",
    #                    end_date=max(df["created_at"]),
    #                    start_date=min(df["created_at"]),
    #                    clearable=True,
    #                    day_size=30,
    #                    end_date_placeholder_text="Enter End Date",
    #                    firt_day_of_week=1,
    #                    number_of_months_shown=1,
    #                    initial_visible_month = "2023-01-01",
    #                   style={'font-size': '6px', 'display': 'inline-block', 'border-radius' : '2px',
    #                           'border': '1px solid #ccc', 'color': '#333',
    #                           'border-spacing': '0', 'border-collapse': 'separate'}
    #                            ),

    #    ]),

    # ])


@app.callback(
    Output('map_fig', 'figure'),
    Input('reg_choice', 'value'),
    Input('cat_choice', 'value'),
           )
def update_map(reg_choice, cat_choice):
    df3 = df2[df2["Ana Kategori"].isin([cat_choice])]
    df3b = by2[by2["Ana Kategori"].isin([cat_choice])]
    if reg_choice == 'Firma':
        dftot = pd.DataFrame(np.array([df3.groupby('boro').count().sum()[0]]), columns=['count'])
        dftot['latitude'] = 39.92509322108889
        dftot['longitude'] = 32.837063345976304
        dftotb = pd.DataFrame(np.array([df3b.groupby('boro').count().sum()[0]]), columns=['count'])
        dftotb['latitude'] = 39.92509322108889
        dftotb['longitude'] = 32.837063345976304
        fig = px.scatter_mapbox(dftot, lat='latitude', lon='longitude', zoom=4.3, height=500,
                                width=700,
                                center=dict(lat=38.000, lon=35.00), mapbox_style="carto-positron",
                                size='count', size_max=40,
                                hover_data={'count': True, 'latitude': False, 'longitude': False},
                                labels={"count": "Adet"})
        fig2 = px.scatter_mapbox(dftotb, lat='latitude', lon='longitude', zoom=4.3, height=500, width=700,
                                 center=dict(lat=38.000, lon=35.00), mapbox_style="carto-positron",
                                 size='count', size_max=15, color_discrete_sequence=["fuchsia"],
                                 opacity=0.8, hover_data={'count': True, 'latitude': False, 'longitude': False},
                                 labels={"count": "Adet"})
        fig.add_trace(fig2.data[0])
    else:
        # figure others
        df4 = df3[['glnno', 'boro', 'İlçe', 'Firma']]
        dfs = df4.groupby(by=reg_choice).count().reset_index()
        dfsn = dfs.rename(columns={'Firma': 'count', })
        df5 = dfsn.merge(df3, on=reg_choice)
        dfecza = df5.drop_duplicates(subset=reg_choice)
        dfecz = dfecza
        dfecz['scale'] = dfecza['count']

        # figure bayer
        df3b = by2[by2["Ana Kategori"].isin([cat_choice])]
        df4b = df3b[['glnno', 'boro', 'İlçe', 'Firma']]
        dfsb = df4b.groupby(by=reg_choice).count().reset_index()
        dfsnb = dfsb.rename(columns={'Firma': 'count'})
        df5b = dfsnb.merge(df3b, on=reg_choice)
        dfeczab = df5b.drop_duplicates(subset=reg_choice)
        dfeczb = dfeczab
        dfeczb['scale'] = dfeczab['count']*df5['count'].max()**2/df5b['count'].max()**2

        if reg_choice == 'glnno':
            fig = px.scatter_mapbox(dfecz, lat='latitude', lon='longitude', zoom=4.3, height=500, width=700,
                                center=dict(lat=38.000, lon=35.00), mapbox_style="carto-positron",
                                size='scale',  labels= {"count": "Adet", "boro": "City"},
                                hover_data={reg_choice: False, 'Ana Kategori': True, 'latitude': False,
                                            'longitude': False, 'Eczane adı': True, 'count': True, 'scale': False})
            fig2 = px.scatter_mapbox(dfeczb, lat='latitude', lon='longitude', zoom=4.3, height=500, width=700,
                                     center=dict(lat=38.000, lon=35.00), mapbox_style="carto-positron",
                                     size='scale', size_max=8,  color_discrete_sequence=["fuchsia"],
                                     opacity=0.8,
                                     labels={"count": "Adet", "boro": "City"},
                                     hover_data={'Eczane adı': True,
                                                 'Ana Kategori': True,
                                                 'count': True, 'scale': False,
                                                 'latitude': False,
                                                 'longitude': False})
            fig.add_trace(fig2.data[0])
        else:
            dflong = df3.groupby(by=reg_choice)['longitude'].mean().to_frame("avg_long")
            dflati = df3.groupby(by=reg_choice)['latitude'].mean().to_frame("avg_lati")
            dffinal = dfecza.merge(dflati, on=reg_choice).merge(dflong, on=reg_choice)
            dffinalb = dfeczb.merge(dflati, on=reg_choice).merge(dflong, on=reg_choice)
            fig = px.scatter_mapbox(dffinal, lat='avg_lati', lon='avg_long', zoom=4.3, height=500, width=700,
                                center=dict(lat=38.000, lon=35.00), mapbox_style="carto-positron",
                                size='count', labels={"scale": "Adet", "boro": "City"},
                                hover_data={reg_choice: True, 'Ana Kategori': True, 'latitude': False, 'longitude': False,
                                            'avg_long': False, 'avg_lati': False, 'scale': True, 'count': False})
            fig2 = px.scatter_mapbox(dffinalb, lat='avg_lati', lon='avg_long', zoom=4.3, height=500, width=700,
                                     center=dict(lat=38.000, lon=35.00), mapbox_style="carto-positron",
                                     size='scale', size_max=8, color_discrete_sequence=["fuchsia"],
                                     opacity=0.8,
                                     labels={"count": "Adet", "boro": "City"},
                                     hover_data={reg_choice: True,
                                                 'Eczane adı': False,
                                                 'Ana Kategori': True,
                                                 'count': True, 'scale': False,
                                                 'latitude': False,
                                                 'longitude': False,
                                                 'avg_lati': False,
                                                 'avg_long': False})
            fig.add_trace(fig2.data[0])
    return fig


@app.callback(
    Output('dyn_dropdown', 'options'),
    Input("reg_choice", "value")
        )
def update_choice(chosen_radioitem):
    if chosen_radioitem == "Firma":
        dff = by2[["Firma"]]
    elif chosen_radioitem == "boro":
        dff = by2[["boro"]]
    elif chosen_radioitem == "İlçe":
        dff = by2[["İlçe"]]
    elif chosen_radioitem == "glnno":
        chosen_radioitem = "Eczane adı"
        dff = by2[["Eczane adı"]]

    return [{'label': c, 'value': c} for c in sorted(dff[chosen_radioitem].unique())]


@app.callback(Output('container_ctx_clicked', 'children'),
              Input('day', 'n_clicks'),
              Input('week', 'n_clicks'),
              Input('month', 'n_clicks'),
              Input('quarter', 'n_clicks'),
              )
def display2(btn9, btn10, btn11, btn12):
    container_ctx_clicked = ctx.triggered_id
    return container_ctx_clicked


@app.callback(Output('group_ctx', 'children'),
              Output('date_input_table', 'children'),
              Input('Yesterday', 'n_clicks'),
              Input('This_Week', 'n_clicks'),
              Input('This_Month', 'n_clicks'),
              Input('This_Quarter', 'n_clicks'),
              Input('This_Year', 'n_clicks'),
              Input('Last_7Days', 'n_clicks'),
              Input('Last_14Days', 'n_clicks'),
              Input('Last_28Days', 'n_clicks'),
              # Input('container_ctx_clicked', 'value'),
              # Input('cat_choice', 'value'),
              # Input('reg_choice', 'value'),
              Input('dyn_dropdown', 'value'),
              )
def display(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, dyn_dropdown):
    # dt_list = []
    gr_button_clicked = ctx.triggered_id
    if gr_button_clicked == "dyn_dropdown":
            dt_list = ["No Date Chosen", "No Date Chosen", "No Date Chosen", "No Date Chosen", ]
            columns = ["Chosen Start Date", "Chosen End Date", "Previous Period Start", "Previous Period End"]
            tdfdf2 = pd.DataFrame(dt_list, columns).transpose()
            # print(f"else state {tdfdf2}")
            date_input = dtb.DataTable(data=tdfdf2.to_dict('records'),  # dates to display in layout as string
                                       columns=[{'name': j, 'id': j} for j in tdfdf2.columns],
                                       style_cell={'textAlign': 'left', 'padding': '5px', 'backgroundColor': '#f39b16',
                                                   'color': 'white', 'fontWeight': 'bold'},
                                       style_header={'backgroundColor': '#f39b16', 'color': 'white', 'fontWeight': 'bold'},
                                       )

    else:
        tdfdf = tdf.filter(items=[gr_button_clicked], axis=0)
        date_input = dtb.DataTable(data=tdfdf.to_dict('records'),           # dates to display in layout as string
                               columns=[{'name': j, 'id': j} for j in tdfdf.columns],
                               style_cell={'textAlign': 'left', 'padding': '5px', 'backgroundColor': '#f39b16',
                                           'color': 'white', 'fontWeight': 'bold'},
                               style_header={'backgroundColor': '#f39b16', 'color': 'white', 'fontWeight': 'bold'})


    #    chosen_dates = dtb.DataTable(data=tdfdf2.to_dict('records'),              # dates as timestamp
    #                                 columns=[{'name': i, 'id': i} for i in tdfdf2.columns])

    return gr_button_clicked,  date_input


@app.callback(
    [Output('datatable_id', 'children')],
    # Input("datepicker", "start_date"),
    # Input("datepicker", "end_date"),
    [Input('date_input_table', 'children'),
     Input('cat_choice', 'value'),
     Input('reg_choice', 'value'),
     Input('dyn_dropdown', 'value'),
     Input('container_ctx_clicked', 'children'),
     Input('group_ctx', 'children')],
               )
def update_table(date_input_table, cat_choice, reg_choice_val, dyn_dropdown, container_ctx_clicked, group_ctx):
    table_dict = date_input_table["props"]['data']
    if table_dict:
        print(f"container_ctx_clicked: {container_ctx_clicked}")
        table_data = table_dict[0]
        start_date = table_data['Chosen Start Date']
        end_date = table_data['Chosen End Date']
        prstart_date = table_data['     Previous Period Start']
        prend_date = table_data['Previous Period End']
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        prstart = pd.to_datetime(prstart_date)
        prend = pd.to_datetime(prend_date)
        print(start, end, prstart, prend)
        dfcat = by2[by2['Ana Kategori'] == cat_choice]
        dfreg = dfcat[dfcat[reg_choice_val] == dyn_dropdown]
        mask1 = (by2['created_at'] >= start) & (by2['created_at'] < end)
        dfanaliz = dfreg.loc[mask1]
        dftable = dfanaliz
        dftable = dftable.loc[:, ['created_at', 'barcode']]
        dftable_copy = dftable
        dftable = dftable.reset_index()
        print(dftable)
        # dftable_copy["Curr. Year"] = pd.to_datetime(dftable['created_at']).apply(lambda x: x.date().isocalendar().year)
        # dftable_copy = dftable_copy.loc[:, ["Curr. Year"]]
        # Filter previous data
        mask2 = (by2['created_at'] >= prstart) & (by2['created_at'] < prend)
        dfanaliz2 = dfreg.loc[mask2]
        dftabpr = dfanaliz2
        dftabpr = dftabpr.loc[:, ['created_at', 'barcode']]
        dftabpr_copy = dftabpr
        dftabpr = dftabpr.reset_index()
        # dftabpr_copy["Pr.P Year"] = pd.to_datetime(dftabpr['created_at']).apply(lambda x: x.date().isocalendar().year)
        # dftabpr_copy = dftabpr_copy.loc[:, "Pr.P Year"]
        print(dftabpr)
        if not container_ctx_clicked:
            print("this is none-loop")
            # datatbl = {}
            # columnstbl = {}
        elif container_ctx_clicked == "quarter":
            print("quarter-loop")
            dftable = dftable.assign(Quarters=dftable['created_at']).drop(columns='created_at', axis=1)
            dftabpr = dftabpr.assign(Quarters=dftabpr['created_at']).drop(columns='created_at', axis=1)
            dftable = dftable.set_index('Quarters')
            dftabpr = dftabpr.set_index('Quarters')
            dftable = dftable.resample('Q', label='right', closed='left').count()
            dftabpr = dftabpr.resample('Q', label='right', closed='left').count()
            dftable["Quarter Number"] = dftable.index.quarter
            dftabpr["Quarter Number"] = dftabpr.index.quarter
            dftable["Curr. Year"] = dftable.index.year
            dftabpr["Pr.P Year"] = dftabpr.index.year
            dftable = dftable[["Curr. Year", "Quarter Number", "barcode"]]
            dftabpr = dftabpr[["Pr.P Year", "Quarter Number", "barcode"]]
            dftable.rename(columns={"Quarter Number": "CY Quarter", "barcode": "CY Sale"}, inplace=True)
            dftabpr.rename(columns={"Quarter Number": "Pr.P Quarter", "barcode": "Pr. Period Sale"}, inplace=True)
            dffin = pd.concat([dftable.reset_index(drop=True),dftabpr.reset_index(drop=True)], axis=1)
            dffin["Growth vs. pr. Period"] = ((dffin["CY Sale"] / dffin["Pr. Period Sale"] - 1) * 100).map(
                    '{:,.2f}'.format).add('%')
            dffinal = dffin[["Pr.P Year", "Pr.P Quarter", "Curr. Year", "CY Quarter", "Pr. Period Sale",
                             "CY Sale", "Growth vs. pr. Period"]]
            datatbl = dffinal.to_dict('records')
            columnstbl = [{'name': i, 'id': i} for i in dffinal.columns]

        elif container_ctx_clicked == "month":
            print("month-loop")
            dftable = dftable.assign(Months=dftable['created_at']).drop(columns='created_at', axis=1)
            dftabpr = dftabpr.assign(Months=dftabpr['created_at']).drop(columns='created_at', axis=1)
            dftable = dftable.set_index('Months')
            dftabpr = dftabpr.set_index('Months')
            dftable = dftable.resample('M', label='right', closed='left').count()
            dftabpr = dftabpr.resample('M', label='right', closed='left').count()
            dftable["Month Number"] = dftable.index.month
            dftabpr["Month Number"] = dftabpr.index.month
            dftable["Curr. Year"] = dftable.index.year
            dftabpr["Pr.P Year"] = dftabpr.index.year
            dftable = dftable[["Curr. Year", "Month Number", "barcode"]]
            dftabpr = dftabpr[["Pr.P Year", "Month Number", "barcode"]]
            # dftable.rename(columns={"Month Number": "CY Month", "barcode": "CY Sale"}, inplace=True)
            dftable.rename(columns={"barcode": "CY Sale"}, inplace=True)
            # dftabpr.rename(columns={"Month Number": "Pr.P Month", "barcode": "Pr. Period Sale"}, inplace=True)
            dftabpr.rename(columns={"barcode": "Pr. Period Sale"}, inplace=True)
            # dffin = pd.concat([dftable.reset_index(drop=True), dftabpr.reset_index(drop=True)], axis=1)
            dffin = pd.merge(dftable, dftabpr, how='outer', on='Month Number')
            dffin["Growth vs. pr. Period"] = ((dffin["CY Sale"] / dffin["Pr. Period Sale"] - 1) * 100).map(
                '{:,.2f}'.format).add('%')
            dffin.rename(columns={"Month Number": "Pr.P Month"}, inplace=True)
            dffin['CY Month'] = dffin["Pr.P Month"]
            dffinal = dffin[["Pr.P Year", "Pr.P Month", "Curr. Year", "CY Month", "Pr. Period Sale",
                             "CY Sale", "Growth vs. pr. Period"]]
            datatbl = dffinal.to_dict('records')
            columnstbl = [{'name': i, 'id': i} for i in dffinal.columns]

        elif container_ctx_clicked == "week":
            print("week-loop")
            dftable = dftable.assign(Weeks=dftable['created_at']).drop(columns='created_at', axis=1)
            dftabpr = dftabpr.assign(Weeks=dftabpr['created_at']).drop(columns='created_at', axis=1)
            dftable = dftable.set_index('Weeks')
            dftabpr = dftabpr.set_index('Weeks')
            dftable = dftable.resample('W', label='right', closed='left').count()
            dftabpr = dftabpr.resample('W', label='right', closed='left').count()
            print(dftable.columns)
            print(dftable.head())
            dftable["Week Number"] = pd.to_datetime(dftable.index).isocalendar().week
            dftabpr["Week Number"] = pd.to_datetime(dftabpr.index).isocalendar().week
            dftable["Curr. Year"] = dftable.index.year
            dftabpr["Pr.P Year"] = dftabpr.index.year
            dftable = dftable[["Curr. Year", "Week Number", "barcode"]]
            dftabpr = dftabpr[["Pr.P Year", "Week Number", "barcode"]]
            dftable.rename(columns={"barcode": "CY Sale"}, inplace=True)
            dftabpr.rename(columns={"barcode": "Pr. Period Sale"}, inplace=True)

            dffin = pd.merge(dftable, dftabpr, how='outer', on='Week Number')
            dffin["Growth vs. pr. Period"] = ((dffin["CY Sale"] / dffin["Pr. Period Sale"] - 1) * 100).map(
                '{:,.2f}'.format).add('%')
            dffin.rename(columns={"Week Number": "Pr.P Week"}, inplace=True)
            dffin['CY Week'] = dffin["Pr.P Week"]
            dffinal = dffin[["Pr.P Year", "Pr.P Week", "Curr. Year", "CY Week", "Pr. Period Sale",
                             "CY Sale", "Growth vs. pr. Period"]]
            datatbl = dffinal.to_dict('records')
            columnstbl = [{'name': i, 'id': i} for i in dffinal.columns]

        elif container_ctx_clicked == "day":
            print("day-loop")
            dftable = dftable.assign(Days=dftable['created_at']).drop(columns='created_at', axis=1)
            dftabpr = dftabpr.assign(Days=dftabpr['created_at']).drop(columns='created_at', axis=1)
            dftable = dftable.set_index('Days')
            dftabpr = dftabpr.set_index('Days')
            dftable = dftable.resample('D', label='right', closed='left').count()
            dftabpr = dftabpr.resample('D', label='right', closed='left').count()
            print(dftable.columns)
            print(dftable.head())
            print(type(dftable.index))
            dftable["DayandMonth"] = dftable.index.dayofyear
            dftabpr["DayandMonth"] = dftabpr.index.dayofyear
            dftable["Curr. Year"] = dftable.index.year
            dftabpr["Pr.P Year"] = dftabpr.index.year
            dftable = dftable[["DayandMonth", "barcode"]]
            dftabpr = dftabpr[["DayandMonth", "barcode"]]
            dftable.rename(columns={"barcode": "CY Sale"}, inplace=True)
            dftabpr.rename(columns={"barcode": "Pr. Period Sale"}, inplace=True)
            dffin = pd.merge(dftable, dftabpr, how='outer', on='DayandMonth')
            if group_ctx == "Yesterday":
                growth1 = ((dftable.loc[stday, "CY Sale"] / dftabpr.loc[ysdy, "Pr. Period Sale"] - 1) * 100).item()
                growth = round(growth1, 2)
                dffin["Growth vs. pr. Period"] = str(f'{growth} %')
            else:
                dffin["Growth vs. pr. Period"] = ((dffin["CY Sale"] / dffin["Pr. Period Sale"] - 1) * 100).map(
                                                    '{:,.2f}'.format).add('%')
            dffin.rename(columns={"DayandMonth": "Pr.PDay"}, inplace=True)
            dffin['CYDay'] = dffin["Pr.PDay"]
            dffin["Pr.Per. Day"] = pd.to_datetime(dffin['Pr.PDay'] - 1, origin=pryf, unit='D')
            dffin["CY Day"] = pd.to_datetime(dffin['CYDay'] - 1, origin=thyf, unit='D')
            dffinal = dffin[["Pr.Per. Day", "CY Day", "Pr. Period Sale", "CY Sale", "Growth vs. pr. Period"]]

            datatbl = dffinal.to_dict('records')
            columnstbl = [{'name': i, 'id': i} for i in dffinal.columns]
    else:
        raise PreventUpdate

    return [dtb.DataTable(data=datatbl, columns=columnstbl, style_cell={'textAlign': 'left', 'padding': '5px'},
                          style_header={'backgroundColor': 'hotpink', 'color': 'white', 'fontWeight': 'bold'})]


if __name__ == "__main__":
    app.run(debug=False)
