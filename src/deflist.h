#pragma once

struct DefList
{
	struct Def { cch* name; cch* value; };
	int load(cch* file);
	void close();
	xarray<Def> find(cch* prefix);
	
	~DefList();
	
	
	
private:
	xstr data;
	xArray<Def> defLst;
};

