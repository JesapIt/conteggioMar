import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from gspread import Cell
from datetime import date
import datetime
from PIL import Image



image = Image.open('jesap.png')

st.set_page_config(page_title='Conteggio Ore', page_icon = image, initial_sidebar_state = 'auto')
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive',
         'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/spreadsheets']

creds = ServiceAccountCredentials.from_json_keyfile_name('key_conteggio.json', scope)
client = gspread.authorize(creds)


st.markdown('## Area Marketing & Comunicazione')
st.markdown('### [Link google sheet](https://docs.google.com/spreadsheets/d/1aihHUw1Qk0p0PutBGolKT4umw_NXKVxuvrx2-o6bSnI/edit#gid=0)')


# --- Interfaccia ----
nome = st.text_input('Nome e/o Cognome')
data = st.date_input('Data', value=date.today())
data = data.strftime("%d/%m/%Y")
options = ['call', 'formazione', 'task', 'progetto', 'altro']
att = st.multiselect('Attività', options)
dictionary = {}
for a in att:
	n_ore = st.time_input(f'Numero di ore {a}', datetime.time(1, 0), key=a)
	dictionary[a] = n_ore


sub = st.button("Invia")


link_MC = "https://docs.google.com/spreadsheets/d/1aihHUw1Qk0p0PutBGolKT4umw_NXKVxuvrx2-o6bSnI/edit#gid=0"
sht = client.open_by_url(link_MC)
# -- Selecting current worksheet ---
if sub and nome != '':
	double = 0
	for w in sht.worksheets():
		lower_title = w.title.lower()
		lower_name = nome.lower()
		if lower_name in lower_title:
			double +=1
			current_work = w
	if double == 0:
		st.error('Nessuna risorsa trovata con questo nome/congome')

	elif double > 1:
		st.warning('Sono state trovate più risorse con questo nome/cognome, cerca di essre più specifico')
	else:
	# --- adding elements to google sheet ---
		def next_available_row(worksheet):
			str_list = list(filter(None, worksheet.col_values(1)))
			return str(len(str_list)+1)

		for a in att:
			row = next_available_row(current_work)
			c1 = Cell(int(row) , 1, str(data))
			c2 = Cell(int(row) , 2, a)
			c3 = Cell(int(row) , 3, str(dictionary[a]).replace(':', '.'))
			current_work.update_cells([c1,c2,c3], value_input_option='USER_ENTERED')
			#current_work.update_cell(row , 1, str(data))
			#current_work.update_cell(row , 2, a)
			#current_work.update_cell(row , 3, str(dictionary[a]).replace(':', '.'))


		st.success(f'Conteggio ore di {current_work.title} aggiornato')
	










