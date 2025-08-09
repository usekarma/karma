package io.karma.normalizer;

import com.fasterxml.jackson.databind.*;
import com.fasterxml.jackson.databind.node.*;
import com.fasterxml.jackson.dataformat.yaml.*;
import java.nio.file.*;
import java.time.OffsetDateTime;

public final class Mapping {
  private final ObjectMapper M = new ObjectMapper();
  private final JsonNode cfg;

  private Mapping(JsonNode cfg){ this.cfg = cfg == null ? M.createObjectNode(): cfg; }

  public static Mapping fromYaml(String envPath, String classpathFallback){
    try {
      ObjectMapper yaml = new ObjectMapper(new YAMLFactory());
      if (envPath != null && Files.exists(Path.of(envPath)))
        return new Mapping(yaml.readTree(Files.readString(Path.of(envPath))));
      return new Mapping(yaml.readTree(Mapping.class.getResourceAsStream(classpathFallback)));
    } catch (Exception e){ return new Mapping(null); }
  }

  public String normalize(String raw){
    try {
      JsonNode change = M.readTree(raw);
      String db = change.at("/ns/db").asText("");
      String coll = change.at("/ns/coll").asText("");
      JsonNode map = match(db, coll);
      JsonNode doc = change.at("/fullDocument");
      String op = text(change.path("operationType"), "event");
      String eventType = overrideEventType(map, change, op);

      ObjectNode out = M.createObjectNode();
      out.put("ts", iso(text(change.path("clusterTime"), null)));
      String entity = text(doc.path("_id"), "");
      out.put("event_type", eventType);
      out.put("entity_id", entity);
      out.put("correlation_id", text(change.at("/documentKey/_id"), entity));
      out.set("tags", extractFields(map.get("tags"), doc));
      out.set("attrs", extractAttrs(map.get("attrs"), change));
      out.put("idempotency_key", "mongo:" + entity + ":" + op + ":" + text(change.path("clusterTime"), ""));

      ObjectNode source = M.createObjectNode();
      ObjectNode ns = M.createObjectNode(); ns.put("db", db); ns.put("coll", coll);
      source.put("system","mongo"); source.set("ns", ns);
      out.set("source", source);

      return M.writeValueAsString(out);
    } catch(Exception e){ return null; }
  }

  private JsonNode match(String db, String coll){
    for (JsonNode m : cfg.path("mappings")) {
      if (db.equals(m.at("/match/ns.db").asText()) && coll.equals(m.at("/match/ns.coll").asText())) return m;
    }
    return M.createObjectNode();
  }

  private String overrideEventType(JsonNode map, JsonNode change, String fallback){
    JsonNode ovr = map.get("event_type_override");
    if (ovr == null) return fallback;
    String when = text(ovr.get("when"), "");
    if (when.startsWith("$eq(")){
      String[] ab = args(when.substring(4, when.length()-1));
      if (val(ab[0], change).equals(val(ab[1], change))) return text(ovr.get("value"), fallback);
      return text(ovr.get("else"), fallback);
    }
    return fallback;
  }

  private String text(JsonNode n, String d){ return n == null || n.isMissingNode() || n.isNull() ? d : n.asText(d); }

  private String val(String token, JsonNode root){
    token = token.trim();
    if (token.startsWith("'") && token.endsWith("'")) return token.substring(1, token.length()-1);
    if (token.contains(".")) return root.at("/" + token.replace(".", "/")).asText("");
    return token;
  }

  private String[] args(String s){ int i = s.indexOf(','); return i<0? new String[]{s,""}: new String[]{s.substring(0,i), s.substring(i+1)}; }

  private String iso(String t){ try { return t == null || t.isBlank() ? OffsetDateTime.now().toString() : OffsetDateTime.parse(t).toString(); } catch(Exception e){ return OffsetDateTime.now().toString(); } }

  private ObjectNode extractFields(JsonNode fields, JsonNode doc){
    ObjectNode o = M.createObjectNode();
    if (fields == null || !fields.isArray()) return o;
    for (JsonNode f : fields) {
      String k = f.asText(); JsonNode v = doc.path(k);
      if (!v.isMissingNode() && !v.isNull()) o.set(k, v);
    }
    return o;
  }

  private ObjectNode extractAttrs(JsonNode attrs, JsonNode change){
    ObjectNode o = M.createObjectNode();
    if (attrs == null || !attrs.isArray()) return o;
    for (JsonNode a : attrs) {
      if (a.isTextual()) {
        String k = a.asText(); JsonNode v = change.at("/fullDocument/"+k);
        if (!v.isMissingNode()) o.set(k, v);
      } else if (a.isObject()) {
        String k = a.fieldNames().next();
        String expr = a.get(k).asText();
        if (expr.startsWith("$secondsDiff(")) {
          String inner = expr.substring(13, expr.length()-1);
          String[] ab = args(inner);
          try {
            var p = java.time.OffsetDateTime.parse(val(ab[0], change));
            var q = java.time.OffsetDateTime.parse(val(ab[1], change));
            o.put(k, java.time.Duration.between(q, p).toSeconds());
          } catch(Exception ignore){}
        }
      }
    }
    return o;
  }
}
