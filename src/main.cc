#include <stdshit.h>
#include <win32hlp.h>
#include "resource.h"
#include "deflist.h"
#include "util.h"

const char progName[] = "windef-lookup";

static DefList s_defLst;
static HWND s_hList;


void loadFile(HWND hwnd, cch* file)
{
	if(file && s_defLst.load(file))
		contError(hwnd, "failed to load def list: %s\n", file);
}


void mainDlgInit(HWND hwnd, cch* file)
{
	loadFile(hwnd, file);
	
	s_hList = GetDlgItem(hwnd, IDC_LIST1);
	lstView_insColumn(s_hList, 0, 78, "Name");
	lstView_insColumn(s_hList, 1, 78, "Value");
}

void listViewInit(HWND hwnd, xarray<DefList::Def> lst)
{
	ListView_DeleteAllItems(s_hList);
	for(auto& x : lst) {
		int i = lstView_iosText(s_hList, -1, x.name);
		lstView_iosText(s_hList, i, 1, x.value);
	}
	
	lstView_autoSize(s_hList);
}



void nameEdtChange(HWND hwnd)
{
	char buff[100];
	GetDlgItemTextA(hwnd, IDC_NAME, buff, 100);
	auto list = s_defLst.find(buff);
	listViewInit(hwnd, list);
}

void valEdtChange(HWND hwnd)
{



}




BOOL CALLBACK mainDlgProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam)
{
	DLGMSG_SWITCH(
		ON_MESSAGE(WM_INITDIALOG, mainDlgInit(hwnd, (cch*)lParam))
		CASE_COMMAND(
			ON_COMMAND(IDCANCEL, EndDialog(hwnd, 0))
			ON_COMMAND(IDC_NAMECLR, SetWindowTextA(sender, ""))
			ON_COMMAND(IDC_VALCLR, SetWindowTextA(sender, ""))
			ON_CONTROL(EN_CHANGE, IDC_NAME, nameEdtChange(hwnd))
			ON_CONTROL(EN_CHANGE, IDC_VAL, valEdtChange(hwnd))
	  ,)
	,)
}	
	

int main(int argc, char** argv)
{
	cch* file = argv[1];
	if(!file) file = "windef.txt";
	DialogBoxParamW(NULL, MAKEINTRESOURCEW(IDD_DIALOG1), 
		NULL, mainDlgProc, (LPARAM)file);
}