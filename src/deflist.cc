#include <stdshit.h>
#include "deflist.h"
#include "util.h"

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
	if(isNull(prefix)) return defLst;
	Def* found = bsearch((void*)prefix, defLst.data, defLst.len, findFn);
	if(!found) return {};
	
	// get all matches
	Def* end = found+1;
	while((end < defLst.end())&&(!findFn(prefix, *end))) end++;
	while((found > defLst.data)&&(!findFn(prefix, found[-1]))) found--;
	return {found, end};
}


int DefList::Def::getVal(u64& val) const
{
	// get string value
	char* end;
	val = strtoui64(eval, &end);
	if(end == NULL) return 0;
	
	// check type
	if(toUpper(*end) == 'U') end++;
	if(!stricmp(end, "ll")) return 2;
	if(toUpper(*end) == 'l') end++;
	val &= 0xFFFFFFFF; return *end ? 0 : 1;
}

bool DefList::Def::cmp(u64 num) const
{
	u64 val;
	u32 type = getVal(val);
	if(type == 0) return false;
	if(type != 1) return num == val;
	return u32(num) == u32(val);
}

xarray<DefList::Def> DefList::numFind(xarray<Def> in, u64 num)
{
	xarray<Def> ret = {};
	for(auto& x : in) { 
		if(x.cmp(num)) ret.push_back(x); }
	return ret;
}
