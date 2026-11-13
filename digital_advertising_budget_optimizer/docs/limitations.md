# System Limitations & Boundary Conditions
## Digital Advertising Budget Optimizer

1. **Synthetic Data Realism Boundaries:**
   Synthetic records model Poisson click arrivals and log-normal impressions calibrated to industry benchmarks. However, real-world advertising features sudden external macroeconomic shocks, ad-fatigue decay, competitor bidding wars, and day-of-week seasonality not fully captured by static distributional priors.

2. **Last-Touch vs Multi-Touch Attribution:**
   The current reporting model uses direct-touch attribution (attributing sales to the immediate channel record). In enterprise multichannel customer journeys, users often discover a product on TikTok, search on Google, and convert via Instagram retargeting. Multi-Touch Attribution (MTA) with Markov Chains is outlined as a future enhancement.

3. **Single-Node Execution Environment:**
   While the Big Data Lab accurately simulates the MapReduce programming model and runs Spark in local standalone mode, benchmarking on a single Windows laptop does not measure physical network shuffle latencies that occur across multi-rack physical Hadoop clusters.

4. **Resource Constraints on 10M Records:**
   Loading 10,000,000 records simultaneously into an in-memory Pandas DataFrame requires approximately 8–12 GB of free physical RAM. On machines with limited memory, users must utilize the streaming/chunked generation option and MapReduce processor to prevent memory saturation.

