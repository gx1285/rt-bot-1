python3 -m pip install -r requirements.txt
git clone https://github.com/RextTeam/rt-lib
mv rt-lib rtlib
cd ./rtlib && python3 -m pip install -r requirements.txt
cd ./common && python3 make_key.py
cd ../../ && mv rtlib/common/secret.key ./
