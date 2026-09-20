# Fabric notebook (PySpark) - medallion starter. Attach a Lakehouse; `spark` is provided.
# Assumes mirrored/raw table `bronze_orders` exists. Adjust names to your schema.
from pyspark.sql import functions as F

bronze = spark.read.table("bronze_orders")

silver = (bronze
    .dropDuplicates(["order_id"])
    .withColumn("order_date", F.to_date("order_date"))
    .filter(F.col("order_id").isNotNull())
    .withColumn("_ingested_at", F.current_timestamp()))
silver.write.mode("overwrite").format("delta").saveAsTable("silver_orders")

gold = (silver.groupBy("order_date")
    .agg(F.count("*").alias("orders"), F.sum("amount").alias("revenue")))
gold.write.mode("overwrite").format("delta").saveAsTable("gold_daily_revenue")
