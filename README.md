# Kriptomist
Analyzing flow in the world of crypto.

Base metrics:
- price
- subreddit subscribers

Derived metrics:
- daily, weekly and mothly change in subscribers
- price prediction based on current price change versus subscriber count change

[Fetcher]
- text_handler function, which if ret value is false, considers the request to be failed
- if request fails, try again, sleeping 2-times more than the previous time
- if request succeeds, reduce sleeping by a factor of 2
- cache functionality, using read_cache and write_cache parameters

[Coinmarketcap]
- make sure the data is there, fill zeroes if necessary

[Subredditstats]
- make sure the data is there, fill zeroes if necessary

