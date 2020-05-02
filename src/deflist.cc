#include <stdshit.h>
#include "deflist.h"

DefList::~DefList() {}
void DefList::close() { pRst(this); }

static
int compar(const DefList::Def& a, const DefList::Def& b) {
	return stricmp(a.name, b.name); }

int DefList::load(cch* file)
{
	close();

	// load the input file
	int nLines;
	char** lines = loadText(file, nLines);
	if(!lines) return 1;
	data.init(lines[0]);
	SCOPE_EXIT(free(lines));
	
	// parse the input file 
	for(int i = 0; i < nLines; i++) {
		char* space = strchr(lines[i], ' ');
		if(space) defLst.push_back(lines[i], space+1);
	} qsort(defLst.data, defLst.len, compar);
	
	return 0;
};


static
int findFn(cch* pkey, const DefList::Def& elem) {
	return strnicmp(pkey, elem.name, strlen(pkey)); }

xarray<DefList::Def> DefList::find(cch* prefix)
{
	// find matching string
	if(isNull(prefix)) return {};
	Def* found = bsearch((void*)prefix, defLst.data, defLst.len, findFn);
	if(!found) return {};
	
	// get all matches
	Def* end = found+1;
	while((end < defLst.end())&&(!findFn(prefix, *end))) end++;
	while((found > defLst.data)&&(!findFn(prefix, found[-1]))) found--;
	return {found, end};
}
