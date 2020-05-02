#pragma once

struct DefList
{
	struct Def { cch* name; cch* value; cch* eval; };
	
	int load(cch* file);
	void close();
	xarray<Def> find(cch* prefix);
	
	~DefList();
	
	
	
private:
	xstr data;
	xArray<Def> defLst;
};

