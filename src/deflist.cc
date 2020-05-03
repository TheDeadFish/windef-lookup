#include <stdshit.h>
#include "deflist.h"
#include "util.h"

DefList::~DefList() {
	for(auto* x : defLst) { free(x); } }
void DefList::close() { pRst(this); }

static
int compar(const DefList::Def*& a, const DefList::Def*& b) {
	return stricmp(a->name, b->name); }

int DefList::load(cch* file)
{
	// load input file
	close();
	data.init(loadText(file).data);
	if(!data) return 1;
	
	// parse input file
	for(char* pos = data; *pos;)
	{
		lpDef def = xCalloc(1);
		defLst.push_back(def);
		
		def->name = pos; pos += strlen(pos)+1;
		def->value = pos; pos += strlen(pos)+1;
		def->eval = pos; pos += strlen(pos)+1;
		if(*def->eval == 0) return 2; def->init();
		if(*pos == '\n') pos++;
	}
	
	qsort(defLst.data, defLst.len, compar);
	return 0;
};


static
int findFn(cch* pkey, const DefList::lpDef& elem) {
	return strnicmp(pkey, elem->name, strlen(pkey)); }

xarray<DefList::lpDef> DefList::find(cch* prefix)
{
	// find matching string
	if(isNull(prefix)) return defLst;
	lpDef* found = bsearch((void*)prefix, defLst.data, defLst.len, findFn);
	if(!found) return {};
	
	// get all matches
	lpDef* end = found+1;
	while((end < defLst.end())&&(!findFn(prefix, *end))) end++;
	while((found > defLst.data)&&(!findFn(prefix, found[-1]))) found--;
	return {found, end};
}

void DefList::Def::init()
{
	// get string value
	char* end;
	num = strtoui64(eval, &end);
	if(end == NULL) return;
	
	// check type
	if(toUpper(*end) == 'U') end++;
	if(!stricmp(end, "ll")) { type = 2; goto L1; }
	if(toUpper(*end) == 'L') end++; if(*end) return;
	type = 1; num &= 0xFFFFFFFF;
	L1: pcnt = __builtin_popcountll(num);
}

bool DefList::Def::cmp(u64 num) const
{
	if(type == 0) return false;
	if(type != 1) return num == this->num;
	return u32(num) == u32(this->num);
}

xarray<DefList::lpDef> DefList::numFind(xarray<lpDef> in, u64 num)
{
	xarray<lpDef> ret = {};
	for(auto* x : in) { 
		if(x->cmp(num)) ret.push_back(x); }
	return ret;
}

static
int compar_num(const DefList::lpDef& a, const DefList::lpDef& b) 
{
	IFRET(a->pcnt-b->pcnt);
	if(a->num < b->num) return -1; 
	return (a->num > b->num);
}

xarray<DefList::lpDef> DefList::numGet(xarray<lpDef> in)
{
	xarray<lpDef> ret = {}; u64 tmp;
	for(auto& x : in) if(x->type) ret.push_back(x); 
	qsort(ret.data, ret.len, compar_num); 
	return ret;	
}
