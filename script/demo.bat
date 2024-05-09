set LANG=en_US

echo "Usage -- run as .\script\demo.bat"
@echo off

REM Find current path to install
set scriptdir=%~dp0
set scriptdir=%scriptdir:~0,-1%
set basedir=%scriptdir%\..
set logconf=%scriptdir:\=/%
set XP=%basedir%

logging_args="-Dlogback.configurationFile=%basedir%\etc\logback.xml"
xponents_args="-Xmx500m -Xms500m"

java %xponents_args% %logging_args% -cp "%XP%\etc;%XP%\lib\*" ^
  org.codehaus.groovy.tools.GroovyStarter --main groovy.ui.GroovyMain ^
  %XP%\script\XponentsCore.groovy  %*
  
pause
