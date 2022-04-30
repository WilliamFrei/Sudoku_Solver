
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

# fill out the Sudoku grids with a pre-defined Sudoku from 'sudoku_examples' to show the functionality without having to enter a Sudoku manually
ENABLE_TEST = True

# if 'ENABLE_TEST' then load the test-Sudoku here
if ENABLE_TEST:
	from sudoku_examples import sdk_givens, sdk_filled
	test_givens = sdk_givens[2]
	test_entered = sdk_filled[2]

# the rows of the Sudoku (as html table elements, each row is a <tr>)
givens_table_rows = [] # the givens (numbers already filled out at the beginning)
entered_table_rows = [] # the numbers filled in by the person solving the Sudoku
for y in range(9):
	g_row_elements = [] # a single 'givens' row, with 9 <td> table cells
	e_row_elements = []
	for x in range(9):
		# a text input field to enter a number, an <input> html element
		givens_input = dcc.Input(
			id='givens_' + str(y * 9 + x),
			value='', # initially empty
			type='text',
			minLength='0',
			maxLength='1',
			pattern='[1-9]?' # this pattern allows the empty sequence (='') or up to 1 digit from 1 to 9
		)
		entered_input = dcc.Input(
			id='entered_' + str(y * 9 + x),
			value='',
			type='text',
			minLength='0',
			maxLength='1',
			pattern='[1-9]?'
		)
		
		# if 'ENABLE_TEST' then fill the input elements with the values from the loaded Sudoku
		if ENABLE_TEST:
			if test_givens[y,x] != 0:
				assert test_givens[y, x] == test_entered[y, x]
				givens_input.value = str(test_givens[y, x])
			if test_entered[y,x] != 0:
				entered_input.value = str(test_entered[y, x])
		
		# populate the rows with <td>s containing the <input>s
		g_row_elements.append(html.Td(givens_input))
		e_row_elements.append(html.Td(entered_input))
		
		# a callback for when a field in the 'givens' Sudoku grid is changed
		# when this happens, the change is carried over to the 'entered' Sudoku grid
		@app.callback(
			Output(entered_input, component_property='value'), # the first return parameter: a value of an input in the 'entered' Sudoku grid
			Output(entered_input, component_property='style'), # second return parameter: a style (a disabled input is greyed out)
			Output(entered_input, component_property='disabled'), # third parameter: boolean to disable the input
			Input(givens_input, component_property='value'), # input parameter, the corresponding value of the 'givens' Sudoku grid
			State(entered_input, component_property='value'), # another input parameter, the value of the input in the 'entered' Sudoku grid
			State(entered_input, component_property='disabled'), # third parameter, whethere that input is disabled
		)
		def update_output_div(givens_value, entered_value, entered_disabled):
			# basic sanity checks
			assert givens_value is not None # as the value is initialized with '', None should not be possible as an value
			assert entered_value is not None # dito
			assert 0 <= len(givens_value) <= 1 # the input-regex should only allow the empty string or digits from 1 to 9
			
			# if there is a number from 1 to 9 entered in a 'givens' input
			if len(givens_value) == 1:
				assert '1' <= givens_value <= '9' # only numbers from 1 to 9 should pass the regex check of the input (see above)
				# then this input is carried over to the corresponding 'entered' input, and the latter is disabled and colored in gray
				return givens_value, {'backgroundColor':'#ccc'}, True
			# else, if the 'givens' input was blanked out and the 'entered' input had been bound to the same value earlier (and thus disabled)
			elif len(givens_value) == 0 and entered_disabled:
				# then empty the 'entered' input field to and enable it
				return '', {}, False
			# the last case only happens at the beginning if 'ENABLE_TEST'==True, because 'update_output_div' is once called for each input after initialization
			# when this happens, the 'givens_value' is blank and also the 'entered' input is enabled
			elif len(givens_value) == 0 and not entered_disabled:
				# in this case the 'entered_value' should be left unchanged
				return entered_value, {}, False
			else:
				# the 3 ifs above should be exhaustive, if we end up here something went wrong
				assert False, f"{givens_value}, {entered_value}, {entered_disabled}"
		
	# create the html <tr> elements
	givens_table_rows.append(html.Tr(g_row_elements))
	entered_table_rows.append(html.Tr(e_row_elements))

# the html structure of the web page
# the corresponding css file is found at assets/table.css
app.layout = html.Div(children=[
	html.H1(children='Sudoku Solver'),
	html.Div(children=[
		html.Div(children=[
			html.Div('Enter the Sudoku puzzle\'s pre-filled numbers here:'),
			html.Table(html.Tbody(givens_table_rows))], className='tableDiv'), # the 'givens' grid
		html.Div(children=[
			html.Div('Enter your (partial or complete) solution of the Sudoku here:'),
			html.Table(html.Tbody(entered_table_rows))], className='tableDiv'), # the 'entered' grid
		], className='splitscreen'), # the grids are displayed horizontally next to each other
	
	html.Button('Check Solution', id='submit-val', n_clicks=0, className='margined'),
	html.Div(className='margined', children=[html.Div(id='error_msg_div', className='error')]),
	html.Img(id='visualisation_output', src ='')
	
], className='baseDiv')

# callback for when the 'Check Solution' button is pressed
@app.callback(
	Output('error_msg_div', 'children'), # div output (text)
	Output('error_msg_div', 'style'), # style (used to hide the div or color its background)
	Output('visualisation_output', 'src'), # an image to be shown
	Input('submit-val', 'n_clicks'), # the number the button has been clicked (mostly irrelevant, but this input leads to the function being called)
	*[State('givens_' + str(i), 'value')  for i in range(81)], # the input values of the 'givens' grid
	*[State('entered_' + str(i), 'value')  for i in range(81)] # the input values of the 'entered' grid
)
def update_output(n_clicks, *values):
	assert len(values) == 81 * 2 # basic sanity check, there should be 9x9x2 values
	
	# initial call without any data entered yet
	if n_clicks == 0:
		# neither an error message nor a figure to display
		return '', {'display': 'none'}, ''
	
	# separate given and entered values
	givens = values[:81]
	entered = values[81:]
	# convert them into numpy arrays
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
		# try solving the Sudoku puzzle presented by the 'givens'
		solution_arr = solve_puzzle(givens_arr) 
	except AssertionError:
		# assertion error if there isn't exactly one solution
		return 'Error: Sudoku puzzle has either more than one or zero solutions.', {'backgroundColor':'#fd7070'}, ''
	
	# otherwise the givens/entered arrays are drawn, with the correct/incorrect entries of the entered array being colored green and red respectively
	fig = draw_attempt(givens_arr, entered_arr, solution_arr, return_fig=True)
	
	# save the figure as a virtual file
	out_img = BytesIO()
	fig.savefig(out_img, format='png', bbox_inches='tight')
	
	fig.clf()
	
	
	# encode that file in base 64
	out_img.seek(0)
	encoded = base64.b64encode(out_img.read()).decode("ascii").replace("\n", "")
	
	# present it to the user
	return 'Correct and incorrect squares are colored green and red respectively:', {}, f"data:image/png;base64,{encoded}"
	


if __name__ == '__main__':
	app.run_server(debug=True)

