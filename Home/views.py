from django.shortcuts import render, HttpResponse
from plotly.offline import plot
import plotly.graph_objs as go
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import IPython

crime_dict={1:'Rape', 2: 'Kidnapping and Abduction',3: 'Dowry Deaths',
                        4: 'Assault on women with intent to outrage her modesty',
                        5: 'Insult to modesty of Women', 6: 'Cruelty by Husband or his Relatives',
                        7: 'Importation of Girls'}

# Create your views here.
def index(request):
    return render(request,'index.html')

def crime(request):
    crimes_df = pd.read_csv(r'C:\Users\meetp\OneDrive\Desktop\Coding\Dotslash\Django\crimeRate\DataSet\crimes_against_women_2001-2014.csv')
    crimes_df.drop(['Unnamed: 0'],axis=1,inplace=True)
    #Changing the cases of all the column to uppercase
    def uppername(dataset):     
        for columns in dataset.columns[:2]:         
            dataset[columns] = dataset[columns].str.upper()      
        return dataset 
    uppername(crimes_df)

    crimes_df.drop(crimes_df[(crimes_df['DISTRICT']=="TOTAL")|(crimes_df['DISTRICT']=="TOTAL DISTRICT(S)")|(crimes_df['DISTRICT']=="DELHI UT TOTAL")|(crimes_df['DISTRICT']=="ZZ TOTAL") ].index, inplace = True) 
    crimes_df['STATE/UT'].replace("A & N ISLANDS", "ANDAMAN AND NICOBAR", inplace = True)
    crimes_df['STATE/UT'].replace("A&N ISLANDS", "ANDAMAN AND NICOBAR", inplace = True)
    crimes_df['STATE/UT'].replace("D&N HAVELI", "DADRA AND NAGAR HAVELI", inplace = True)
    crimes_df['STATE/UT'].replace("D & N HAVELI", "DADRA AND NAGAR HAVELI", inplace = True)
    crimes_df['STATE/UT'].replace("DELHI UT", "DELHI", inplace = True)
    crimes_df['STATE/UT'].replace("TELANGANA", "ANDHRA PRADESH", inplace = True)
    crimes_df['STATE/UT'].replace("JAMMU & KASHMIR", "JAMMU AND KASHMIR", inplace = True)
    crimes_df['STATE/UT'].replace("DAMAN & DIU", "DAMAN AND DIU", inplace = True)

    def crimes_by_different_order(dataframe,column_name):
        "This function returns a dataframe with total number of particular crimes grouping by certain column"
        for column in list(crimes_df.columns)[3:]:
            dataframe[column]=crimes_df.groupby([column_name])[column].sum()   
        return dataframe

    total_crimes_in_years_df=pd.DataFrame()
    total_crimes_in_years_df=crimes_by_different_order(total_crimes_in_years_df,"Year")
    total_crimes_in_years_df.reset_index(inplace=True)
    total_crimes_in_years_df['Total Number of Cases']=total_crimes_in_years_df.sum(axis=1)
    # State Data
    state_ut_crimes_df=pd.DataFrame()
    state_ut_crimes_df=crimes_by_different_order(state_ut_crimes_df,"STATE/UT")
    state_ut_crimes_df

    def plot_figure(title, crime,ylabel,color="red"):
        "This function generate a bar graph using the total_crimes_in_years_df"
        fig = go.Figure(data=[go.Bar(
                x=total_crimes_in_years_df["Year"], y=total_crimes_in_years_df[crime],
                text=total_crimes_in_years_df[crime],
            )])
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside',marker_color=color)
        fig.update_layout(title=title,
                        xaxis = dict(title='Years',
                                        tickmode = 'linear',
                                        tickangle=-30 ),
                    yaxis_title=ylabel,uniformtext_minsize=8, uniformtext_mode='show')
        return fig
    
    def plotmap(crime_name):
        with open(r'C:\Users\meetp\OneDrive\Desktop\Coding\Dotslash\Django\crimeRate\DataSet\india.geojson', 'r') as fp:
            js=json.load(fp)

        for i in range(len(js["features"])):
            ls=[js["features"][i]["properties"]["NAME_1"]]
            js["features"][i]["properties"]["NAME_1"]=ls[0].upper()

        #dumping the names in the new json files named result.json and opening it
        with open(r'C:\Users\meetp\OneDrive\Desktop\Coding\Dotslash\Django\crimeRate\DataSet\result.json', 'w') as fil:
            json.dump(js, fil)
            
        with open(r'C:\Users\meetp\OneDrive\Desktop\Coding\Dotslash\Django\crimeRate\DataSet\result.json',  'r') as fp:
            india_geojson = json.load(fp)

        state_ut_crimes_df.reset_index(inplace=True)

        #Adding a id column in the state dataframe which as the same value for a particular as the GeoJSON as for that state.
        state_id_map = {}
        for feature in india_geojson["features"]:
            feature["id"] = feature["properties"]["ID_1"]
            state_id_map[feature["properties"]["NAME_1"]] = feature["id"]
            
        state_ut_crimes_df["id"] = state_ut_crimes_df['STATE/UT'].apply(lambda x: state_id_map[x])
        fig = px.choropleth(state_ut_crimes_df, geojson=india_geojson, locations='id', color= crime_name,
                           hover_name="STATE/UT", color_continuous_scale="Viridis",
                           hover_data=[crime_name],
                           title=' '.join([str(crime_name), 'cases in India(2001-2014)'])
                          )
        fig.update_geos(fitbounds="locations", visible=False)
        return fig
    
    
    def which_state_you_want_to_analyze(state_name):
        try:
            fig = px.pie(state_ut_crimes_df, values=state_ut_crimes_df.loc[state_name], 
            names=state_ut_crimes_df.iloc[0,:].index, title='Total Crime Rate Distribution for {}'.format(state_name))
            return fig
        except KeyError:
            print('You Entered Wrong STATE/UT Name')
            
    if request.method == 'POST':
        state = request.POST.get('state1')
        if state == "":
            category = int(request.POST.get('category'))
            print(category)
            plt_div = plot(plotmap(crime_dict[category]))
        else:
            print(state_ut_crimes_df.index)  # Print out the index values
            print(state.upper())
            plt_div = plot(which_state_you_want_to_analyze(state.upper()), output_type='div')
    else:
        plt_div = plot(plot_figure("Rape cases in India in 2001-2014","Rape","Cases of Rape in India", color='lightslategray'), output_type='div')
    return render(request,'crime.html',context={"plt_div":plt_div})
    # return render(request,'plot.html')