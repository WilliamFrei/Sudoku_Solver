
from dash import Dash, html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import numpy as np

from Main import solve_puzzle
from visualisation import draw_attempt

from io import BytesIO
import base64

app = Dash(__name__)

ENABLE_TEST = True

if ENABLE_TEST:
	from sudoku_examples import sdk_puzzles, sdk_filled
	test_givens = sdk_puzzles[2]
	test_entered = sdk_filled[2]

givens_table_rows = []
entered_table_rows = []
for y in range(9):
	g_row_elements = []
	e_row_elements = []
	for x in range(9):
		givens_input = dcc.Input(
			id=str(y * 9 + x),
			value='',
			type='text',
			minLength='0',
			maxLength='1',
			pattern='[1-9]?'
		)
		entered_input = dcc.Input(
			id=str(100 + y * 9 + x),
			value='',
			type='text',
			minLength='0',
			maxLength='1',
			pattern='[1-9]?'
		)
		
		if ENABLE_TEST:
			if test_givens[y,x] != 0:
				assert test_givens[y, x] == test_entered[y, x]
				givens_input.value = str(test_givens[y, x])
			if test_entered[y,x] != 0:
				entered_input.value = str(test_entered[y, x])
		
		g_row_elements.append(html.Td(givens_input))
		e_row_elements.append(html.Td(entered_input))
		
		@app.callback(
			Output(entered_input, component_property='value'),
			Output(entered_input, component_property='style'),
			Output(entered_input, component_property='disabled'),
			Input(givens_input, component_property='value'),
			State(entered_input, component_property='value'),
		)
		def update_output_div(input_value, entered_value):
			if input_value is not None and len(input_value) == 1 and '1' <= input_value <= '9':
				return input_value, {'backgroundColor':'#ccc'}, True
			elif entered_value is not None and len(entered_value) == 1 and '1' <= entered_value <= '9':
				return entered_value, {}, False
			else:
				return '', {}, False
	givens_table_rows.append(html.Tr(g_row_elements))
	entered_table_rows.append(html.Tr(e_row_elements))

app.layout = html.Div(children=[
	html.H1(children='Sudoku Solver'),
	html.Div(children=[
		html.Div(className='separator'),
		html.Div(children=[
			html.Div('enter the Sudoku puzzle\'s pre-filled numbers here'),
			html.Table(html.Tbody(givens_table_rows))], className='tableDiv'),
		html.Div(className='separator'),
		html.Div(className='separator'),
		html.Div(children=[
			html.Div('enter your (partial or complete) solution of the Sudoku here'),
			html.Table(html.Tbody(entered_table_rows))], className='tableDiv'),
		html.Div(className='separator')], className='splitscreen'),
	
	html.Button('check solution', id='submit-val', n_clicks=0, className='margined'),
	html.Div(className='margined', children=[html.Div(id='error_msg_div', className='error')]),
	html.Img(id='visualisation_output', src ='')
	
], className='baseDiv')

@app.callback(
	Output('error_msg_div', 'children'),
	Output('error_msg_div', 'style'),
	Output('visualisation_output', 'src'),
	Input('submit-val', 'n_clicks'),
	*[State(str(i), 'value')  for i in range(81)],
	*[State(str(100 + i), 'value')  for i in range(81)]
)
def update_output(n_clicks, *values):
	assert len(values) == 81 * 2
	
	# initial call without any data entered yet
	if n_clicks == 0:
		# neither an error message nor a figure to display
		return '', {'display': 'none'}, ''
	
	givens = values[:81]
	entered = values[81:]
	givens_arr = np.zeros((9,9), dtype=int)
	entered_arr = np.zeros((9,9), dtype=int)
	for i in range(81):
		y = i // 9
		x = i % 9
		g = givens[i]
		e = entered[i]
		if len(g) == 1 and '1' <= g <= '9':
			assert g == e
			givens_arr[y, x] = int(g)
		if len(e) == 1 and '1' <= e <= '9':
			entered_arr[y, x] = int(e)
	
	try:
		solution_arr = solve_puzzle(givens_arr) 
	except AssertionError:
		return 'Error: Sudoku puzzle has either more than one or zero solutions', {'backgroundColor':'#fd7070'}, ''
		
	fig = draw_attempt(givens_arr, entered_arr, solution_arr, return_fig=True)
	
	out_img = BytesIO()
	fig.savefig(out_img, format='png', bbox_inches='tight')
	
	fig.clf()
	
	out_img.seek(0)
	
	encoded = base64.b64encode(out_img.read()).decode("ascii").replace("\n", "")
	
	return 'correct and incorrect squares are colored green and red respectively', {}, f"data:image/png;base64,{encoded}"
	


if __name__ == '__main__':
	app.run_server(debug=True)

