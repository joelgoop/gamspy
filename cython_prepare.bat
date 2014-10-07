SETLOCAL EnableDelayedExpansion
CALL "C:\Program Files\Microsoft SDKs\Windows\v7.0\Bin\SetEnv.cmd" /x64 /release
SET INCLUDE="C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\include";"C:\Program Files\Microsoft SDKs\Windows\v7.0\Include";"C:\"
SET LIB="C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\lib\amd64";"C:\Program Files\Microsoft SDKs\Windows\v7.0\Lib\x64";
set MSSdk=1
set DISTUTILS_USE_SDK=1