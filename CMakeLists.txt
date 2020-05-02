project(win32-res-lib)
cmake_minimum_required(VERSION 3.12)
set( EXECUTABLE_OUTPUT_PATH ../bin)

add_executable(windef-lookup 
	src/resource.rc
	src/deflist.cc
	src/main.cc
	src/util.cc
)
	
	
target_link_libraries(windef-lookup -lwin32hlp -lexshit 
	-lstdshit)
