import json
import statistics
from http.server import BaseHTTPRequestHandler

# Paste the entire JSON data here as a Python list
DATA = [
  {"region":"apac","service":"analytics","latency_ms":187.13,"uptime_pct":99.103,"timestamp":20250301},
  {"region":"apac","service":"checkout","latency_ms":225.58,"uptime_pct":98.869,"timestamp":20250302},
  {"region":"apac","service":"payments","latency_ms":214.32,"uptime_pct":97.798,"timestamp":20250303},
  {"region":"apac","service":"recommendations","latency_ms":190.28,"uptime_pct":98.14,"timestamp":20250304},
  {"region":"apac","service":"support","latency_ms":119.3,"uptime_pct":98.913,"timestamp":20250305},
  {"region":"apac","service":"payments","latency_ms":142.1,"uptime_pct":98.577,"timestamp":20250306},
  {"region":"apac","service":"checkout","latency_ms":181.78,"uptime_pct":99.216,"timestamp":20250307},
  {"region":"apac","service":"checkout","latency_ms":219.97,"uptime_pct":99.164,"timestamp":20250308},
  {"region":"apac","service":"recommendations","latency_ms":132.76,"uptime_pct":99.157,"timestamp":20250309},
  {"region":"apac","service":"recommendations","latency_ms":199.65,"uptime_pct":99.332,"timestamp":20250310},
  {"region":"apac","service":"analytics","latency_ms":197.75,"uptime_pct":97.685,"timestamp":20250311},
  {"region":"apac","service":"recommendations","latency_ms":161.12,"uptime_pct":98.457,"timestamp":20250312},
  {"region":"emea","service":"support","latency_ms":165.18,"uptime_pct":99.475,"timestamp":20250301},
  {"region":"emea","service":"recommendations","latency_ms":233.99,"uptime_pct":98.429,"timestamp":20250302},
  {"region":"emea","service":"recommendations","latency_ms":185,"uptime_pct":97.53,"timestamp":20250303},
  {"region":"emea","service":"analytics","latency_ms":188.02,"uptime_pct":97.173,"timestamp":20250304},
  {"region":"emea","service":"payments","latency_ms":150.23,"uptime_pct":97.187,"timestamp":20250305},
  {"region":"emea","service":"recommendations","latency_ms":208.96,"uptime_pct":97.878,"timestamp":20250306},
  {"region":"emea","service":"catalog","latency_ms":193.78,"uptime_pct":98.834,"timestamp":20250307},
  {"region":"emea","service":"checkout","latency_ms":147.97,"uptime_pct":99.362,"timestamp":20250308},
  {"region":"emea","service":"support","latency_ms":129.79,"uptime_pct":99.236,"timestamp":20250309},
  {"region":"emea","service":"support","latency_ms":170.93,"uptime_pct":97.934,"timestamp":20250310},
  {"region":"emea","service":"recommendations","latency_ms":129.94,"uptime_pct":97.693,"timestamp":20250311},
  {"region":"emea","service":"catalog","latency_ms":204.74,"uptime_pct":98.935,"timestamp":20250312},
  {"region":"amer","service":"recommendations","latency_ms":197.02,"uptime_pct":97.47,"timestamp":20250301},
  {"region":"amer","service":"analytics","latency_ms":203.37,"uptime_pct":97.616,"timestamp":20250302},
  {"region":"amer","service":"checkout","latency_ms":209.57,"uptime_pct":98.995,"timestamp":20250303},
  {"region":"amer","service":"catalog","latency_ms":118.49,"uptime_pct":98.168,"timestamp":20250304},
  {"region":"amer","service":"recommendations","latency_ms":211.19,"uptime_pct":99.066,"timestamp":20250305},
  {"region":"amer","service":"analytics","latency_ms":138.25,"uptime_pct":97.714,"timestamp":20250306},
  {"region":"amer","service":"support","latency_ms":121.44,"uptime_pct":97.793,"timestamp":20250307},
  {"region":"amer","service":"payments","latency_ms":159.83,"uptime_pct":98.258,"timestamp":20250308},
  {"region":"amer","service":"support","latency_ms":157.06,"uptime_pct":98.544,"timestamp":20250309},
  {"region":"amer","service":"catalog","latency_ms":212.35,"uptime_pct":98.54,"timestamp":20250310},
  {"region":"amer","service":"support","latency_ms":151.03,"uptime_pct":98.179,"timestamp":20250311},
  {"region":"amer","service":"payments","latency_ms":170.81,"uptime_pct":99.297,"timestamp":20250312},
]

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))

        regions = body.get("regions", [])
        threshold = body.get("threshold_ms", 200)

        result = {}
        for region in regions:
            records = [r for r in DATA if r["region"] == region]
            if not records:
                result[region] = None
                continue
            latencies = [r["latency_ms"] for r in records]
            uptimes   = [r["uptime_pct"]  for r in records]
            sorted_lat = sorted(latencies)
            n = len(sorted_lat)
            # 95th percentile using nearest-rank method
            idx = max(int(0.95 * n) - 1, 0)
            p95 = sorted_lat[idx]

            result[region] = {
                "avg_latency": round(statistics.mean(latencies), 4),
                "p95_latency": round(p95, 4),
                "avg_uptime":  round(statistics.mean(uptimes), 4),
                "breaches":    sum(1 for l in latencies if l > threshold),
            }

        response = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(response)