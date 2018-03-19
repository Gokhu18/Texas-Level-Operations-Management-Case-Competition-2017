import os 
import pandas as pd
from geolocation.main import GoogleMaps
from geolocation.distance_matrix.client import DistanceMatrixApiClient

#google_maps = GoogleMaps(api_key='AIzaSyDYgz9eU5Ek9kmnNNz5mFzmumqVqmBpcMA')
google_maps = GoogleMaps(api_key='AIzaSyADi0QelZUXUVdtSTFvPCedYa2bk7qopm')
FILE_NAME="OMCC2017Final (2).xlsx"
FILE_NAME_CLEANED=("cleaned.csv")
HEIGHT_LIMIT=(13*12)+5
WIDTH_LIMIT=(8*12)+6

class Trailer:

    def __init__(self,name,axle,trailer_length,trailer_height,front_deck=False,rear_deck=False,front_deck_dimension=[],rear_deck_dimension=[]):
        self.name=name
        self.axle=axle+2
        self.trailer_length=trailer_length
        self.trailer_height=trailer_height
        self.trailer_width=self.feet_to_inches(8,6)
        self.trailer_capacity=0
        self.front_deck=front_deck
        self.rear_deck=rear_deck
        self.Length_fitting=False
        self.Width_Fitting=False
        self.Capacity_Fitting=False
        self.Height_Fitting=False
        self.remaining_length=0
        self.OVER_WIDTH=False
        self.OVER_HEIGHT=False
        self.product_picked=[]
        self.cost=0
        
        if self.front_deck:
            self.front_deck_length=front_deck_dimension[0]
            self.front_deck_height=front_deck_dimension[1]
        if self.rear_deck: 
            self.rear_deck_length=rear_deck_dimension[0]
            self.rear_deck_height=rear_deck_dimension[1]
    def feet_to_inches(self,feet,inches):
        return(feet*12+inches)
    def get_length(self):
        return(self.trailer_length)
    def get_height(self):
        return(self.trailer_height)
    def get_capacity(self):
        return(self.axle*15000)
    
    
def read_cleaned_file(file_name):
    df_cleaned=pd.read_csv(file_name)
    df_cleaned['Location']=df_cleaned['Source_City']+','+df_cleaned['Source_State']
    #df_cleaned['Distance']=df_cleaned['Location'].map(lambda x:google_maps.distance(x, ['DALLAS,TX'])[0].distance.miles)
    df_cleaned['Destination']=df_cleaned['Destination_city']+','+df_cleaned['Destination_State']
    #print df_cleaned[df_cleaned['Location']=='CHICAGO,IL']['Destination']
    df_cleaned['Distance']=df_cleaned['Location'].map(lambda x:google_maps.distance(x, df_cleaned[df_cleaned['Location']==x]['Destination'])[0].distance.miles)
    df_cleaned['Product']=df_cleaned['Product'].str.strip("\r\n")
    return(df_cleaned)

def find_trailer(trailers,df,file_name):
    df['Picked']=False
#    cities=(df['Source_City']+','+df['Source_State']).tolist()
#    cities.append('DALLAS,TX')
#    cities_df=pd.DataFrame(index=cities,columns=cities)
#    for city in cities:
#        for city2 in cities:
#            distance=google_maps.distance(city, city2)[0].distance.miles
#            cities_df.loc[city,city2]=distance
#    cities_df.to_csv('cities_distance.csv')
##    for index,row in cities_df.iterrows():
#        print(index,row)
#        break
    for trailer in trailers:
        df[trailer.name]=0
        df[trailer.name+'_extra_axle']=0
        df[trailer.name+'_default_axle']=trailer.axle
        df[trailer.name+'_OVER_HEIGHT']=trailer.OVER_HEIGHT
        df[trailer.name+'_OVER_WIDTH']=trailer.OVER_WIDTH
        
    for index,row in df.iterrows():
        df_current=row
#        print(row)
    
        for trailer in trailers:
            axle=0
            cost=trailer.cost
            if trailer.get_length()>=df_current['Length(Inches)']:
                trailer.Length_Fitting=True
                trailer.remaining_length=trailer.get_length()-df_current['Length(Inches)']
                if (trailer.get_capacity()+axle*15000)>=df_current['Weight']:
                    trailer.Capacity_Fitting=True
                else:
#                    print(trailer.get_capacity(),df_current['Weight'])
                    while((trailer.get_capacity()+axle*15000)<df_current['Weight']):
#                        print(trailer.get_capacity(),df_current['Weight'])
                        axle+=1
#                        print(trailer.axle)
                        cost+=2000
                if trailer.trailer_width>=df_current['Width(Inches)']:
                    trailer.Width_Fitting=True
                    trailer.OVER_WIDTH=False
                else:
                    trailer.OVER_WIDTH=True
                    trailer.Width_Fitting=False
                if trailer.get_height()+df_current['Height(Inches)']<161:
                    trailer.Height_Fitting=True
                    trailer.OVER_HEIGHT=False
                else:
                    trailer.OVER_HEIGHT=True
                    trailer.Height_Fitting=False
                trailer.product_picked.append(df_current.Product)
                cost+=calculate_cost(trailer,df_current)

                df.loc[df['Source_City']==df_current['Source_City'],[trailer.name]]=cost
                print(trailer.axle)
                df.loc[df['Source_City']==df_current['Source_City'],[trailer.name+"_default_axle"]]=trailer.axle
                df.loc[df['Source_City']==df_current['Source_City'],[trailer.name+"_extra_axle"]]=axle
                df.loc[df['Source_City']==df_current['Source_City'],[trailer.name+"_OVER_HEIGHT"]]=trailer.OVER_HEIGHT
                df.loc[df['Source_City']==df_current['Source_City'],[trailer.name+"_OVER_WIDTH"]]=trailer.OVER_WIDTH
               
        df.loc[df['Source_City']==df_current['Source_City'],'Picked']=True
        df.to_csv('cost.csv')

def calculate_cost(trailer,df):
    cost=0
    df_permit=pd.read_excel(FILE_NAME,sheetname='OTR PERMIT TABLE',header=0,skiprows=2,names=['STATE','ST','OVER WIDTH','OVER HEIGHT']).dropna()
    df_routepd=pd.read_excel(FILE_NAME,sheetname='Route',header=0).dropna()
    if trailer.name=='Trailer1':
        cost=float(df['LINE HAUL/mile'])*float(df['Distance'])    
    elif trailer.name=='Trailer2' or trailer.name=='Trailer3':
        cost=float((1.15*df['LINE HAUL/mile']))*float(df['Distance'])
    else:
        cost=float((1.20*df['LINE HAUL/mile']))*float(df['Distance'])    
    route=df_routepd.loc[df_routepd['SOURCE'] == df['Source_City']]
    routes=route.ROUTE.to_string(index=False).split(',')
    if trailer.OVER_HEIGHT:
        
        for state in routes:
            
            cost+=df_permit[df_permit['ST']==state]['OVER HEIGHT'].iloc[0]
            
    if trailer.OVER_WIDTH:
        for state in routes:
            cost+=df_permit[df_permit['ST']==state]['OVER WIDTH'].iloc[0]
    return cost


if __name__=='__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    trailer_48=Trailer('Trailer1',2,48*12,58)
    trailer_53=Trailer('Trailer1',2,53*12,58)
    trailer_drop=Trailer('Trailer2',2,(43*12)+6,39,front_deck=True,front_deck_dimension=[(9*12)+6,61])
    trailer_double_drop_2=Trailer('Trailer3',2,(30*12),24,front_deck=True,rear_deck=True,front_deck_dimension=[(9*12)+6,72],rear_deck_dimension=[(9*12),43])
    trailer_double_drop_3=Trailer('Trailer3',3,(30*12),24,front_deck=True,rear_deck=True,front_deck_dimension=[(9*12)+6,72],rear_deck_dimension=[(13*12)+6,43])
    trailer_high_tonnage_6=Trailer('Trailer4',6,(60*12),26,front_deck=True,rear_deck=True,front_deck_dimension=[(23*12)+6,62],rear_deck_dimension=[(24*12),62])
    trailer_high_tonnage_9=Trailer('Trailer4',9,(60*12),26,front_deck=True,rear_deck=True,front_deck_dimension=[(23*12)+6,62],rear_deck_dimension=[(24*12),62])
    trailers=[trailer_48,trailer_53,trailer_drop,trailer_double_drop_2,trailer_double_drop_3,trailer_high_tonnage_6,trailer_high_tonnage_9]


    df=read_cleaned_file(os.path.join(dir_path,FILE_NAME_CLEANED))

    find_trailer(trailers,df,FILE_NAME)
        
      