

# Cassandra Vision - TableAnalyzer
Make sure to use pip3 / python3. Needs pandas, statistics for analysis tool 

## prerequisities
- pandas
- statistics
- xlsxwriter 
- openpyxl

Install using `pip3 install -r requirements.txt` `pip install -r requirements.txt`

## How to use

1. In the home directory, in a folder `config`, create the file `environments.yaml` if it does not yet exist using a copy of `environments-sample.yaml`
2. In the home directory, in a folder `keys`, add pem files needed to ssh into each node to be analyzed - reference these in your `environments.yaml`
3. Run `cfstats.receive.py region cluster datacenter` to get table data from a specific datacenter (see `environments.yaml`)
4. Run `cfstats.transform.py region cluster datacenter` to transform the retrieved data into json, csv, and xlsx files
5. Run `csv2formattedxls.py data/region/cluster/region.cluster.cfstats.pivot.csv data/region/cluster/region.prod.cfstats.xlsx` to pivot the data into a formatted excel file 


## environments.yaml

```
us:
  prod:
    cassandra:
      - 192.168.0.1
      - 192.168.0.2
      - 192.168.0.3
    spark:
      - 192.168.0.4
    key: keyfile.pem
  prod2:
    cassandra:
      - 192.168.0.11
      - 192.168.0.12
      - 192.168.0.13
    spark:
      - 192.168.0.14
    key: keyfile.pem 
  stage:
    cassandra:
      - 192.168.1.1
      - 192.168.1.2
      - 192.168.1.3
    spark:
      - 192.168.1.4
    key: keyfile.pem 
region:
  cluster:
    datacenter:
```



## Credits

1. Rahul Singh - Concept, Initial Version
2. Tom Hada - Refactoring, Code Cleanup
3. Rohan Bane - Refactoring, Dockerization, Gridview Start
4. Jagannath Bilgi - Refactoring, Testing
5. Shridhar Nandeshwar - Testing, User Feedback
6. Senthilvel Palaniappan - Testing, User Feedback
7. Ameer Ajmal Baig - Testing, User Feedback