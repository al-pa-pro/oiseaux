@echo off
cd "C:\Users\alexa\Documents\informatique\htlm_css\oiseaux_afrique_subsaharienne\.oiseau\Scripts\"
call activate
cd "C:\Users\alexa\Documents\informatique\htlm_css\oiseaux_afrique_subsaharienne\services\"
python pipeline_ETL.py > pipeline_ETL.log 2>&1
