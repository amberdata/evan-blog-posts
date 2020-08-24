# Large Transactions in the Mempool
Author: Evan Azevedo

## Setup
If you would like to clone this repository and try it for yourself, please head over to the parent repo `evan-blog-posts` and clone it there. These scripts were written in Python version 3.7. You can install the required packages for ingesting the data with:  

```pip3 install websockets python-dotenv requests```.   

## Usage
For the analysis notebooks, other packages are required. The data collection script is called by:  

```python3 src/whale_watching.py```.   

You can edit the minimum transaction size in `src/config.py`.