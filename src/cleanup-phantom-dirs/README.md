# Install
```
python3 -m venv ./venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

# Run
(assuming DSE is running locally)
```
python3 main.py
```

## Specifying hostname
By default, we will assume the output of `hostname -i` for a hostname for connecting to your cluster. If that doesn't work for you, make sure to send in arg

```
python3 main.py --hostname 123.456.678.123

```

# Debugging
## Data doesn't match tables when testing
Make sure to flush tables to disk, using `nodetool flush`

# TODOs
- Add docs to main c.toolkit docs pages, under [docs/operation](../../docs/operation/README.md)
