import os
import shutil
import sys
import re
import argparse
from subprocess import run


png_o_modes = {'min' : '-o7', 'medium' : '-o4', 'max' : '-o7', 'normal': '-o2'}
default_output_dir = 'optiall_output'

def validate_format(file, format):
	return file.endswith(tuple(format.split('|')))

def get_files_by_format(format, exceptions):
	if exceptions is None:
		exceptions = []
	return [f for f in os.listdir() if validate_format(f, format) and f not in exceptions]


def validate_exceptions(exceptions):
	wrong_files = []
	for f in exceptions:
		print('trying file' + f)
		if f not in os.listdir() or not validate_format(f, 'jpg|jpeg|png'):
			wrong_files.append(f)
	return wrong_files


def create_HTML(files, opti_dir):

	def generate_rows():
		rows = ''
		for f in files:
			rows += '<tr><td><img src="' + f + '"></td><td><img src="'+ os.path.join(opti_dir, f) +'"></td></tr>\n'
		return rows


	f = open('optiWebView.html', 'w')

	message = """
<!DOCTYPE html>
<html>
<head>
	<title>optiAll Web Visualizer</title>
	<style>
		td img {
		  display: block;
		  max-width: 600px;
		}
	</style>
</head>
<body>
	<table style="width: 100%;">
		<tr>
			<th>Original</th>
			<th>Optimized</th>		
		</tr>
		
		"""+generate_rows()+"""
		
	</table>
</body>
</html>
	"""	

	f.write(message)
	f.close()


def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('-m', '--mode', dest="mode", choices=['min', 'normal', 'medium', 'max'], \
						default="normal", help="Mode of PNG optimization. Default = normal")

	parser.add_argument('-e', '--exceptions', dest="exceptions", nargs='*', \
						metavar='', help="List of images to not include")

	parser.add_argument('-d', '--dir', dest="dir", nargs=1, metavar="path", help="Write output files to path direcotry.")

	parser.add_argument('-wv', '-webview', dest="webview", action="store_true", help="Generates an HTML visualion before/after of your images.")
	
	args = parser.parse_args()

	
	# validate exceptions
	if args.exceptions is not None:
		wrong_files = validate_exceptions(args.exceptions)
		if len(wrong_files) > 0:
			exit('The following files are invalid: '+ str(wrong_files))
		
	
	# creates directory for optimized files	
	dir_output_option = [[''],['']]
	directory = ''
	if args.dir is not None:
		if args.dir[0] == default_output_dir:
			exit('You should not use this folder name')
		directory = str(args.dir[0])
		dir_output_option = [['-d', directory], ['-dir', directory]]
		if directory not in os.listdir():
			os.mkdir(directory)

	elif args.webview:
		directory = default_output_dir 
		dir_output_option = [['-d', directory], ['-dir', directory]]
		if directory not in os.listdir():		
			os.mkdir(directory)

	
	# define paramaters from external programs
	mode = png_o_modes[args.mode]
	jpgs_to_optim = get_files_by_format('jpg|jpeg', args.exceptions)
	pngs_to_optim = get_files_by_format('png', args.exceptions)
	
	# RUN EXTERNAL PROGRAMS
	if len(jpgs_to_optim):
		run(['jpegoptim'] + ['--strip-all'] + jpgs_to_optim + ['-f'] + ['-o'] + dir_output_option[0])

	if len(pngs_to_optim):
		run(['optipng'] + [mode] + ['-nb'] + ['-clobber'] +  dir_output_option[1] + pngs_to_optim + ['-strip all']) 


	# just to remove the bak files left by optiPng 'issue'
	for f in pngs_to_optim:
		try:			
			os.remove(os.path.join(os.getcwd(), directory, f) + '.bak')
		except:
		    pass


	if args.webview: 
		create_HTML(jpgs_to_optim + pngs_to_optim, directory)	



if __name__ == '__main__':
	main()