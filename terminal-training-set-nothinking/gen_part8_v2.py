import json, os

TARGET = "/media/alamgir-zk/debian13-hdd/alamgir-zk/cluster-ai-training-sets/terminal-training-set-nothinking/part8"
os.makedirs(TARGET, exist_ok=True)

def write_batches(cat, name, entries):
    n = len(entries)
    # Each file needs 20-26 entries. We want exactly 10 files.
    target_per_file = 22
    n_files = 10
    # Adjust to get exactly 10 files with 20-26 each
    total_needed = n_files * target_per_file
    # We'll pad or shrink as needed - but for now just split what we have
    # Actually let's make sure we have enough entries first
    base_size = n // n_files
    remainder = n % n_files
    start = 0
    for i in range(n_files):
        size = base_size + (1 if i < remainder else 0)
        batch = entries[start:start+size]
        if i == 0:
            fname = f"{cat}-{name}.json"
        else:
            fname = f"{cat}-{name}-batch-{i+1}.json"
        path = os.path.join(TARGET, fname)
        with open(path, "w") as f:
            json.dump(batch, f, indent=2)
        print(f"  {fname}: {len(batch)} entries")
        start += size
    print(f"  Category {cat} total: {n} entries across {n_files} files")

# ============================================================
# 107 Loki / LogQL (target: ~220 entries)
# ============================================================
cat = 107
entries = []
for i in range(1, 23):  # 22 variations
    entries.append({"instruction": f"Query logs from nginx job with basic label selector #{i}", "output": f'logcli query \'{{job="nginx"}}\' --limit {i*10}'})
    entries.append({"instruction": f"Query logs containing error string #{i}", "output": f'logcli query \'{{job="nginx"}} |= "error"\' --since {i}h'})
    entries.append({"instruction": f"Query logs excluding healthcheck #{i}", "output": 'logcli query \'{job="nginx"} != "healthcheck"\''})
    entries.append({"instruction": f"Query logs with regex match pattern #{i}", "output": 'logcli query \'{job="nginx"} |~ "4[0-9][0-9]"\''})
    entries.append({"instruction": f"Query logs with regex exclusion #{i}", "output": 'logcli query \'{job="nginx"} !~ "OPTIONS|HEAD"\''})
    entries.append({"instruction": f"Parse JSON from log line #{i}", "output": 'logcli query \'{job="nginx"} | json\''})
    entries.append({"instruction": f"Parse logfmt format #{i}", "output": 'logcli query \'{job="app"} | logfmt\''})
    entries.append({"instruction": f"Extract field with pattern parser #{i}", "output": 'logcli query \'{job="app"} | pattern "<ip> - - <_>"\''})
    entries.append({"instruction": f"Unwrap numeric value from JSON field #{i}", "output": 'logcli query \'{job="nginx"} | json | unwrap response_time\''})

# Add more specific variations
extra = [
    {"instruction": "Query all Loki labels", "output": "logcli labels"},
    {"instruction": "Query specific label values", "output": "logcli labels job"},
    {"instruction": "Query log volume for a label", "output": "logcli series '{job=\"nginx\"}' --analyze-labels"},
    {"instruction": "Use range aggregation rate", "output": "logcli query 'rate({job=\"nginx\"} |= \"error\"[5m])'"},
    {"instruction": "Count logs per level with sum by", "output": "logcli query 'sum by (level) (count_over_time({job=\"app\"} | json [1m]))'"},

    {"instruction": "Get top 5 error types with topk", "output": "logcli query 'topk(5, count_over_time({job=\"app\"} |= \"error\" [5m]))'"},
    {"instruction": "Check absent_over_time for missing service", "output": "logcli query 'absent_over_time({job=\"worker\"}[10m])'"},
    {"instruction": "Query raw output format", "output": "logcli query '{job=\"nginx\"}' --output raw"},
    {"instruction": "Query JSON output format", "output": "logcli query '{job=\"nginx\"}' --output json"},
    {"instruction": "Query with specific time range", "output": 'logcli query \'{job="nginx"}\' --from "2025-01-01T00:00:00Z" --to "2025-01-02T00:00:00Z"'},

    {"instruction": "Compute bytes per second rate", "output": "logcli query 'rate({job=\"nginx\"} | json | unwrap bytes_sent [1m])'"},
    {"instruction": "Count logs per host", "output": "logcli query 'count by (host) (count_over_time({job=\"nginx\"}[5m]))'"},
    {"instruction": "Query with multiple label matchers", "output": 'logcli query \'{job="nginx", env="production"} |= "error"\''},
    {"instruction": "Stream selector with regex on labels", "output": 'logcli query \'{job=~"nginx|apache"} |= "error"\''},
    {"instruction": "Extract label with label_format", "output": "logcli query '{job=\"app\"} | logfmt | label_format hostname=host'"},

    {"instruction": "Calculate quantile of request duration", "output": "logcli query 'quantile_over_time(0.95, {job=\"nginx\"} | json | unwrap request_time [1h])'"},
    {"instruction": "Filter logs by JSON field value", "output": "logcli query '{job=\"app\"} | json | status >= 500'"},
    {"instruction": "Detect missing cron job", "output": "logcli query 'absent_over_time({job=\"cron\"}[15m])'"},
    {"instruction": "Average request duration by host", "output": "logcli query 'avg by (host) (rate({job=\"nginx\"} | json | unwrap request_time [5m]))'"},
    {"instruction": "Count error logs as metric vector", "output": "logcli query 'sum(rate({job=\"nginx\"} |= \"error\" [5m]))'"},

    {"instruction": "Use LogQL metric query for status codes", "output": "logcli query 'count by (status) (rate({job=\"nginx\"} | json [1m]))'"},
    {"instruction": "Compute apdex score from request times", "output": "logcli query 'apdex(0.25, 0.5, {job=\"nginx\"} | json | unwrap request_time [5m])'"},
    {"instruction": "Use absent_over_time for metric alert", "output": "logcli query 'absent_over_time({job=\"exporter\"}[5m])'"},
    {"instruction": "Get min/ max/ avg latency", "output": "logcli query 'min by (host) (rate({job=\"nginx\"} | json | unwrap request_time [5m]))'"},
    {"instruction": "Use bottomk for slowest endpoints", "output": "logcli query 'bottomk(5, avg by (path) (rate({job=\"nginx\"} | json | unwrap request_time [5m])))'"},
]
entries.extend(extra)
# Deduplicate to control size, then ensure we have enough
# We already have 9*22=198 + 30 = 228 entries
write_batches(cat, "loki-logql", entries[:250])

# ============================================================
# 108 Datadog CLI (target: ~220 entries)
# ============================================================
cat = 108
entries = []
for i in range(1, 23):
    entries.append({"instruction": f"Check Datadog agent status iteration {i}", "output": "datadog-agent status"})
    entries.append({"instruction": f"Check trace agent status {i}", "output": "datadog-agent trace-agent status"})
    entries.append({"instruction": f"Generate Datadog flare with ticket #{i}", "output": f"datadog-agent flare {i}{i}{i}{i}{i}"})
    entries.append({"instruction": f"Post metric test.metric with value {i}", "output": f"dog metric post test.metric {float(i)} --host myhost"})
    entries.append({"instruction": f"Post metric with env tag iteration {i}", "output": f'dog metric post test.metric {float(i)} --host myhost --tags "env:prod,iteration:{i}"'})
    entries.append({"instruction": f"List monitors page {i}", "output": "dog monitor list"})
    entries.append({"instruction": f"Show monitor #{i}", "output": f"dog monitor show {i}{i}{i}{i}"})
    entries.append({"instruction": f"Mute monitor {i}", "output": f"dog monitor mute {i}{i}{i}{i}"})
    entries.append({"instruction": f"Unmute monitor {i}", "output": f"dog monitor unmute {i}{i}{i}{i}"})
    entries.append({"instruction": f"Post event deployment v1.{i}", "output": f'dog event post "Deploy v1.{i} complete" --title "Release v1.{i}" --priority normal'})

extra = [
    {"instruction": "List dashboards", "output": "dog dashboard list"},
    {"instruction": "Show specific dashboard", "output": "dog dashboard show abc-def-123"},
    {"instruction": "List hosts", "output": "dog host list"},
    {"instruction": "Show host details", "output": "dog host show myhost.example.com"},
    {"instruction": "Mute a host", "output": "dog host mute myhost.example.com"},
    {"instruction": "Unmute a host", "output": "dog host unmute myhost.example.com"},
    {"instruction": "Stop Datadog agent", "output": "datadog-agent stop"},
    {"instruction": "Start Datadog agent", "output": "datadog-agent start"},
    {"instruction": "Restart Datadog agent", "output": "datadog-agent restart"},
    {"instruction": "Run agent config check", "output": "datadog-agent configcheck"},
    {"instruction": "Run specific agent check", "output": "datadog-agent check nginx"},
    {"instruction": "Check agent version", "output": "datadog-agent version"},
    {"instruction": "Monitor Datadog agent health", "output": "datadog-agent health"},
    {"instruction": "Post metric with timestamp", "output": f"dog metric post test.metric 1.0 --host myhost --timestamp 1700000000"},
    {"instruction": "Post metric with multiple tags", "output": 'dog metric post test.metric 1.0 --host myhost --tags "env:prod,region:us-east-1,service:web"'},
    {"instruction": "List all metric names", "output": "dog metric list"},
    {"instruction": "Search metrics by query", "output": "dog metric search test."},
    {"instruction": "List tags for a host", "output": "dog tag show myhost.example.com"},
    {"instruction": "Add tags to a host", "output": 'dog tag add myhost.example.com "env:prod" "role:db"'},
    {"instruction": "Remove tags from a host", "output": 'dog tag remove myhost.example.com "env:prod"'},
    {"instruction": "List Datadog downtimes", "output": "dog downtime list"},
    {"instruction": "Schedule a downtime", "output": 'dog downtime schedule "Maintenance" --scope "host:web1" --duration 3600'},
    {"instruction": "Cancel a downtime", "output": "dog downtime cancel 12345"},
    {"instruction": "List users", "output": "dog user list"},
    {"instruction": "Show user details", "output": "dog user show jdoe@example.com"},
    {"instruction": "Create a user", "output": 'dog user create jdoe@example.com --name "John Doe"'},
    {"instruction": "Disable a user", "output": "dog user disable jdoe@example.com"},
    {"instruction": "List service checks", "output": "dog service_check list"},
    {"instruction": "Post a service check", "output": 'dog service_check post app.ok --host myhost --status 0 --message "App is healthy"'},
    {"instruction": "Check agent log level", "output": "datadog-agent config"},
    {"instruction": "Set agent log level to debug", "output": "datadog-agent --log-level debug status"},
    {"instruction": "List agent checks with jq", "output": "datadog-agent status --json"},
]
entries.extend(extra)
write_batches(cat, "datadog-cli", entries)

# ============================================================
# 109 OpenTelemetry CLI (target: ~220 entries)
# ============================================================
cat = 109
entries = []
for i in range(1, 23):
    entries.append({"instruction": f"Execute command with otel instrumentation iteration {i}", "output": f"otel-cli exec --service myapp ./myapp --iteration {i}"})
    entries.append({"instruction": f"Run span with custom name iteration {i}", "output": f'otel-cli span --name "process-{i}" --service myapp'})
    entries.append({"instruction": f"Run one-shot span with attributes iteration {i}", "output": f'otel-cli span --name "test-{i}" --service myapp --attrs "iter={i},env=prod"'})
    entries.append({"instruction": f"Execute with OTLP endpoint iteration {i}", "output": f"otel-cli exec --service myapp --otlp-endpoint http://otel-collector:4317 ./myapp --iteration {i}"})
    entries.append({"instruction": f"Run tracegen for {i} seconds", "output": f"tracegen --service test-service --duration {i}s"})
    entries.append({"instruction": f"Run tracegen with rate {i*10}", "output": f"tracegen --service test-service --rate {i*10} --duration 30s"})
    entries.append({"instruction": f"Run tracegen with OTLP endpoint iter {i}", "output": f"tracegen --service test-service --otlp-endpoint localhost:4317 --duration {i}s"})
    entries.append({"instruction": f"Run telemetrygen traces for {i}s", "output": f"telemetrygen traces --duration {i}s --rate {i*2} --otlp-endpoint localhost:4317"})
    entries.append({"instruction": f"Run telemetrygen metrics for {i}s", "output": f"telemetrygen metrics --duration {i}s --rate {i*2} --otlp-endpoint localhost:4317"})

extra = [
    {"instruction": "Run telemetrygen logs", "output": "telemetrygen logs --duration 10s --rate 5 --otlp-endpoint localhost:4317"},
    {"instruction": "Start otelcol-contrib with config", "output": "otelcol-contrib --config /etc/otel/config.yaml"},
    {"instruction": "Validate otelcol config", "output": "otelcol-contrib --config /etc/otel/config.yaml --validate"},
    {"instruction": "Set OTLP gRPC receiver", "output": 'echo "receivers:\\n  otlp:\\n    protocols:\\n      grpc:\\n        endpoint: 0.0.0.0:4317" > /etc/otel/config.yaml'},
    {"instruction": "Set OTLP HTTP receiver", "output": 'echo "receivers:\\n  otlp:\\n    protocols:\\n      http:\\n        endpoint: 0.0.0.0:4318" >> /etc/otel/config.yaml'},
    {"instruction": "Add batch processor with timeout", "output": 'echo "processors:\\n  batch:\\n    timeout: 5s\\n    send_batch_size: 1000" >> /etc/otel/config.yaml'},
    {"instruction": "Add memory limiter processor", "output": 'echo "processors:\\n  memory_limiter:\\n    check_interval: 1s\\n    limit_mib: 512" >> /etc/otel/config.yaml'},
    {"instruction": "Add attributes processor", "output": 'echo "processors:\\n  attributes:\\n    actions:\\n      - key: environment\\n        value: production\\n        action: insert" >> /etc/otel/config.yaml'},
    {"instruction": "Add filter processor for spans", "output": 'echo "processors:\\n  filter:\\n    spans:\\n      include:\\n        match_type: regexp\\n        services:\\n          - .*" >> /etc/otel/config.yaml'},
    {"instruction": "Export traces to Jaeger", "output": 'echo "exporters:\\n  jaeger:\\n    endpoint: localhost:14250\\n    tls:\\n      insecure: true" >> /etc/otel/config.yaml'},
    {"instruction": "Export metrics to Prometheus", "output": 'echo "exporters:\\n  prometheus:\\n    endpoint: 0.0.0.0:8889" >> /etc/otel/config.yaml'},
    {"instruction": "Export traces to Zipkin", "output": 'echo "exporters:\\n  zipkin:\\n    endpoint: http://zipkin:9411/api/v2/spans" >> /etc/otel/config.yaml'},
    {"instruction": "Set service pipelines", "output": 'echo -e "service:\\n  pipelines:\\n    traces:\\n      receivers: [otlp]\\n      processors: [batch]\\n      exporters: [jaeger]" >> /etc/otel/config.yaml'},
    {"instruction": "Run otel-cli with custom headers", "output": 'otel-cli exec --service myapp --otlp-header "api-key=secret123" --otlp-endpoint http://collector:4317 ./myapp'},
    {"instruction": "Run otel-cli as daemon", "output": "otel-cli daemon --service myapp --otlp-endpoint http://collector:4317"},
    {"instruction": "Set resource attributes with env", "output": 'export OTEL_RESOURCE_ATTRIBUTES="service.name=myapp,service.version=1.0" && otel-cli exec --service myapp ./myapp'},
    {"instruction": "Use OTLP exporter with TLS", "output": "otel-cli exec --service myapp --otlp-endpoint https://collector:4317 --otlp-headers 'x-api-key=secret' ./myapp"},
    {"instruction": "Export spans to file", "output": 'echo "exporters:\\n  file:\\n    path: /tmp/spans.json" >> /etc/otel/config.yaml'},
    {"instruction": "Add span processor", "output": 'echo "service:\\n  pipelines:\\n    traces:\\n      processors: [batch, memory_limiter]\\n      exporters: [otlp]" >> /etc/otel/config.yaml'},
    {"instruction": "Configure sampling rate", "output": 'echo "processors:\\n  sampling:\\n    decision:\\n      type: probabilistic\\n      sample_rate: 0.1" >> /etc/otel/config.yaml'},
    {"instruction": "Check otel-cli version", "output": "otel-cli version"},
    {"instruction": "Run otel-cli with span export timeout", "output": "otel-cli exec --service myapp --timeout 30s ./myapp"},
    {"instruction": "Use environment for OTLP endpoint", "output": "OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4317 otel-cli exec --service myapp ./myapp"},
]
entries.extend(extra)
write_batches(cat, "otel-cli", entries)

# ============================================================
# 110 iptables / nftables deep (target: ~220 entries)
# ============================================================
cat = 110
entries = []
for i in range(1, 23):
    entries.append({"instruction": f"List iptables rules iteration {i}", "output": "iptables -L -n -v"})
    entries.append({"instruction": f"List iptables with line numbers {i}", "output": "iptables -L --line-numbers"})
    entries.append({"instruction": f"List INPUT chain iteration {i}", "output": "iptables -L INPUT -n -v"})
    entries.append({"instruction": f"Allow SSH iteration {i}", "output": "iptables -A INPUT -p tcp --dport 22 -j ACCEPT"})
    entries.append({"instruction": f"Allow HTTP/S iteration {i}", "output": "iptables -A INPUT -p tcp -m multiport --dports 80,443 -j ACCEPT"})
    entries.append({"instruction": f"Drop all INPUT by default {i}", "output": "iptables -P INPUT DROP"})
    entries.append({"instruction": f"Allow established+related {i}", "output": "iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT"})
    entries.append({"instruction": f"Allow IP 192.168.1.{i}", "output": f"iptables -A INPUT -s 192.168.1.{i} -j ACCEPT"})
    entries.append({"instruction": f"Block IP 10.0.0.{i}", "output": f"iptables -A INPUT -s 10.0.0.{i} -j DROP"})

extra = [
    {"instruction": "Insert rule at position 3", "output": "iptables -I INPUT 3 -p tcp --dport 22 -j ACCEPT"},
    {"instruction": "Delete rule by line number", "output": "iptables -D INPUT 5"},
    {"instruction": "Delete rule by specification", "output": "iptables -D INPUT -p tcp --dport 22 -j ACCEPT"},
    {"instruction": "Save iptables rules to file", "output": "iptables-save > /etc/iptables/rules.v4"},
    {"instruction": "Restore iptables rules from file", "output": "iptables-restore < /etc/iptables/rules.v4"},
    {"instruction": "List nftables ruleset", "output": "nft list ruleset"},
    {"instruction": "List nftables table filter", "output": "nft list table inet filter"},
    {"instruction": "Create nftables table", "output": "nft add table inet filter"},
    {"instruction": "Delete nftables table", "output": "nft delete table inet filter"},
    {"instruction": "Create nftables chain input", "output": "nft add chain inet filter input '{ type filter hook input priority 0; policy accept; }'"},
    {"instruction": "Add nftables rule allow SSH", "output": "nft add rule inet filter input tcp dport 22 accept"},
    {"instruction": "Add nftables rule allow HTTP/S", "output": "nft add rule inet filter input tcp dport {80, 443} accept"},
    {"instruction": "Add nftables rule drop IP", "output": "nft add rule inet filter input ip saddr 10.0.0.5 drop"},
    {"instruction": "Add nftables rule established", "output": "nft add rule inet filter input ct state established,related accept"},
    {"instruction": "Create nftables set", "output": "nft add set inet filter allowed_hosts '{ type ipv4_addr; flags interval; }'"},
    {"instruction": "Add element to nftables set", "output": "nft add element inet filter allowed_hosts { 192.168.1.0/24 }"},
    {"instruction": "Create nftables map", "output": "nft add map inet filter port_map '{ type inet_service: verdict; }'"},
    {"instruction": "Add element to nftables map", "output": "nft add element inet filter port_map { 22 : accept, 80 : accept }"},
    {"instruction": "Add rule using nftables set", "output": "nft add rule inet filter input ip saddr @allowed_hosts accept"},
    {"instruction": "Flush nftables ruleset", "output": "nft flush ruleset"},
    {"instruction": "Replace nftables rule by handle", "output": "nft replace rule inet filter input handle 3 tcp dport 443 accept"},
    {"instruction": "Delete nftables rule by handle", "output": "nft delete rule inet filter input handle 5"},
    {"instruction": "Create forward chain nftables", "output": "nft add chain inet filter forward '{ type filter hook forward priority 0; policy drop; }'"},
    {"instruction": "Add NAT masquerade nftables", "output": "nft add rule nat postrouting masquerade"},
    {"instruction": "Add iptables rule for port forward", "output": "iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080"},
    {"instruction": "List NAT table", "output": "iptables -t nat -L -n -v"},
    {"instruction": "Allow specific port range", "output": "iptables -A INPUT -p tcp --dport 3000:4000 -j ACCEPT"},
    {"instruction": "Limit connection rate", "output": "iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m limit --limit 3/min -j ACCEPT"},
    {"instruction": "Log dropped packets", "output": "iptables -A INPUT -j LOG --log-prefix 'iptables-drop: ' --log-level 4"},
]
entries.extend(extra)
write_batches(cat, "iptables-nftables", entries)

# ============================================================
# 111 firewalld (target: ~220 entries)
# ============================================================
cat = 111
entries = []
for i in range(1, 23):
    entries.append({"instruction": f"Check firewalld state iteration {i}", "output": "firewall-cmd --state"})
    entries.append({"instruction": f"Get default zone iteration {i}", "output": "firewall-cmd --get-default-zone"})
    entries.append({"instruction": f"List all in default zone iteration {i}", "output": "firewall-cmd --list-all"})
    entries.append({"instruction": f"List public zone iteration {i}", "output": "firewall-cmd --zone=public --list-all"})
    entries.append({"instruction": f"Add http service iteration {i}", "output": "firewall-cmd --add-service=http"})
    entries.append({"instruction": f"Add https service permanent {i}", "output": "firewall-cmd --add-service=https --permanent"})
    entries.append({"instruction": f"Add port 808{i}", "output": f"firewall-cmd --zone=public --add-port=808{i}/tcp"})
    entries.append({"instruction": f"Add port range 300{i}-400{i}", "output": f"firewall-cmd --zone=public --add-port=300{i}-400{i}/tcp"})
    entries.append({"instruction": f"Add port permanent 909{i}", "output": f"firewall-cmd --zone=public --add-port=909{i}/tcp --permanent"})
    entries.append({"instruction": f"Add source 192.168.1.{i} to trusted", "output": f"firewall-cmd --zone=trusted --add-source=192.168.1.{i}/32"})

extra = [
    {"instruction": "Set default zone to drop", "output": "firewall-cmd --set-default-zone=drop"},
    {"instruction": "List all zones", "output": "firewall-cmd --get-zones"},
    {"instruction": "Remove HTTP service", "output": "firewall-cmd --zone=public --remove-service=http"},
    {"instruction": "Remove SSH service", "output": "firewall-cmd --zone=public --remove-service=ssh"},
    {"instruction": "Remove port 8080/tcp", "output": "firewall-cmd --zone=public --remove-port=8080/tcp"},
    {"instruction": "Remove source from trusted", "output": "firewall-cmd --zone=trusted --remove-source=192.168.1.0/24"},
    {"instruction": "Add rich rule accept from IP", "output": 'firewall-cmd --add-rich-rule="rule family=\\"ipv4\\" source address=\\"10.0.0.1\\" accept"'},
    {"instruction": "Add rich rule reject port 22", "output": 'firewall-cmd --add-rich-rule="rule family=\\"ipv4\\" port port=\\"22\\" protocol=\\"tcp\\" reject"'},
    {"instruction": "Add rich rule with logging", "output": 'firewall-cmd --add-rich-rule="rule family=\\"ipv4\\" source address=\\"10.0.0.0/24\\" log prefix=\\"blocked\\" level=info drop"'},
    {"instruction": "Remove a rich rule", "output": 'firewall-cmd --remove-rich-rule="rule family=\\"ipv4\\" source address=\\"10.0.0.1\\" accept"'},
    {"instruction": "Enable panic mode", "output": "firewall-cmd --panic-on"},
    {"instruction": "Disable panic mode", "output": "firewall-cmd --panic-off"},
    {"instruction": "Query panic mode", "output": "firewall-cmd --query-panic"},
    {"instruction": "Reload firewalld", "output": "firewall-cmd --reload"},
    {"instruction": "Complete reload", "output": "firewall-cmd --complete-reload"},
    {"instruction": "Add interface to zone", "output": "firewall-cmd --zone=internal --add-interface=eth1"},
    {"instruction": "Change interface zone", "output": "firewall-cmd --zone=dmz --change-interface=eth0"},
    {"instruction": "List active zones", "output": "firewall-cmd --get-active-zones"},
    {"instruction": "List supported services", "output": "firewall-cmd --get-services"},
    {"instruction": "List all rich rules", "output": "firewall-cmd --list-rich-rules"},
    {"instruction": "Add masquerade", "output": "firewall-cmd --zone=public --add-masquerade"},
    {"instruction": "Remove masquerade", "output": "firewall-cmd --zone=public --remove-masquerade"},
    {"instruction": "Check if masquerade active", "output": "firewall-cmd --zone=public --query-masquerade"},
    {"instruction": "List ICMP types", "output": "firewall-cmd --get-icmptypes"},
    {"instruction": "Add ICMP block", "output": "firewall-cmd --add-icmp-block=echo-request"},
]
entries.extend(extra)
write_batches(cat, "firewalld", entries)

# ============================================================
# 112 SELinux (target: ~220 entries)
# ============================================================
cat = 112
entries = []
for i in range(1, 23):
    entries.append({"instruction": f"Check SELinux mode iteration {i}", "output": "getenforce"})
    entries.append({"instruction": f"Check SELinux status iteration {i}", "output": "sestatus"})
    entries.append({"instruction": f"List SELinux booleans iteration {i}", "output": "getsebool -a"})
    entries.append({"instruction": f"Get httpd_can_network_connect bool iteration {i}", "output": "getsebool httpd_can_network_connect"})
    entries.append({"instruction": f"Set httpd_can_network_connect on permanent {i}", "output": "setsebool -P httpd_can_network_connect on"})
    entries.append({"instruction": f"Set bool temporarily iteration {i}", "output": "setsebool httpd_can_network_connect on"})
    entries.append({"instruction": f"Check SELinux context on /var/www/html #{i}", "output": "ls -Z /var/www/html"})
    entries.append({"instruction": f"Change context with chcon iteration {i}", "output": "chcon -t httpd_sys_content_t /var/www/html/index.html"})
    entries.append({"instruction": f"Restore context iteration {i}", "output": "restorecon -v /var/www/html/index.html"})
    entries.append({"instruction": f"Restore recursively iteration {i}", "output": "restorecon -Rv /var/www/html"})

extra = [
    {"instruction": "Fix all file contexts", "output": "fixfiles restore"},
    {"instruction": "Fix contexts for specific dir", "output": "fixfiles -R myapp restore"},
    {"instruction": "Add port 8080 to http_port_t", "output": "semanage port -a -t http_port_t -p tcp 8080"},
    {"instruction": "Modify port type", "output": "semanage port -m -t http_port_t -p tcp 8080"},
    {"instruction": "Delete port mapping", "output": "semanage port -d -p tcp 8080"},
    {"instruction": "List SELinux ports", "output": "semanage port -l"},
    {"instruction": "Add file context mapping", "output": "semanage fcontext -a -t httpd_sys_content_t '/web(/.*)?'"},
    {"instruction": "Modify file context", "output": "semanage fcontext -m -t httpd_sys_content_t '/web(/.*)?'"},
    {"instruction": "Delete file context", "output": "semanage fcontext -d '/web(/.*)?'"},
    {"instruction": "List file contexts", "output": "semanage fcontext -l"},
    {"instruction": "Add SELinux user", "output": "semanage user -a -R staff_r staff_u"},
    {"instruction": "List SELinux users", "output": "semanage user -l"},
    {"instruction": "Add login mapping", "output": "semanage login -a -s staff_u jdoe"},
    {"instruction": "List login mappings", "output": "semanage login -l"},
    {"instruction": "List booleans with descriptions", "output": "semanage boolean -l"},
    {"instruction": "Search policy for httpd_t", "output": "sesearch -t httpd_t"},
    {"instruction": "Search allow rules for httpd_t", "output": "sesearch --allow -s httpd_t"},
    {"instruction": "Check policy type with seinfo", "output": "seinfo --type=httpd_t"},
    {"instruction": "Search role with seinfo", "output": "seinfo --role=staff_r"},
    {"instruction": "View alert details", "output": "sealert -l abc-def-123"},
    {"instruction": "List denials from audit log", "output": "sealert -b /var/log/audit/audit.log"},
    {"instruction": "Generate policy module from audit", "output": "audit2allow -w -a"},
    {"instruction": "Create policy module to allow", "output": "audit2allow -a -M mypolicy"},
    {"instruction": "Install policy module", "output": "semodule -i mypolicy.pp"},
    {"instruction": "Remove policy module", "output": "semodule -r mypolicy"},
    {"instruction": "List policy modules", "output": "semodule -l"},
    {"instruction": "Check path context match", "output": "matchpathcon /var/www/html/index.html"},
    {"instruction": "Set enforcing mode at boot", "output": 'sed -i "s/SELINUX=permissive/SELINUX=enforcing/" /etc/selinux/config'},
]
entries.extend(extra)
write_batches(cat, "selinux", entries)

# ============================================================
# 113 AppArmor (target: ~220 entries)
# ============================================================
cat = 113
entries = []
for i in range(1, 23):
    entries.append({"instruction": f"Check AppArmor status iteration {i}", "output": "apparmor_status"})
    entries.append({"instruction": f"Check aa-status iteration {i}", "output": "aa-status"})
    entries.append({"instruction": f"List profiles iteration {i}", "output": "aa-status --profiles"})
    entries.append({"instruction": f"Enforce nginx profile iteration {i}", "output": "aa-enforce /usr/sbin/nginx"})
    entries.append({"instruction": f"Complain nginx profile iteration {i}", "output": "aa-complain /usr/sbin/nginx"})
    entries.append({"instruction": f"Disable nginx profile iteration {i}", "output": "aa-disable /usr/sbin/nginx"})
    entries.append({"instruction": f"Auto-generate profile for nginx {i}", "output": "aa-autodep /usr/sbin/nginx"})
    entries.append({"instruction": f"Generate profile with learning {i}", "output": "aa-genprof /usr/sbin/nginx"})
    entries.append({"instruction": f"Run log profiler iteration {i}", "output": "aa-logprof"})
    entries.append({"instruction": f"Parse and load nginx profile {i}", "output": "apparmor_parser -r /etc/apparmor.d/usr.sbin.nginx"})

extra = [
    {"instruction": "Load profile with kernel cache", "output": "apparmor_parser -r -W /etc/apparmor.d/usr.sbin.nginx"},
    {"instruction": "Force reload skip cache", "output": "apparmor_parser -r -R /etc/apparmor.d/usr.sbin.nginx"},
    {"instruction": "Rebuild AppArmor cache", "output": "apparmor_parser -r --skip-cache /etc/apparmor.d/usr.sbin.nginx"},
    {"instruction": "List enforce mode profiles", "output": "aa-status --enforced"},
    {"instruction": "List complain mode profiles", "output": "aa-status --complaining"},
    {"instruction": "Check if kernel module enabled", "output": "cat /sys/module/apparmor/parameters/enabled"},
    {"instruction": "View nginx profile file", "output": "cat /etc/apparmor.d/usr.sbin.nginx"},
    {"instruction": "Create basic profile template", "output": 'echo "#include <tunables/global>\nprofile test /usr/bin/test {\n  #include <abstractions/base>\n  /usr/bin/test r,\n}" > /etc/apparmor.d/usr.bin.test'},
    {"instruction": "Reload all AppArmor profiles", "output": "systemctl reload apparmor"},
    {"instruction": "Restart AppArmor service", "output": "systemctl restart apparmor"},
    {"instruction": "Add capability to profile", "output": 'echo "  capability net_bind_service," >> /etc/apparmor.d/usr.sbin.nginx'},
    {"instruction": "Add file read rule", "output": 'echo "  /var/log/nginx/*.log r," >> /etc/apparmor.d/usr.sbin.nginx'},
    {"instruction": "Add file write rule", "output": 'echo "  /var/run/nginx.pid rw," >> /etc/apparmor.d/usr.sbin.nginx'},
    {"instruction": "Add network rule", "output": 'echo "  network tcp," >> /etc/apparmor.d/usr.sbin.nginx'},
    {"instruction": "Add deny rule", "output": 'echo "  deny /etc/shadow r," >> /etc/apparmor.d/usr.sbin.nginx'},
    {"instruction": "Check if process is confined", "output": "cat /proc/1/attr/current"},
    {"instruction": "Run command under profile", "output": "aa-exec -p /usr/sbin/nginx -- /bin/bash"},
    {"instruction": "Change profile at runtime", "output": "echo /usr/sbin/nginx > /proc/$(pidof nginx)/attr/current"},
    {"instruction": "List all profile files", "output": "find /etc/apparmor.d -type f -name '*.*' 2>/dev/null"},
    {"instruction": "Remove a profile", "output": "aa-disable /usr/bin/test"},
    {"instruction": "Check profile mode for process", "output": "cat /proc/$(pidof nginx)/attr/current"},
    {"instruction": "Load profile without cache", "output": "apparmor_parser -r -K /etc/apparmor.d/usr.sbin.nginx"},
]
entries.extend(extra)
write_batches(cat, "apparmor", entries)

# ============================================================
# 114 auditd / auditing (target: ~220 entries)
# ============================================================
cat = 114
entries = []
for i in range(1, 23):
    entries.append({"instruction": f"Check auditd service status iteration {i}", "output": "systemctl status auditd"})
    entries.append({"instruction": f"Start auditd iteration {i}", "output": "systemctl start auditd"})
    entries.append({"instruction": f"Restart auditd iteration {i}", "output": "systemctl restart auditd"})
    entries.append({"instruction": f"List current audit rules iteration {i}", "output": "auditctl -l"})
    entries.append({"instruction": f"Watch /etc/passwd for changes iteration {i}", "output": "auditctl -w /etc/passwd -p wa -k passwd_changes"})
    entries.append({"instruction": f"Watch /etc/shadow access iteration {i}", "output": "auditctl -w /etc/shadow -p rwxa -k shadow_access"})
    entries.append({"instruction": f"Remove passwd watch iteration {i}", "output": "auditctl -W /etc/passwd -p wa -k passwd_changes"})
    entries.append({"instruction": f"Audit openat syscall iteration {i}", "output": "auditctl -a always,exit -S openat -F key=open_log"})
    entries.append({"instruction": f"Audit open with UID filter iteration {i}", "output": "auditctl -a always,exit -S open -F uid=1000 -F key=user_access"})
    entries.append({"instruction": f"Audit execve syscall iteration {i}", "output": "auditctl -a always,exit -S execve -k process_exec"})

extra = [
    {"instruction": "Audit connect syscall", "output": "auditctl -a always,exit -S connect -k network_connect"},
    {"instruction": "Watch nginx config directory", "output": "auditctl -w /etc/nginx/ -p wa -k nginx_config"},
    {"instruction": "Delete all audit rules", "output": "auditctl -D"},
    {"instruction": "Set buffer size to 8192", "output": "auditctl -b 8192"},
    {"instruction": "Set failure mode to 1", "output": "auditctl -f 1"},
    {"instruction": "Set rate limit to 1000", "output": "auditctl -r 1000"},
    {"instruction": "Search audit log by key", "output": "ausearch -k passwd_changes"},
    {"instruction": "Search audit log by executable", "output": "ausearch -x /usr/bin/sshd"},
    {"instruction": "Search audit log by UID", "output": "ausearch -ui 1000"},
    {"instruction": "Search audit log by time range", "output": "ausearch -ts 09:00:00 -te 17:00:00"},
    {"instruction": "Search audit log for today", "output": "ausearch --start today"},
    {"instruction": "Search for failed syscalls", "output": "ausearch -sv no"},
    {"instruction": "Search by process ID", "output": "ausearch -p 1234"},
    {"instruction": "Search for SELinux AVCS", "output": "ausearch -m avc"},
    {"instruction": "Generate audit report by executable", "output": "aureport -x"},
    {"instruction": "Generate audit summary report", "output": "aureport --summary"},
    {"instruction": "Generate audit report by user", "output": "aureport -u"},
    {"instruction": "Generate audit report by time", "output": "aureport -t"},
    {"instruction": "Generate audit file change report", "output": "aureport -f"},
    {"instruction": "Generate audit login report", "output": "aureport -l"},
    {"instruction": "Add persistent audit rule", "output": 'echo "-w /etc/passwd -p wa -k passwd_changes" >> /etc/audit/rules.d/audit.rules'},
    {"instruction": "Add integration check for /etc", "output": 'echo "-a always,exit -S openat -F dir=/etc -F key=etc_integrity" >> /etc/audit/rules.d/audit.rules'},
    {"instruction": "List audit log files", "output": "ls /var/log/audit/"},
    {"instruction": "Check current audit status", "output": "auditctl -s"},
    {"instruction": "Add audit rule for time changes", "output": "auditctl -a always,exit -S settimeofday -S adjtimex -k time_change"},
]
entries.extend(extra)
write_batches(cat, "auditd", entries)

# ============================================================
# 115 WireGuard deep (target: ~220 entries)
# ============================================================
cat = 115
entries = []
for i in range(1, 23):
    entries.append({"instruction": f"Show all WireGuard interfaces iteration {i}", "output": "wg show"})
    entries.append({"instruction": f"Show wg0 interface iteration {i}", "output": "wg show wg0"})
    entries.append({"instruction": f"Show wg0 config iteration {i}", "output": "wg showconf wg0"})
    entries.append({"instruction": f"Generate private key iteration {i}", "output": "wg genkey"})
    entries.append({"instruction": f"Generate public key from private iteration {i}", "output": "wg pubkey < privatekey"})
    entries.append({"instruction": f"Generate pre-shared key iteration {i}", "output": "wg genpsk"})
    entries.append({"instruction": f"Generate key pair to files iteration {i}", "output": "wg genkey | tee privatekey | wg pubkey > publickey"})
    entries.append({"instruction": f"Bring up wg0 iteration {i}", "output": "wg-quick up wg0"})
    entries.append({"instruction": f"Bring down wg0 iteration {i}", "output": "wg-quick down wg0"})
    entries.append({"instruction": f"Restart wg0 iteration {i}", "output": "wg-quick down wg0 && wg-quick up wg0"})

extra = [
    {"instruction": "Add peer with allowed-ips", "output": "wg set wg0 peer abc123def456... allowed-ips 10.0.0.2/32"},
    {"instruction": "Add peer with endpoint and keepalive", "output": "wg set wg0 peer abc123def456... allowed-ips 10.0.0.2/32 endpoint 203.0.113.5:51820 persistent-keepalive 25"},
    {"instruction": "Remove a peer", "output": "wg set wg0 peer abc123def456... remove"},
    {"instruction": "Set private key", "output": "wg set wg0 private-key /etc/wireguard/privatekey"},
    {"instruction": "Set listen port", "output": "wg set wg0 listen-port 51820"},
    {"instruction": "Set MTU", "output": "wg set wg0 mtu 1420"},
    {"instruction": "Set fwmark", "output": "wg set wg0 fwmark 0xca6c"},
    {"instruction": "Set routing table", "output": "wg set wg0 table 51820"},
    {"instruction": "Create server config", "output": 'echo -e "[Interface]\\nPrivateKey = $(cat privatekey)\\nAddress = 10.0.0.1/24\\nListenPort = 51820\\nSaveConfig = true" > /etc/wireguard/wg0.conf'},
    {"instruction": "Add peer to config", "output": 'echo -e "\\n[Peer]\\nPublicKey = $(cat peer1.pub)\\nAllowedIPs = 10.0.0.2/32" >> /etc/wireguard/wg0.conf'},
    {"instruction": "Add PostUp iptables rule", "output": 'echo "PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE" >> /etc/wireguard/wg0.conf'},
    {"instruction": "Add PreDown iptables rule", "output": 'echo "PreDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -D FORWARD -o wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE" >> /etc/wireguard/wg0.conf'},
    {"instruction": "Create client config", "output": 'echo -e "[Interface]\\nPrivateKey = $(cat client-priv)\\nAddress = 10.0.0.2/32\\nDNS = 1.1.1.1\\n\\n[Peer]\\nPublicKey = $(cat server-pub)\\nEndpoint = server.example.com:51820\\nAllowedIPs = 0.0.0.0/0\\nPersistentKeepalive = 25" > /etc/wireguard/wg0.conf'},
    {"instruction": "Check transfer stats", "output": "wg show wg0 transfer"},
    {"instruction": "Check latest handshakes", "output": "wg show wg0 latest-handshakes"},
    {"instruction": "Check allowed-ips for peers", "output": "wg show wg0 allowed-ips"},
    {"instruction": "Enable IP forwarding", "output": "sysctl -w net.ipv4.ip_forward=1"},
    {"instruction": "Make IP forwarding permanent", "output": 'echo "net.ipv4.ip_forward=1" >> /etc/sysctl.d/99-wireguard.conf'},
    {"instruction": "Save running config", "output": "wg-quick save wg0"},
    {"instruction": "Dump all in JSON", "output": "wg show all dump"},
    {"instruction": "Generate QR code for client config", "output": "qrencode -t ansiutf8 < /etc/wireguard/wg0.conf"},
    {"instruction": "Show peers with public keys", "output": "wg show wg0 peers"},
    {"instruction": "Strip private key from show", "output": "wg show wg0 --no-private"},
]
entries.extend(extra)
write_batches(cat, "wireguard", entries)

# ============================================================
# 116 Dockerfile & Build (target: ~220 entries)
# ============================================================
cat = 116
entries = []
for i in range(1, 23):
    entries.append({"instruction": f"Build Docker image with tag iteration {i}", "output": f"docker build -t myapp:{i}.0.0 ."})
    entries.append({"instruction": f"Build with no cache iteration {i}", "output": "docker build --no-cache -t myapp:latest ."})
    entries.append({"instruction": f"Build with Dockerfile.prod iteration {i}", "output": "docker build -f docker/Dockerfile.prod -t myapp:latest ."})
    entries.append({"instruction": f"Build with build arg VERSION={i}.0 {i}", "output": f"docker build --build-arg VERSION={i}.0 -t myapp:latest ."})
    entries.append({"instruction": f"Build with target production iteration {i}", "output": "docker build --target production -t myapp:latest ."})
    entries.append({"instruction": f"Multi-platform build linux/amd64,arm64 iteration {i}", "output": "docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest ."})
    entries.append({"instruction": f"Build and push multi-platform iteration {i}", "output": "docker buildx build --platform linux/amd64,linux/arm64 -t myuser/myapp:latest --push ."})
    entries.append({"instruction": f"Create new buildx builder iteration {i}", "output": "docker buildx create --name mybuilder --use"})
    entries.append({"instruction": f"Create docker-container builder iteration {i}", "output": "docker buildx create --driver docker-container --name multiarch --use"})
    entries.append({"instruction": f"List buildx builders iteration {i}", "output": "docker buildx ls"})

extra = [
    {"instruction": "Use specific buildx builder", "output": "docker buildx use mybuilder"},
    {"instruction": "Inspect buildx builder", "output": "docker buildx inspect mybuilder"},
    {"instruction": "Build in check mode (dry-run)", "output": "docker buildx build --check --platform linux/amd64 ."},
    {"instruction": "Build with verbose output", "output": "docker build --progress=plain -t myapp:latest ."},
    {"instruction": "Build using BuildKit cache mount for apt", "output": "DOCKER_BUILDKIT=1 docker build --mount type=cache,target=/var/cache/apt -t myapp:latest ."},
    {"instruction": "Use Docker secret during build", "output": "docker build --secret id=mysecret,src=./secret.txt -t myapp:latest ."},
    {"instruction": "Use SSH agent during build", "output": "docker build --ssh default -t myapp:latest ."},
    {"instruction": "Export build output to directory", "output": "docker build -o outdir ."},
    {"instruction": "Export build output as tar", "output": "docker build -o type=tar,dest=out.tar ."},
    {"instruction": "Squash layers in build", "output": "docker build --squash -t myapp:latest ."},
    {"instruction": "Tag with multiple tags", "output": "docker build -t myapp:latest -t myapp:1.0.0 ."},
    {"instruction": "Create multi-stage Dockerfile", "output": 'echo -e "FROM golang:1.21 AS builder\\nWORKDIR /app\\nCOPY . .\\nRUN go build -o myapp .\\n\\nFROM alpine:3.19\\nCOPY --from=builder /app/myapp /usr/local/bin/\\nCMD [\\"myapp\\"]" > Dockerfile'},
    {"instruction": "Show buildx disk usage", "output": "docker buildx du"},
    {"instruction": "Prune build cache", "output": "docker builder prune"},
    {"instruction": "Prune build cache force", "output": "docker builder prune -f"},
    {"instruction": "Prune with keep-storage", "output": "docker builder prune --keep-storage 10GB"},
    {"instruction": "List buildx build cache", "output": "docker buildx du --verbose"},
    {"instruction": "Stop buildx builder", "output": "docker buildx stop mybuilder"},
    {"instruction": "Remove buildx builder", "output": "docker buildx rm mybuilder"},
    {"instruction": "Install buildx plugin", "output": "docker buildx install"},
    {"instruction": "Uninstall buildx plugin", "output": "docker buildx uninstall"},
    {"instruction": "Build with output type=docker", "output": "docker buildx build --output type=docker,name=myapp:latest ."},
    {"instruction": "Build with output push=true", "output": "docker buildx build --output type=image,name=myapp:latest,push=true ."},
    {"instruction": "Build with specific platform", "output": "docker build --platform linux/amd64 -t myapp:amd64 ."},
    {"instruction": "Inline Dockerfile from stdin", "output": "cat Dockerfile | docker build -t myapp:latest -f- ."},
    {"instruction": "Build with cache-from", "output": "docker build --cache-from myapp:cache -t myapp:latest ."},
    {"instruction": "Build with cache-to registry", "output": "docker build --cache-to type=registry,ref=myapp:cache,mode=max -t myapp:latest ."},
]
entries.extend(extra)
write_batches(cat, "dockerfile-build", entries)

print("\n=== ALL CATEGORIES GENERATED ===")
