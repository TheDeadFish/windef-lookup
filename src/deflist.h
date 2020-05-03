#pragma once

struct DefList
{
	struct Val { s64 value; bool x64; };
	struct Def { cch* name; cch* value; cch* eval; 
		int getVal(u64& val) const; 
		bool cmp(u64 num) const;};
		
		
	
	int load(cch* file);
	void close();
	xarray<Def> find(cch* prefix);
	
	~DefList();

	xarray<Def> numFind(xarray<Def> in, u64 num);

private:
	xstr data;
	xArray<Def> defLst;
};

