#include <stdshit.h>
#include "deflist.h"

DefList::~DefList() {}
void DefList::close() { pRst(this); }

static
int compar(const DefList::Def& a, const DefList::Def& b) {
	return stricmp(a.name, b.name); }
	
	

	

int DefList::load(cch* file)
{
	// load input file
	close();
	data.init(loadText(file).data);
	if(!data) return 1;
	
	// parse input file
	for(char* pos = data; *pos;)
	{
		cch* name = pos; pos += strlen(pos)+1;
		cch* val = pos; pos += strlen(pos)+1;
		cch* eval = pos; pos += strlen(pos)+1;
		if(*eval == 0) return 2;
		defLst.push_back(name, val, eval);
		if(*pos == '\n') pos++;
	}
	
	qsort(defLst.data, defLst.len, compar);
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
