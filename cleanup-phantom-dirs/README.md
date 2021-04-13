# Install
```
python3 -m venv ./venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

# Run
(assuming DSE is running locally)
python3 main.py

# Debugging
## Data doesn't match tables when testing
Make sure to flush tables to disk, using `nodetool flush`
