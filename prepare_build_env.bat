SET ORIGINAL_PATH=%PATH%
CALL "C:\Program Files\Microsoft SDKs\Windows\v7.0\Bin\SetEnv.cmd" /x64 /release /win7
:: Reset LIB and INCLUDE with correct folders (for some reason set incorrectly from SetEnv)
SET INCLUDE="C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\include";"C:\Program Files\Microsoft SDKs\Windows\v7.0\Include";
SET LIB="C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\lib\amd64";"C:\Program Files\Microsoft SDKs\Windows\v7.0\Lib\x64";
:: Tell distutils to use SDK
SET DISTUTILS_USE_SDK=1
:: Add original PATH since SetEnv destroys it
SET PATH=%PATH%;%ORIGINAL_PATH%