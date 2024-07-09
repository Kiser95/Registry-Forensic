set “dest_folder=E:\temp\%COMPUTERNAME%
md “%dest_folder%”
cd /d%~dp0 
KAPE\kape.exe ‑tsource C: ‑tdest%dest_folder% ‑target RegistryHivesOther,RegistryHivesSystem,RegistryHivesUser