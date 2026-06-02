{
  "$schema": "https://json-schema.org",
  "title": "ChargeStatisticalSummary",
  "type": "object",
  "properties": {
    "reporting_year": { "type": "integer" },
    "population_baseline": { "type": "integer" },
    "metrics": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "statute_code": { "type": "string" },
          "category": { "type": "string" },
          "raw_count": { "type": "integer" },
          "rate_per_100k": { "type": "number" },
          "percentage_of_total": { "type": "number" },
          "z_score_deviation": { "type": "number" }
        },
        "required": ["statute_code", "category", "raw_count", "rate_per_100k", "percentage_of_total", "z_score_deviation"]
      }
    }
  },
  "required": ["reporting_year", "population_baseline", "metrics"]
}
