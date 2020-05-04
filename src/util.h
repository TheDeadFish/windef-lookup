#pragma once
void lstView_autoSize(HWND hList, int iCol);
void lstView_autoSize(HWND hList);
u64 strtoui64(cch* str, char** end);

#define XARRAY_FILTER(xa, ...) ({ \
	auto* _wrPos_ = xa.data; for(auto& x : xa) { \
		__VA_ARGS__;  *_wrPos_ = x; _wrPos_++; } \
	xa.setend(_wrPos_); })
