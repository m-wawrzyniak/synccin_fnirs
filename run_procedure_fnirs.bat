@echo off

cd /d "C:\Users\user\PycharmProjects\synccin_fnirs"
call .venv\Scripts\activate

python main_procedure.py

deactivate

pause
