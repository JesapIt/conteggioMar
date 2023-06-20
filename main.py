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
link_MC = "https://docs.google.com/spreadsheets/d/1aihHUw1Qk0p0PutBGolKT4umw_NXKVxuvrx2-o6bSnI/edit#gid=0"
sht = client.open_by_url(link_MC)


# funzione al click del bottone
def fun():
	st.session_state.multi = []
	if nome != '':
		if not temp_att:
			st.warning('Inserire almeno un\'attività')
			return
		double = 0
		double_inprova = 0
		for w in sht.worksheets():
			lower_title = w.title.lower()
			index_inprova = lower_title.find("- socio in prova")
			if (index_inprova >= 0):
				lower_title = lower_title[0:index_inprova-1]
			lower_name = nome.lower()
			if lower_name in lower_title:
				if (index_inprova >= 0):
					double_inprova += 1
					work_inprova = w
				else:
					double += 1
					work = w
		if double == 0 and double_inprova == 0:
			st.error('Nessuna risorsa trovata con questo nome/cognome')
			return
		if double > 1 and (not in_prova):
			st.warning('Sono state trovate più risorse con questo nome/cognome, cerca di essre più specifico.')
			return
		if double_inprova > 1 and (in_prova):
			st.warning('Sono state trovate più risorse in prova con questo nome/cognome, cerca di essre più specifico.')
			return
		else:
			if in_prova: 
				if double_inprova == 0:
					st.error('Non è stata trovata nessuna risorsa corrispondente ai criteri di ricerca')
					return
				elif double_inprova == 1:
					current_work = work_inprova
			elif (not in_prova):
				if double == 0:
					st.error('Non è stata trovata nessuna risorsa corrispondente ai criteri di ricerca')
					return
				elif double == 1:
					current_work = work
		# --- adding elements to google sheet ---
			def next_available_row(worksheet): #funzione
				str_list = list(filter(None, worksheet.col_values(1))) #fa la lista delle colonne del worksheet scegliendo un elemento non vuoto
				return str(len(str_list)+1) #va a prendere il prossimo elemento, che sarà vuoto

			for a in temp_att:
				row = next_available_row(current_work)
				if int(row) > (len(current_work.get_all_values())-1):
					current_work.append_row(["", "", ""])
				c1 = Cell(int(row) , 1, str(data))
				c2 = Cell(int(row) , 2, a)
				c3 = Cell(int(row) , 3, str(dictionary[a]).replace(':', '.'))
				current_work.update_cells([c1,c2,c3], value_input_option='USER_ENTERED')

			st.success(f'Conteggio ore di {current_work.title} aggiornato')
	else:
		st.warning('Inserire un nome e/o cognome')
	return

# --- Interfaccia ----
nome = st.text_input('Nome e/o Cognome. Se Socio in prova, spunta la checkbox relativa')
in_prova = st.checkbox('Socio in Prova')
data = st.date_input('Data', value=date.today())
options = ['Call d\'area', 'Assemblea mensile', 'Delega', 'Recruiting', 'Mentoring', 'Progetto esterno'
,'Progetto interno', 'Formazione', 'Call con HR buddy', 'Case study', 'Organizzazione area', 'Altro', 'Task interno', 'Evento', 'Revisione Task', 'Creazione contenuti social', 'Video editing', 'Interviste', 'Board Resp/Resp Vice']

att = st.multiselect('Attività', options, key="multi")
dictionary = {}
temp_att = []
for a in att:
	if a == "Progetto esterno":
		### estrazione nomi progetti in corso
		prog_link = "https://docs.google.com/spreadsheets/d/1-bXwTiVfxFYbFKHCeJyocKIKCQsn0ZIK4Kq7Q8A9ND8/edit#gid=1224600023"		
		prog_spread_sht = client.open_by_url(prog_link)
		prog_sht = prog_spread_sht.get_worksheet(7)

		column_b = prog_sht.col_values(2)  # Column B is index 2
		column_d = prog_sht.col_values(4)  # Column D is index 4

		column_e = prog_sht.col_values(5)

		progetti_in_corso = []
		for name, value, state in zip(column_b, column_d, column_e):
			if value.lower() == 'in corso' and state.lower() == 'progetto esterno':
				progetti_in_corso.append(name)
		### fine estrazione
		sel_prog = st.selectbox("Selezionare il progetto", progetti_in_corso)
		if sel_prog:
			temp_att.append('Progetto esterno - ' + sel_prog)
			n_ore = st.time_input(f'Numero di ore: {sel_prog}', datetime.time(1, 0), key=sel_prog+'1')
			dictionary['Progetto esterno - ' + sel_prog] = n_ore

	else:
		temp_att.append(a)
		n_ore = st.time_input(f'Numero di ore: {a}', datetime.time(1, 0), key=a)
		dictionary[a] = n_ore

data = data.strftime("%d/%m/%Y")
sub = st.button("Invia",on_click=fun)

# Font: Nunito, colore bottone blu
m = st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@200;300;400&display=swap');
html, body, [class*="css"]  {
	font-family: 'Nunito', sans-serif; 
	text-color: "#ffffff";
}
div.stButton > button:first-child {
    background-color: #2e9aff;
    border-color: #2e9aff;
}
header.css-1avcm0n, section {
	background-color: rgba(89, 55, 146, 0.8);
}
</style>""", unsafe_allow_html=True)










