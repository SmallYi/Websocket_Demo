from kafka import KafkaProducer
class Kafka_producer():
  def __init__(self,kafkaservers,kafkatopic):
     self.producer=KafkaProducer(bootstrap_servers=kafkaservers)
     self.kafkatopic=kafkatopic

  def senddata(self,data):
     try:
       self.producer.send(self.kafkatopic,data)
     except KafkaError as e:
       print(e)
