### NBP Currency exchanger with API

1. At the start, the application connects to the API of the **[National Bank of Poland](https://www.nbp.pl/Kursy/KursyA.html)**, downloads the current exchange rates and stores them in a local database.

2. At the beginning we enter:
- amount and name of the currency we want to exchange
- the name of the currency we want to convert to 
- the date of the exchange rate

3. Each exchange is saved to a *'.json'* file and automatically uploaded to an **[AWS s3 Bucket](https://aws.amazon.com/s3/)**. 
4. You need to enter your AWS access passwords in credentials.py