import re, sys, os
import shutil
from subprocess import Popen, call, PIPE

build_base = 'R:/'


gcc_opts = ("-S -g0 -Os -fomit-frame-pointer -mno-accumulate-outgoing-args "
 "-mno-stack-arg-probe -mpreferred-stack-boundary=2 -fno-exceptions "
 "-fno-asynchronous-unwind-tables -DUNICODE -D_UNICODE")

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
	return match(str, r"^(0x[0-9A-Fa-f]+|-?[0-9]+)([uU]?[lL]{0,2})$")
	
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
	return [x.strip() for x in s.splitlines()]
	
def execute_cpp(str, args):
	proc = Popen('cpp -DUNICODE -D_UNICODE '+args, stdin=PIPE, stdout=PIPE,
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
	
def evalMacro(x):
	# skip non-number
	x[2] = strip_brace(x[2])
	if is_string(x[2]): return False;
	if is_ident(x[2]): return False;
	if is_brinit(x[2]): return False
	if x[2].find('__attribute__') >= 0:
		return;
	
	# handle number
	if is_number(x[2]):
		tmp = x[2].lower()
		if (tmp[-1] == 'l') and (tmp[-2] not in ['l','u']):
			x[2] = x[2][:-1]
		return False
	
	# preduce source file
	print x[0]
	with open('R:/tmpdef/%s.cc' % (x[0]), 'w') as f:
		f.write('#include "tmpdef.h"\n')
		f.write("void test() { get_value(%s); }" % (x[2]));
	return True
	
def evalAsmValue(push):
	try:
		iVal = long(push[0][1:]); uVal = iVal & 0xFFFFFFFF
		hexStr = '0x%X' % (uVal)
		if len(push) == 2: 
			iVal = uVal | (long(push[1][1:]) << 32)
			hexStr = '0x%X' % (iVal & 0xFFFFFFFFFFFFFFFF)
	except: return None
	return hexStr
		
def evalAsmParse2(str, push, call):
	
	int_types = {'j':'U', 'm':'Ul', 'x':'LL', 'y':'ULL'}

	# number type
	if str == None:
		val = evalAsmValue(push)
		if val == None: return None
		return val+int_types.get(call, '')
		
	# string type
	if call != 'PKw': return str
	return 'L"'+eval(str).replace('\0', '')+'"'
	
def evalAsmParse(name):
	# open asm file
	dir=build_base+'tmpdef/build/CMakeFiles/tmpdef.dir/'
	lines = []
	try:
		with open(dir+name, 'r') as f:
			lines = getLines(f.read())
	except: pass

	# parse asm file
	str = None;	push = []
	for line in lines:
		if line.startswith('.ascii "'):
			str = line[7:]; continue
		if line.startswith('pushl\t'):
			push.append(line[6:]); continue
		if line.startswith('call\t__Z9get_value'):
			line = line.split('@')[0][18:]
			return evalAsmParse2(str, push, line)
			break
	return None
	
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
	asm_list = []
	with open(dir+'/CmakeLists.txt', 'w') as f:
		f.writelines(cmake_lines)
		for x in mList: 
			if evalMacro(x):
				asm_list.append((x, '%s.cc.obj' % (x[0])))
				f.write('%s.cc\n' % (x[0]))
		f.writelines(cmake_lines2)
		
	# build asm output
	
	call('%CMAKE% ..', shell=True, cwd=dir+'/build')
	with open(dir+'/build/build.ninja', 'r+') as f:
		while True:
			pos = f.tell(); line = f.readline()
			if line.find('FLAGS') < 0: continue
			f.seek(pos); f.write(line.replace('-S', '  '))
			break
	call('ninja -k 99999', cwd=dir+'/build')
	
	# parse asm output
	for x in asm_list: 
		val = evalAsmParse(x[1])
		if val != None: x[0][2] = val
		
	
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
with open('../../bin/windef.txt', 'w') as f:
	for x in mList:
		f.write(x[0]+'\0'+x[1]+'\0'+x[2]+'\0\n')
