# simple-extract-app
A simple extract app for learning python&amp;pyqt  
Extract all the 7z/zip/tgz/gz compressed package within a folder,and delete the compressed package.  

* call_extract.py  
    > call_extract.py is the main file of this project, support a windows form application to execute function like select a folder,select the compressed type,extract file,delete compressed package. 

* ui.ui
    > The ui file generated by QtDesigner.

* ui.py
    > The interface transfer from ui.ui by pyuic.

* extract.py
    > extract.py include all the extract and delete folder function.

You can easily make the .exe file use pyinstaller,an example:  
pyinstaller -F (-i pixel_extract.ico) call_extract.py (-w)
