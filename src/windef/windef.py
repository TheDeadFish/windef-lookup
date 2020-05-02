import re, sys, os
import shutil
from subprocess import Popen, call, PIPE

build_base = 'R:/'


gcc_opts = ("-S -g0 -Os -fomit-frame-pointer -mno-accumulate-outgoing-args "
 "-mno-stack-arg-probe -mpreferred-stack-boundary=2 -fno-exceptions "
 "-fno-asynchronous-unwind-tables")

def_types = [
	'__stdcall void get_value(int);\n',
	'__stdcall void get_value(long);\n',
	'__stdcall void get_value(unsigned long);\n',
	'__stdcall void get_value(unsigned int);\n',
	'__stdcall void get_value(long long);\n',
	'__stdcall void get_value(unsigned long long);\n',
	'__stdcall void get_value(const void*);\n',
	'__stdcall void get_value(const char*);\n',
	'__stdcall void get_value(const wchar_t*);\n'
]

cmake_lines = [
	'project(tmpdef)\n', 
	'cmake_minimum_required(VERSION 3.16)\n',
	'add_compile_options(%s)\n' % (gcc_opts),
	'add_library(tmpdef OBJECT\n'
]

cmake_lines2 = [ ')\n', 
	'target_precompile_headers(tmpdef PUBLIC "tmpdef.h")\n'
]


def match(str, reg):
	return bool(re.search(reg, str))	
	
def is_brinit(str):
	x = str.strip();
	if len(x) and x[0] == '{':
		return True
	return False

def is_ident(str):
	return match(str, r"^[a-zA-Z_][a-zA-Z0-9_]*$")
	
def is_number(str):
	return match(str, r"^0x[0-9A-Fa-f]+$|^[0-9]+$")
	
def is_string(str):
	return match(str, r"^(L?\"(?:[^\"\\]|\\.)*\")*$|^(\'(?:[^\'\\]|\\.)*\')*$")


def brance_balence(str):
	level = 0
	for x in str:
		if (x == '"') or (x == "'"): 
			return False
		if x == '(': level += 1;
		if x == ')': level -= 1
		if level < 0: return False
	return level == 0

def strip_brace(str):
	tmp = str
	while (tmp[0] == '(') and (tmp[-1] == ')'):
		tmp = tmp[1:-1]
		if brance_balence(tmp): str = tmp
	return str
	

def getLines(s):
	return [x.rstrip() for x in s.splitlines()]
	
def execute_cpp(str, args):
	proc = Popen('cpp '+args, stdin=PIPE, stdout=PIPE,
		universal_newlines=True)
	proc.stdin.write(str);
	lines = proc.communicate()[0]
	return getLines(lines)
	
def loadText(name):
	with open(name, 'r') as f: 
		return f.read()

def getMacroList(mList, defFile):

	# get default defines
	defSet = set()
	for line in execute_cpp('', '-dM'):
		tok = line.split(' ', 2)
		defSet.add(tok[1])
		
	mStr = ""
	lines = execute_cpp(defFile, '-dM')	
	for line in lines:
		tok = line.split(' ', 2)
		if len(tok) < 3: continue
		if tok[1] in defSet: continue
		mStr += line+'\n'		
		if tok[1].find('(') >= 0: continue
		mList.append([tok[1], tok[2], None])
	return mStr;
	
def evalMacro(makeFile, x):
	# skip non-number
	if x[1] == x[2]: return
	x[2] = strip_brace(x[2])
	if is_string(x[2]): return;
	if is_ident(x[2]): return;
	if is_brinit(x[2]): return
	if x[2].find('__attribute__') >= 0:
		return;
	
	# handle number
	if is_number(x[2]): return;
	if x[2][-1] == 'l':
		if is_number(x[2][:-1]):
			x[2] = x[2][:-1]
			return
	
	# preduce source file
	print x[0]
	with open('R:/tmpdef/%s.cc' % (x[0]), 'w') as f:
		f.write('#include "tmpdef.h"\n')
		f.write("void test() { get_value(%s); }" % (x[2]));
	makeFile.write('%s.cc\n' % (x[0]))
	
def evalBuild(mList, mStr):

	# prepare directory
	dir=build_base+'tmpdef'
	try: 
		os.mkdir(dir)
		os.mkdir(dir+'/build')
	except: pass

	# generate tmpdef.h
	with open(dir+'/tmpdef.h', 'w') as f:
		f.write(mStr);
		f.writelines(def_types);
		
	# generate CmakeLists.txt
	with open(dir+'/CmakeLists.txt', 'w') as f:
		f.writelines(cmake_lines)
		for x in mList: evalMacro(f, x)
		f.writelines(cmake_lines2)
		
	# build
	call('%CMAKE% ..', shell=True, cwd=dir+'/build')
	with open(dir+'/build/build.ninja', 'r+') as f:
		while True:
			pos = f.tell(); line = f.readline()
			if line.find('FLAGS') < 0: continue
			f.seek(pos); f.write(line.replace('-S', '  '))
			break
	call('ninja -k 99999', cwd=dir+'/build')
	
def cookMacroList(mList, mStr):
	mListStr = mStr
	for x in mList: mListStr += x[0]+'\n'
	lines = execute_cpp(mListStr, '-P')
	assert len(mList) == len(lines)
	for i in range(len(mList)):
		mList[i][2] = lines[i]

defFile = loadText("windef.cc")
mList = []
mStr = getMacroList(mList, defFile)
cookMacroList(mList, mStr)
evalBuild(mList, defFile)




"""
for x in mList:
	line = x[0]+'\0'+x[1]+'\0'+x[2]+'\0'
	print line
"""
