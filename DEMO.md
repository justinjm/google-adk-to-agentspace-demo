# DEMO

Steps to launch the app locally for demoing.

```sh
# oneliners to resume development or demo
cd src/data-science && source $(poetry env info --path)/bin/activate && poetry run adk web
poetry run adk web
```

## example chat questions

* Hi what can you help me with? and what data do you have access to?
* I need more details on the train table. What countries exist? How many stores are there?
* Please generate a plot from the train table of total sales per country, sort the plot as descending from left to right
* What kinds of forecasting models can I train in BQML?
* can you train an ARIMA\_PLUS model that forecasts total sales (num\_sold) by date ?
* using the model you just trained, can you generate a forecast for 30 days as well as the upper and lower confidence intervals in a timeseries plot?

```sql
SELECT forecast_timestamp, forecast_value, prediction_interval_lower_bound, prediction_interval_upper_bound FROM ML.FORECAST(MODEL `demos-vertex-ai.forecasting_sticker_sales.arima_plus_model`, STRUCT(30 AS horizon, 0.95 AS confidence_level))
```