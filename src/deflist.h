#pragma once

struct DefList
{
	struct Val { s64 value; bool x64; };
	struct Def { cch* name; cch* value; cch* eval; 
		char type; char pcnt; u64 num; void init(void);		
		bool cmp(u64 num) const; 
	};
	
	typedef Def* lpDef;
	
	int load(cch* file);
	void close();
	
	
	xarray<lpDef> find(char* str);
	
	
	
	
	~DefList();
	
	

	xarray<lpDef> numFind(xarray<lpDef> in, u64 num);
	xarray<lpDef> numGet(xarray<lpDef> in);

private:
	xarray<lpDef> find_(cch* prefix);
	xstr data;
	xArray<lpDef> defLst;
};

