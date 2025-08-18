# DEMO

Steps to launch the app locally for demoing and sample questions.

```sh
# oneliner to resume development or demo
cd src/data-science && source $(poetry env info --path)/bin/activate && poetry run adk web
```

## example chat questions

* Hi, What data do you have access to?
* I need more details on the train table. What countries exist? How many stores are there?
* Please generate a plot with total sales per country of the train table
* What kinds of forecasting models can I train in BQML?
* Can you train an ARIMA_PLUS model that forecasts total sales (num_sold) by date ?
* Using the model you just trained, can you generate a forecast for 30 days as well as the upper and lower confidence intervals in a time series plot?

Example query to generate a forecast:

```sql
SELECT 
    forecast_timestamp, 
    forecast_value, 
    prediction_interval_lower_bound, 
    prediction_interval_upper_bound 
FROM 
    ML.FORECAST(
        MODEL `demos-vertex-ai.forecasting_sticker_sales.arima_plus_model`, 
        STRUCT(30 AS horizon, 0.95 AS confidence_level)
    )
```