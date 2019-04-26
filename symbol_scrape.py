import pandas as pd
from string import ascii_lowercase

# Initialize dataframes for NYSE and NASDAQ symbols
NYSE_symbols = pd.Series([])
NASDAQ_symbols = pd.Series([])

for c in ascii_lowercase:
    # Create urls for scraping symbols
    NYSE_url = "http://eoddata.com/stocklist/NYSE/" + c + ".htm"
    NASDAQ_url = "http://eoddata.com/stocklist/NASDAQ/" + c + ".htm"
    # Extract tables from url
    NYSE_tables = pd.read_html(NYSE_url)
    NASDAQ_tables = pd.read_html(NASDAQ_url)
    # Add stock symbols dataframe
    NYSE_symbols = pd.concat([NYSE_symbols, NYSE_tables[4]['Code']])
    NASDAQ_symbols =  pd.concat([NASDAQ_symbols, NASDAQ_tables[4]['Code']])
# Save dataframes as CSV files
NYSE_symbols.to_csv("NYSE_symbols.csv", index=False)
NASDAQ_symbols.to_csv("NASDAQ_symbols.csv", index=False)
