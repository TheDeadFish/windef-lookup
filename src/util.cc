#include <stdshit.h>
#include <win32hlp.h>

	
void lstView_autoSize(HWND hList, int iCol)
{
	ListView_SetColumnWidth(hList, iCol, LVSCW_AUTOSIZE_USEHEADER);
	int headSize = ListView_GetColumnWidth(hList, iCol);
	ListView_SetColumnWidth(hList, iCol, LVSCW_AUTOSIZE);
	int bodySize = ListView_GetColumnWidth(hList, iCol);
	if(bodySize < headSize)
		ListView_SetColumnWidth(hList, iCol, headSize);
}

void lstView_autoSize(HWND hList)
{
	int nItem = ListView_GetItemCount(hList);
	for(int i = 0; i < nItem; i++)
		lstView_autoSize(hList, i);
}

u64 strtoui64(cch* str, char** end)
{
	int base = 10;
	if(strScmp(str, "0x")) { str += 2; base = 16; }
	u64 val = _strtoui64(str, end, base);
	if(str == *end) *end = NULL;
	return val;
}
