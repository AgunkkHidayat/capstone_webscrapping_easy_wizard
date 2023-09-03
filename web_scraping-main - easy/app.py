from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/exchange-rate-history/usd-idr')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('tbody')
row = table.find_all('a',attrs={'class':'n'})

row_length = len(row)

temp = [] #initiating a list 

for i in range(0, row_length):
#insert the scrapping process here
    
	exchange = table.find_all('span',attrs={'class':'w'})[i].text
	exchange = exchange.strip()

	period = table.find_all('a',attrs={'class':'n'})[i].text
	period = period.strip()
	
	temp.append((period,exchange))
   
temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns = ('period','daily_exchange'))

#insert data wrangling here
df[['dollar','rupiah']]=df['daily_exchange'].str.split(' = ', expand=True)
df[['simbol_Rp','Nominal_Rupiah']]=df['rupiah'].str.split('Rp', expand=True)
df['Nominal_Rupiah']=df['Nominal_Rupiah'].str.replace(',','.')
df['Nominal_Rupiah']=df['Nominal_Rupiah'].astype('float64')
df['period']=df['period'].astype('datetime64[ns]')
df.drop(columns=['daily_exchange','dollar','rupiah','simbol_Rp'], inplace=True)
df = df.set_index('period')

#end of data wranggling 


@app.route("/")
def index(): 
	
	card_data = f'{df["Nominal_Rupiah"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)