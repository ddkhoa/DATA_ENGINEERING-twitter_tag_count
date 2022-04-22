from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SQLContext, SparkSession
import sys
import requests
import os

os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

# function that calcul the sum across all the batches


def aggregate_tags_count(new_values, total_sum):
    # new_values: value of current batch
    # total_sum: the sum of previous batches
    return sum(new_values) + (total_sum or 0)


def get_sql_context_instance(spark_context):
    if('sqlContextSingletonInstance' not in globals()):
        globals()['sqlContextSingletonInstance'] = SQLContext(spark_context)

    return globals()['sqlContextSingletonInstance']


def send_df_to_dashboard(df):
    top_tags = [str(item.hashtag) for item in df.select("hashtag").collect()]
    tags_count = [item.hashtag_count for item in df.select("hashtag_count").collect()]
    url = "http://localhost:5001/updateData"
    request_data = {"label" : str(top_tags), "data": str(tags_count)}
    response = requests.post(url, data=request_data)


def process_rdd(time, rdd):
    print("---------- %s -------------" % str(time))
    try:
        sql_context = get_sql_context_instance(rdd.context)

        # convert RDD to Row RDD
        row_rdd = rdd.map(lambda hc: Row(hashtag=hc[0], hashtag_count=hc[1]))

        # create a DF from Row RDD
        hashtags_df = sql_context.createDataFrame(row_rdd)

        # register df as table
        hashtags_df.registerTempTable("hashtags")

        # query top 10 hashtags
        hashtag_counts_df = sql_context.sql(
            "SELECT hashtag, hashtag_count FROM hashtags ORDER BY hashtag_count DESC LIMIT 10")

        hashtag_counts_df.show()

        # send to dashboard to visualize top 10 hashtag
        send_df_to_dashboard(hashtag_counts_df)

    except:

        # we get some errors when the application runs
        # RDD is empty
        e = sys.exc_info()[1]
        print("Error %s" % e)


# Spark session
spark = SparkSession.builder.appName("TwitterStreamApp").getOrCreate()

# Spark context
sc = spark.sparkContext
sc.setLogLevel("ERROR")

# Spark streaming context, interval = 2 secs
ssc = StreamingContext(sc, 2)

ssc.checkpoint("checkpoint_TwitterApp")

# read data from port 9009 (twitter app)
dataStream = ssc.socketTextStream("localhost", 9009)

# Transformation logic
# [Line] -> [Word]
words = dataStream.flatMap(lambda line: line.split(" "))

# [Word] -> [(Word, Count)]
hashtags = words.filter(lambda w: "#" in w).map(lambda x: (x, 1))

# use updateStateByKey to maintain RDD state between batches
# if we use reduceByKey, it will reset the counter for each batch
tags_totals = hashtags.updateStateByKey(aggregate_tags_count)

tags_totals.foreachRDD(process_rdd)

ssc.start()
ssc.awaitTermination()
