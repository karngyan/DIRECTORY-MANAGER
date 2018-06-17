#! python3

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State

import tree,os
import plotly.graph_objs as go

''' 
	Functions for making pies
'''
def folder_pie(folders):
	return dcc.Graph(
		id = 'folder-pie',
		figure = go.Figure(
			data = [
				go.Pie(
					labels = folders[0],
					values = folders[1],
					hoverinfo = 'label+percent'
				)

			],
			layout = go.Layout(
				title = f'Directories Distribution',
			)

		)
	)

def file_pie(files):
	return dcc.Graph(
		id = 'file-pie',
		figure = go.Figure(
			data = [
				go.Pie(
					labels = files[0],
					values = files[1],
					hoverinfo = 'label+percent'
				)

			],
			layout = go.Layout(
				title = f'File Distribution',
			)

		)
	)

def file_type_pie(file_types):
	return dcc.Graph(
		id = 'file-type-pie',
		figure = go.Figure(
			data = [
				go.Pie(
					labels = list(file_types.keys()),
					values = list(file_types.values()),
					hoverinfo = 'label+percent'
				)
			],
			layout = go.Layout(
				title = f'File type distribution (Excluding sub-directories)'
			)
		)
	)


'''
	Utility Functions
'''
def readable(size):
    size = int(size)
    power = 2**10
    n = 0
    D = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /=  power
        n += 1
    if (n==0):
    	return str(size) + ' bytes'
    else :
    	return str(size)+' '+ D[n]+'B'

def setup_tree(path):

	folder = tree.Tree(path)

	try:
		folder.make_tree()
	except OSError as e:
		return html.Div([

			html.H4(f'Location: {path}'),

			html.Label(f'{e}: Permission Denied'),
		])

	folders = folder.get_folders()
	files = folder.get_files()
	file_types = folder.get_file_types()

	folders = folder.get_folders()

	dropdown_options = []
	
	for subFolder in folders[0]:
		dropdown_options.append(
			{
				'label': f'Folder: {subFolder}', 'value': os.path.join(path,subFolder) 
			}
		)

	for file in files[0]:
		dropdown_options.append(
			{
				'label': f'File: {file}', 'value': os.path.join(path,file) 
			}
		)

	folders[0].append('_Other Files_')
	folders[1].append(sum(files[1]))

	return html.Div([

		html.H4(f'Location: {path}'),
		html.Label(f'Total Size of directory: {readable(folder.total_size())}'),

		dcc.Dropdown(
			id = 'my-dropdown',
		    options=dropdown_options,
		    placeholder = 'Select a sub-folder or file... '
		),
		html.Div(
			id = 'sub-folder-size'
		),
		html.Br(),
		folder_pie(folders),
		html.Hr(),
		file_type_pie(file_types),
		html.Hr(),
		file_pie(files)


	])




#initialize app
app = dash.Dash()

#external css style sheet
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

#Multiple Callback Exceptions
app.config['suppress_callback_exceptions']=True


'''
	Layout
'''
app.layout = html.Div(children = [

		html.Label('Enter the path of the folder: '),
		dcc.Input(
			id = 'input-state',
			type = 'text', 
			value = '', 
			placeholder = 'Path(Folder)...',
			style = { 'width': '100%'}
		),
		html.Button(id = 'submit-button', n_clicks = 0, children = 'Submit'),

		html.Div(
			id = 'pies-dropdown'
		)

	]
)

@app.callback(
	Output('pies-dropdown', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('input-state', 'value')]
)
def update_pie(n_clicks, path):
	return setup_tree(path)

@app.callback(
	Output('sub-folder-size','children'),
	[Input('my-dropdown','value')]	
)
def show_size(path):
	return html.Div([
			html.Label(
				f'Path of sub-folder/file: {path}'
			),
			html.Label(
				f'Size : {readable(tree.size(path))}'	
			),
			html.Label(
				'Note: Copy Paste the path and hit submit to see the distribution.'
			)
		])

'''
	Run Server
'''

if __name__ == '__main__':
	app.run_server(debug = True)

