import re, sys, os
from subprocess import Popen, call, PIPE

gcc_opts = ("-g0 -Os -fomit-frame-pointer -mno-accumulate-outgoing-args "
 "-mno-stack-arg-probe -mpreferred-stack-boundary=2 -fno-exceptions "
 "-fno-asynchronous-unwind-tables")

def_types = [
	'__stdcall void get_value(int);',
	'__stdcall void get_value(long);',
	'__stdcall void get_value(unsigned long);',
	'__stdcall void get_value(unsigned int);',
	'__stdcall void get_value(long long);',
	'__stdcall void get_value(const char*);',
	'__stdcall void get_value(const wchar_t*);'
]

def match(str, reg):
	return bool(re.search(reg, str))	

def is_ident(str):
	return match(str, r"^[a-zA-Z_][a-zA-Z0-9_]*$")
	
def is_number(str):
	return match(str, r"^0x[0-9A-Fa-f]+$|^[0-9]+$")
	
def is_string(str):
	return match(str, r"^(L?\"(?:[^\"\\]|\\.)*\")*$|^(\'(?:[^\'\\]|\\.)*\')*$")

def strip_brace(str):
	tmp = str
	while (tmp[0] == '(') and (tmp[-1] == ')'):
		tmp = tmp[1:-1]
		if tmp.find('(') <= tmp.find(')'):
			str = tmp
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
	print defSet
	
	

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
	
def evalInit(mStr):
	with open('tmpdef.h', 'w') as f:
		f.write(mStr);
		f.writelines(def_types);
	call('gcc -x c++-header tmpdef.h ' + gcc_opts)
	os.remove('tmpdef.h')
	
def evalMacro(x):
	# skip non-number
	if x[1] == x[2]: return
	x[2] = strip_brace(x[2])
	if is_string(x[2]): return;
	if is_ident(x[2]): return;
	
	# handle number
	if is_number(x[2]): return;
	if x[2][-1] == 'l':
		if is_number(x[2][:-1]):
			x[2] = x[2][:-1]
			return
	
	# preduce source file
	with open('tmpdef.cc', 'w') as f:
		f.write('#include "tmpdef.h"\n')
		f.write("void test() { get_value(%s); }" % (x[1]));
		
	# compile source file
	result = call('gcc tmpdef.cc -S '  + gcc_opts)
	print result

def cookMacroList(mList, mStr):
	mListStr = mStr
	for x in mList: mListStr += x[0]+'\n'
	lines = execute_cpp(mListStr, '-P')
	assert len(mList) == len(lines)
	
	for i in range(len(mList)):
		mList[i][2] = lines[i]
		evalMacro(mList[i])

#
defFile = loadText("windef.cc")
evalInit(defFile)
mList = []
mStr = getMacroList(mList, defFile)
cookMacroList(mList, mStr)


"""
for x in mList:
	line = x[0]+'\0'+x[1]+'\0'+x[2]+'\0'
	print line
"""
