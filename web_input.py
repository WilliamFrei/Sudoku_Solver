
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


test_sudoku = np.zeros((9,9), dtype=int)

test_sudoku[0,0] = 6
test_sudoku[0,2] = 5
test_sudoku[0,6] = 3
test_sudoku[1,1] = 2
test_sudoku[1,2] = 7
test_sudoku[1,4] = 1
test_sudoku[2,4] = 7
test_sudoku[2,5] = 8
test_sudoku[2,8] = 9
test_sudoku[3,3] = 9
test_sudoku[3,6] = 6
test_sudoku[3,7] = 4
test_sudoku[4,0] = 7
test_sudoku[4,8] = 2
test_sudoku[5,1] = 9
test_sudoku[5,2] = 6
test_sudoku[5,5] = 4
test_sudoku[6,0] = 5
test_sudoku[6,3] = 1
test_sudoku[6,4] = 8
test_sudoku[7,4] = 4
test_sudoku[7,6] = 2
test_sudoku[7,7] = 1
test_sudoku[8,2] = 4
test_sudoku[8,6] = 9
test_sudoku[8,8] = 8

print(test_sudoku)

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
		
		if test_sudoku[y,x] != 0:
			givens_input.value = str(test_sudoku[y,x])
		
		g_row_elements.append(html.Td(givens_input))
		e_row_elements.append(html.Td(entered_input))
		
		@app.callback(
			Output(entered_input, component_property='value'),
			Output(entered_input, component_property='style'),
			Output(entered_input, component_property='disabled'),
			Input(givens_input, component_property='value')
		)
		def update_output_div(input_value):
			if input_value is not None and len(input_value) == 1 and '1' <= input_value <= '9':
				return input_value, {'backgroundColor':'#ccc'}, True
			else:
				return '', {}, False
	givens_table_rows.append(html.Tr(g_row_elements))
	entered_table_rows.append(html.Tr(e_row_elements))

app.layout = html.Div(children=[
	html.H1(children='Sudoku Input'),
	html.Div(children=[
		html.Div(className='separator'),
		html.Table(html.Tbody(givens_table_rows)),
		html.Div(className='separator'),
		html.Div(className='separator'),
		html.Table(html.Tbody(entered_table_rows)),
		html.Div(className='separator')], className='splitscreen'),
	
	html.Button('Submit', id='submit-val', n_clicks=0, className='margined'),
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
		return 'Error: Sudoku puzzle has either more than one or zero solutions', {}, ''
		
	fig = draw_attempt(givens_arr, entered_arr, solution_arr, return_fig=True)
	
	out_img = BytesIO()
	fig.savefig(out_img, format='png')
	
	fig.clf()
	
	out_img.seek(0)
	
	encoded = base64.b64encode(out_img.read()).decode("ascii").replace("\n", "")
	
	return '', {'display': 'none'}, f"data:image/png;base64,{encoded}"
	


if __name__ == '__main__':
	app.run_server(debug=True)

