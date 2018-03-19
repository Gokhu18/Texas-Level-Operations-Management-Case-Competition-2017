import pandas as pd
#data_df=pd.read_csv('OMCC2017Final.xlsx','r',sheetname = 'RAIL LANE RATES')
#data_df=data_df.drop(['id'],1)
xls = pd.ExcelFile('OMCC2017Final.xlsx')
df1 = xls.parse('RAIL LANE RATES')
df1.info()

from geolocation.main import GoogleMaps 
from geolocation.distance_matrix.client import DistanceMatrixApiClient
origins1 = ['CHICAGO,IL'] 
destination1_1 = ['AURORA,IL']
destination1_2 = ['JOLIET,IL']
origins2 = ['INDIANAPOLIS,IN']
destination2_1 = ['BLOOMINGTON,IN']
destination2_2 = ['CARMEL,IN']
origins3 = ['SAN ANTONIO,TX']
destination3_1 = ['DALLAS,TX']

google_maps = GoogleMaps(api_key='AIzaSyDYgz9eU5Ek9kmnNNz5mFzmumqVqmBpcM')

dis1 = google_maps.distance(origins1, destination1_1).all()
dis2 = google_maps.distance(destination1_1, destination1_2).all()
dis3 = google_maps.distance(origins2, destination2_1).all()
dis4 = google_maps.distance(destination2_1, destination2_2).all()
dis5 = google_maps.distance(origins3, destination3_1).all()
for item in dis1:
    d1 = (float(item.distance.miles) * 1.58)
for item in dis2:
    d1 += (float(item.distance.miles) * 0.99)
for item in dis3:
    d2 = (float(item.distance.miles) * 1.58)
for item in dis4:
    d2 += (float(item.distance.miles) * 1.32)
for item in dis5:
    d3 = (float(item.distance.miles) * 1.38)
    
print d1 + 1612.00 + d3
print d2 + 1520.00 + d3
