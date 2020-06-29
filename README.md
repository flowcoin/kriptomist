# Kriptomist
**Python3 Framework for Crypto-Currency Price Prediction using Fundamental Analysis.**

![Bitcoin price, supply with reddit subscribers, Tether supply, transactions squared, difficulty and hashrate](https://i.imgur.com/CridKuT.png)

Author:
- Jure V. `<jure42@protonmail.com>`

### Base metrics
- price (in USD and BTC)
- supply
- subreddit subscribers
- twitter followers
- transaction count
- mining difficulty
- hashrate

### Derived metrics
- daily, weekly and monthly change in subscribers/followers
- price prediction based on current price change versus subscriber/follower count change


## Setup
To setup and play with `Kriptomist` we recommend using the **IPython** shell.

### Requirements
- Install required Python modules:

      pip install -r requirements.txt

### Database
- Download the [coin SQLite database](https://bit.ly/31fv8CX) and save it to `db/db.sqlite`
  
  **OR**
  
  Run `db.py` to create an empty database.
  
## Usage
Using IPython, you can run scripts using `run` IPython command. The advantage is that you keep the global namespace in the shell after the script was executed.

### Updating data for the current day
    In [1]: run kriptomist.py

This populates the database with (reddit, twitter, ...) data at the time the command was executed.
It also outputs 2 HTML files: 
- `html/table_{day}.html` (all coins)
- `html/binance_table_{day}.html` (only coins traded on Binance are listed here)

### Setting NUM_COINS
The default number of coins to process is initialy set to 10. To process more coins, create a file named `local_config.py` and specify number of coins you want to process:

    NUM_COINS = 5000

The maximum value for `NUM_COINS` is 5000.

### Displaying chart for a specific coin
    In [1]: run kriptomist.py bitcoin

Once you've looked at the html table and want to analyze a specific coin (in this case - bitcoin), you can run the above command (replace bitcoin with the name of your chosen coin).

### Customizing chart metrics
Copy the following to `local_config.py` and comment/uncomment desired metrics:

    CHART_METRICS = [
        # Price in USD
        'usd',
        # Price in BTC
        'btc',
        # Circulating supply
        'supply',
        # Subreddit subscribers
        'subs',
        # Twitter followers
        'flw',
        # BTC/USD
        'btcusd',
        # 28 day moving average
        #'ma28',
        # 100 day moving average
        #'ma100',
        # COIN/USD daily price change
        #'xusddiff',
        # BTC/USD daily price change
        #'btcusddiff',
        # BTC/USD correlation to COIN/USD
        #'btcusdxusdcorr',
        # BTC/USD correlation to COIN/BTC
        #'btcusdxbtccorr',
        # COIN/USD next day correlation to BTC/USD
        #'xusdnextdaycorrbtc',
        # COIN/USD prev day correlation to BTC/USD
        #'xusdprevdaycorrbtc',
        # Tether supply
        'tethersupply',
        # Daily transaction count
        'ntx',
        # Daily transaction count squared
        'ntxsquared',
        # Mining difficulty
        'difficulty',
        # Mining hashrate
        'hashrate',
    ]
