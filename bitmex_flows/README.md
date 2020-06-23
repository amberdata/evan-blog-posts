# BitMEX Inflow Outflow
## Setup
If you have not already, please create a file `.env` which contains your Amberdata API key. It should look like this:  
```
AMBERDATA_API_KEY=your_key
```

You should make a list of the addresses you would like to see with the format:
| Address                            |
|------------------------------------|
| 3BitMEXqEQeUPUTsATaEPv1AwrgogtegB1 |
|...                                 | 

in `input/addresses_all.csv`.

## Usage
You can then run the analysis with:
```
python src/main.py --n-addresses 500
```
where `n-addresses` specifies how many addresses you would like to include in the analysis.
