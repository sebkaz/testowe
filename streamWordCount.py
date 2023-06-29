
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split

if __name__ == "__main__":
    spark = SparkSession.builder.appName("Stream_DF").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    lines = (spark
         .readStream
         .format("socket")
         .option("host", "localhost")
         .option("port", 9999)
         .load())

    words = lines.select(explode(split(lines.value, " ")).alias("word"))
    word_counts = words.groupBy("word").count()

    streamingQuery = (word_counts
         .writeStream
         .format("console")
         .outputMode("complete")
         .trigger(processingTime="5 second")
         .start())

    streamingQuery.awaitTermination()
         
         
