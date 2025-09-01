@echo off

cd /d "C:\Users\Badania\PycharmProjects\synccin_fnirs"
call .venv\Scripts\activate

python main_procedure.py

deactivate

pause
