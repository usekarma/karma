package io.karma.normalizer;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.*;
import java.util.Properties;

public final class NormalizerApp {
  public static void main(String[] args) {
    final Properties p = new Properties();
    p.put(StreamsConfig.APPLICATION_ID_CONFIG, System.getenv().getOrDefault("APPLICATION_ID","karma-normalizer"));
    p.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, env("KAFKA_BOOTSTRAP", "localhost:9092"));
    p.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, StreamsConfig.EXACTLY_ONCE_V2);
    p.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
    p.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());

    final StreamsBuilder b = new StreamsBuilder();
    final Mapping mapping = Mapping.fromYaml(System.getenv("MAPPING_PATH"), "/mapping.yml");

    KStream<String,String> in = b.stream(env("INPUT_TOPIC","cdc.raw"), Consumed.with(Serdes.String(), Serdes.String()));
    KStream<String,String> out = in
      .mapValues(mapping::normalize)
      .filter((k,v) -> v != null);

    out.to(env("OUTPUT_TOPIC","events.normalized"), Produced.with(Serdes.String(), Serdes.String()));
    final KafkaStreams streams = new KafkaStreams(b.build(), p);
    streams.start();
    Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
  }

  private static String env(String k, String d){ String v = System.getenv(k); return v == null || v.isBlank() ? d : v; }
}
