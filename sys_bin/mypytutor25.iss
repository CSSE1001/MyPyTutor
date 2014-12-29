; -- mypytutor25.iss --
[Setup]
AppName=MyPyTutor
AppVerName=MyPyTutor version 0.1
AppCopyright=Copyright C 2009 Peter Robinson
DefaultDirName=c:\Program Files\MyPyTutor
DefaultGroupName=MyPyTutor
OutputBaseFilename=MyPyTutor25_setup

[files]
Source: "MyPyTutor.pyw"; Destdir: "{app}"
Source: "tutorlib\*.pyc"; Destdir: "{app}\tutorlib"

