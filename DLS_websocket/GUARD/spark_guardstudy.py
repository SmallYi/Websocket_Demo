#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
 Counts words in UTF8 encoded, '\n' delimited text received from the network every second.
 Usage: network_wordcount.py <hostname> <port>
   <hostname> and <port> describe the TCP server that Spark Streaming would connect to receive data.

 To run this on your local machine, you need to first run a Netcat server
    `$ nc -lk 9999`
 and then run the example
    `$ bin/spark-submit examples/src/main/python/streaming/network_wordcount.py localhost 9999`
"""
from __future__ import print_function

import sys
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

first=0
def Save(rdd,output,ssc):
  global first
  if not rdd.isEmpty():
      rdd.saveAsTextFile(output)
      first=1
  else:
     if first==1:
      ssc.stop()
  
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: spark_guardstudy.py <hostname> <port>", file=sys.stderr)
        exit(-1)
    modelname=sys.argv[1]
    output="output/"+modelname+"/"+modelname+".csv"

    sc = SparkContext(appName="spark_guardstudy")
    ssc = StreamingContext(sc, 30)
    brokers="master:2181,slave1:2181,slave2:2181"
    topic='GuardStudy'
    lines=KafkaUtils.createStream(ssc,brokers, "spark-streaming-consumer", {topic: 1})
    liner = lines.map(lambda x: x[1])
    liner.pprint()
    liner.foreachRDD(lambda rdd:Save(rdd,output,ssc))
    ssc.start()
    ssc.awaitTermination()
