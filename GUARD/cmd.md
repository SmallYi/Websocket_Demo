spark-submit --master spark://master:7077 --jars /home/zwh/TensorFlowOnSpark/examples/websocket/LSTM/spark-streaming-kafka-0-8-assembly_2.11-2.2.0.jar --py-files Encoder.py,/home/zwh/TensorFlowOnSpark/examples/websocket/configure_info.py,krspark.zip spark_guarddect.py modelname

