## About project
- I followed the tutorial [here](https://www.toptal.com/apache/apache-spark-streaming-twitter) to create my first application in data-engineering domain. Because there are some changes in 3rd libraries (TwitterAPI, Spark, Charts.js) since the author wrote the article, I adapted my code to make it worked.

- There is 3 components :
    - An ingestion layer that pull tweets stream using Twitter API, then send data to the processing layer
    - The processing layer is implemented using Spark. We use SparkStreaming component to process the data stream. The program counts the tags (#) from tweets, sorts them in descending order to find the most popular tags on Twitter. Finally, the program sends aggregated data to the presentaion layer to display
    -  The presentation layer is an simple web app implemented by FlaskAPI in the backend, HTML/JS in the frontend, Charts.js to draw the graph

## Run project
- You must have Hadoop/Spark installed on your machine. You can follow the instruction [here](https://phoenixnap.com/kb/install-spark-on-windows-10)
- You create your Twitter accounts and get the BEARER_TOKEN
- Open 3 terminals, then run the commands below:

In terminal 1:
```
cd ingestion
python twitter_app.py --twitter_bearer_token=YOUR_TWITTER_BEARER_TOKEN
```
   
In terminal 2: 

```
cd processing
python process.py
```

In terminal 3:
```
cd dashboard
python app.py
```

- Then open your browser and goto: http://localhost:5001 to see the chart :)