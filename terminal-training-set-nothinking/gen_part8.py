import json, os

TARGET = "/media/alamgir-zk/debian13-hdd/alamgir-zk/cluster-ai-training-sets/terminal-training-set-nothinking/part8"

def write_file(cat, name, entries):
    path = os.path.join(TARGET, f"{cat}-{name}.json")
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)
    print(f"  Wrote {path} ({len(entries)} entries)")

def generate_batches(cat, topic, all_entries):
    n = len(all_entries)
    # Split into 10 batches of roughly equal size, each 20-26
    base_size = n // 10
    remainder = n % 10
    start = 0
    for i in range(10):
        size = base_size + (1 if i < remainder else 0)
        batch = all_entries[start:start+size]
        if i == 0:
            write_file(cat, topic, batch)
        else:
            write_file(cat, f"{topic}-batch-{i+1}", batch)
        start += size

# ============================================================
# 107 Loki / LogQL
# ============================================================
cat = 107
entries = [
    {"instruction": "Query all logs from a job with label selector", "output": 'logcli query \'{job="nginx"}\''},
    {"instruction": "Query logs containing an error string", "output": 'logcli query \'{job="nginx"} |= "error"\''},
    {"instruction": "Query logs excluding a string", "output": 'logcli query \'{job="nginx"} != "healthcheck"\''},
    {"instruction": "Query logs with regex match", "output": 'logcli query \'{job="nginx"} |~ "4[0-9][0-9]"\''},
    {"instruction": "Query logs with regex exclusion", "output": 'logcli query \'{job="nginx"} !~ "OPTIONS|HEAD"\''},
    {"instruction": "Parse JSON from log line", "output": 'logcli query \'{job="nginx"} | json\''},
    {"instruction": "Parse logfmt format from log line", "output": 'logcli query \'{job="app"} | logfmt\''},
    {"instruction": "Extract a field with pattern parser", "output": 'logcli query \'{job="app"} | pattern "<ip> - - <_>"\''},
    {"instruction": "Unwrap a numeric value from a JSON field", "output": 'logcli query \'{job="nginx"} | json | unwrap response_time\''},
    {"instruction": "Calculate rate over time", "output": 'logcli query \'rate({job="nginx"} |= "error"[5m])\''},
    {"instruction": "Count logs per level with sum by", "output": 'logcli query \'sum by (level) (count_over_time({job="app"} | json [1m]))\''},
    {"instruction": "Get top 5 error types", "output": 'logcli query \'topk(5, count_over_time({job="app"} |= "error" [5m]))\''},
    {"instruction": "Check absent over time for missing metric", "output": 'logcli query \'absent_over_time({job="worker"}[10m])\''},
    {"instruction": "Query logs from last hour with limit", "output": 'logcli query \'{job="nginx"} |= "error" --limit 100 --since 1h\''},
    {"instruction": "Query logs with specific time range", "output": 'logcli query \'{job="nginx"} --from "2025-01-01T00:00:00Z" --to "2025-01-02T00:00:00Z"\''},
    {"instruction": "Query logs in raw output format", "output": "logcli query '{job=\"nginx\"}' --output raw"},
    {"instruction": "Use LogQL to compute bytes per second rate", "output": 'logcli query \'rate({job="nginx"} | json | unwrap bytes_sent [1m])\''},
    {"instruction": "Count logs per host using label matchers", "output": 'logcli query \'count by (host) (count_over_time({job="nginx"}[5m]))\''},
    {"instruction": "Query logs with multiple label matchers", "output": 'logcli query \'{job="nginx", env="production"} |= "error"\''},
    {"instruction": "Use stream selector with regex on labels", "output": 'logcli query \'{job=~"nginx|apache"} |= "error"\''},
    {"instruction": "Extract label value from log content", "output": 'logcli query \'{job="app"} | logfmt | label_format hostname=host\''},
    {"instruction": "Calculate quantile of request duration", "output": 'logcli query \'quantile_over_time(0.95, {job="nginx"} | json | unwrap request_time [1h])\''},
    {"instruction": "Filter logs by JSON field value", "output": 'logcli query \'{job="app"} | json | status >= 500\''},
    {"instruction": "Use absent_over_time to detect missing service", "output": 'logcli query \'absent_over_time({job="cron"}[15m])\''},
    {"instruction": "Compute avg request duration with unwrap", "output": 'logcli query \'avg by (host) (rate({job="nginx"} | json | unwrap request_time [5m]))\''},
]
generate_batches(cat, "loki-logql", entries)
print(f"Category {cat} done ({len(entries)} total entries)")

# ============================================================
# 108 Datadog CLI
# ============================================================
cat = 108
entries = [
    {"instruction": "Check Datadog agent status", "output": "datadog-agent status"},
    {"instruction": "Check Datadog agent health", "output": "datadog-agent health"},
    {"instruction": "Generate a Datadog flare", "output": "datadog-agent flare --send"},
    {"instruction": "Generate a Datadog flare to a specific case ID", "output": "datadog-agent flare 12345"},
    {"instruction": "Check Datadog agent version", "output": "datadog-agent version"},
    {"instruction": "Start the Datadog agent", "output": "datadog-agent start"},
    {"instruction": "Stop the Datadog agent", "output": "datadog-agent stop"},
    {"instruction": "Restart the Datadog agent", "output": "datadog-agent restart"},
    {"instruction": "Reload the Datadog agent config", "output": "datadog-agent configcheck"},
    {"instruction": "List Datadog agent checks", "output": "datadog-agent check"},
    {"instruction": "Run a specific agent check", "output": "datadog-agent check nginx"},
    {"instruction": "Check Datadog trace agent status", "output": "datadog-agent trace-agent status"},
    {"instruction": "Post a metric via dog CLI", "output": "dog metric post test.metric 1.0 --host myhost"},
    {"instruction": "Post a metric with a tag", "output": 'dog metric post test.metric 1.0 --host myhost --tags "env:prod,region:us-east-1"'},
    {"instruction": "Post a metric at a specific timestamp", "output": "dog metric post test.metric 1.0 --host myhost --timestamp 1700000000"},
    {"instruction": "List monitors with dog CLI", "output": "dog monitor list"},
    {"instruction": "Show a specific monitor", "output": "dog monitor show 12345"},
    {"instruction": "Mute a monitor", "output": "dog monitor mute 12345"},
    {"instruction": "Unmute a monitor", "output": "dog monitor unmute 12345"},
    {"instruction": "List dashboards with dog CLI", "output": "dog dashboard list"},
    {"instruction": "Show a specific dashboard", "output": "dog dashboard show abc-def-123"},
    {"instruction": "Post an event with dog CLI", "output": 'dog event post "Deploy complete" --title "Release v2.0" --priority normal'},
    {"instruction": "Post an event with tags", "output": 'dog event post "Something happened" --tags "env:prod,service:web"'},
    {"instruction": "List hosts with dog CLI", "output": "dog host list"},
    {"instruction": "Get host details", "output": "dog host show myhost.example.com"},
    {"instruction": "Mute a host", "output": "dog host mute myhost.example.com"},
    {"instruction": "Unmute a host", "output": "dog host unmute myhost.example.com"},
    {"instruction": "Set Datadog agent hostname", "output": "datadog-agent hostname"},
    {"instruction": "Check Datadog agent configuration", "output": "datadog-agent config"},
    {"instruction": "List available Datadog integrations", "output": "datadog-agent integration"},
    {"instruction": "Install a Datadog integration wheel", "output": "datadog-agent integration install datadog-nginx==1.0.0"},
    {"instruction": "Check Datadog agent logs", "output": "datadog-agent status --verbose"},
]
generate_batches(cat, "datadog-cli", entries)
print(f"Category {cat} done ({len(entries)} total entries)")

# ============================================================
# 109 OpenTelemetry CLI
# ============================================================
cat = 109
entries = [
    {"instruction": "Execute a command with OpenTelemetry instrumentation", "output": "otel-cli exec --service myapp ./myapp"},
    {"instruction": "Execute a command with custom span name", "output": 'otel-cli exec --service myapp --span-name "process" ./myapp'},
    {"instruction": "Execute a command with OTEL exporter set", "output": "otel-cli exec --service myapp --otlp-endpoint http://otel-collector:4317 ./myapp"},
    {"instruction": "Run a one-shot span with otel-cli", "output": 'otel-cli span --name "my-span" --service myapp'},
    {"instruction": "Run a span with attributes", "output": 'otel-cli span --name "my-span" --service myapp --attrs "key1=val1,key2=val2"'},
    {"instruction": "Run otel-cli as HTTP server", "output": "otel-cli http --service myapp --port 8080"},
    {"instruction": "Run tracegen to generate test traces", "output": "tracegen --service test-service --duration 30s"},
    {"instruction": "Run tracegen with specified rate", "output": "tracegen --service test-service --rate 100 --duration 60s"},
    {"instruction": "Run tracegen with OTLP endpoint", "output": "tracegen --service test-service --otlp-endpoint localhost:4317 --duration 10s"},
    {"instruction": "Run telemetrygen for traces", "output": "telemetrygen traces --duration 10s --rate 10 --otlp-endpoint localhost:4317"},
    {"instruction": "Run telemetrygen for metrics", "output": "telemetrygen metrics --duration 10s --rate 5 --otlp-endpoint localhost:4317"},
    {"instruction": "Run telemetrygen for logs", "output": "telemetrygen logs --duration 10s --rate 5 --otlp-endpoint localhost:4317"},
    {"instruction": "Start otelcol-contrib with a config file", "output": "otelcol-contrib --config /etc/otel/config.yaml"},
    {"instruction": "Validate otelcol config", "output": "otelcol-contrib --config /etc/otel/config.yaml --validate"},
    {"instruction": "Set OTLP gRPC endpoint receiver", "output": 'echo "receivers:\\n  otlp:\\n    protocols:\\n      grpc:\\n        endpoint: 0.0.0.0:4317" > /etc/otel/config.yaml'},
    {"instruction": "Set OTLP HTTP endpoint receiver", "output": 'echo "receivers:\\n  otlp:\\n    protocols:\\n      http:\\n        endpoint: 0.0.0.0:4318" >> /etc/otel/config.yaml'},
    {"instruction": "Add a batch processor to otelcol config", "output": 'echo "processors:\\n  batch:\\n    timeout: 5s\\n    send_batch_size: 1000" >> /etc/otel/config.yaml'},
    {"instruction": "Add memory limiter processor", "output": 'echo "processors:\\n  memory_limiter:\\n    check_interval: 1s\\n    limit_mib: 512" >> /etc/otel/config.yaml'},
    {"instruction": "Add attributes processor to insert env", "output": 'echo "processors:\\n  attributes:\\n    actions:\\n      - key: environment\\n        value: production\\n        action: insert" >> /etc/otel/config.yaml'},
    {"instruction": "Add filter processor to drop debug spans", "output": 'echo "processors:\\n  filter:\\n    spans:\\n      include:\\n        match_type: regexp\\n        services:\\n          - .*" >> /etc/otel/config.yaml'},
    {"instruction": "Export traces to Jaeger", "output": 'echo "exporters:\\n  jaeger:\\n    endpoint: localhost:14250\\n    tls:\\n      insecure: true" >> /etc/otel/config.yaml'},
    {"instruction": "Export metrics to Prometheus", "output": 'echo "exporters:\\n  prometheus:\\n    endpoint: 0.0.0.0:8889" >> /etc/otel/config.yaml'},
    {"instruction": "Export traces to Zipkin", "output": 'echo "exporters:\\n  zipkin:\\n    endpoint: http://zipkin:9411/api/v2/spans" >> /etc/otel/config.yaml'},
    {"instruction": "Set service pipelines in otelcol config", "output": 'echo -e "service:\\n  pipelines:\\n    traces:\\n      receivers: [otlp]\\n      processors: [batch]\\n      exporters: [jaeger]\\n    metrics:\\n      receivers: [otlp]\\n      processors: [batch]\\n      exporters: [prometheus]" >> /etc/otel/config.yaml'},
    {"instruction": "Run otel-cli with custom OTLP headers", "output": 'otel-cli exec --service myapp --otlp-header "api-key=secret123" --otlp-endpoint http://collector:4317 ./myapp'},
    {"instruction": "Run otel-cli as a daemon for background spans", "output": "otel-cli daemon --service myapp --otlp-endpoint http://collector:4317"},
]
generate_batches(cat, "otel-cli", entries)
print(f"Category {cat} done ({len(entries)} total entries)")

# ============================================================
# 110 iptables / nftables deep
# ============================================================
cat = 110
entries = [
    {"instruction": "List all iptables rules", "output": "iptables -L -n -v"},
    {"instruction": "List iptables rules with line numbers", "output": "iptables -L --line-numbers"},
    {"instruction": "List rules in a specific chain", "output": "iptables -L INPUT -n -v"},
    {"instruction": "Allow SSH incoming", "output": "iptables -A INPUT -p tcp --dport 22 -j ACCEPT"},
    {"instruction": "Allow HTTP and HTTPS incoming", "output": "iptables -A INPUT -p tcp -m multiport --dports 80,443 -j ACCEPT"},
    {"instruction": "Drop all incoming traffic by default", "output": "iptables -P INPUT DROP"},
    {"instruction": "Allow established and related connections", "output": "iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT"},
    {"instruction": "Allow traffic from a specific IP", "output": "iptables -A INPUT -s 192.168.1.100 -j ACCEPT"},
    {"instruction": "Block an IP address", "output": "iptables -A INPUT -s 10.0.0.5 -j DROP"},
    {"instruction": "Insert a rule at a specific position", "output": "iptables -I INPUT 3 -p tcp --dport 22 -j ACCEPT"},
    {"instruction": "Delete a rule by line number", "output": "iptables -D INPUT 5"},
    {"instruction": "Delete a rule by specification", "output": "iptables -D INPUT -p tcp --dport 22 -j ACCEPT"},
    {"instruction": "Save iptables rules to file", "output": "iptables-save > /etc/iptables/rules.v4"},
    {"instruction": "Restore iptables rules from file", "output": "iptables-restore < /etc/iptables/rules.v4"},
    {"instruction": "List nftables ruleset", "output": "nft list ruleset"},
    {"instruction": "List nftables table", "output": "nft list table inet filter"},
    {"instruction": "Create an nftables table", "output": "nft add table inet filter"},
    {"instruction": "Delete an nftables table", "output": "nft delete table inet filter"},
    {"instruction": "Create an nftables chain", "output": "nft add chain inet filter input '{ type filter hook input priority 0; policy accept; }'"},
    {"instruction": "Add an nftables rule to allow SSH", "output": "nft add rule inet filter input tcp dport 22 accept"},
    {"instruction": "Add an nftables rule to allow HTTP/HTTPS", "output": "nft add rule inet filter input tcp dport {80, 443} accept"},
    {"instruction": "Add an nftables rule to drop from IP", "output": "nft add rule inet filter input ip saddr 10.0.0.5 drop"},
    {"instruction": "Add an nftables rule to allow established traffic", "output": "nft add rule inet filter input ct state established,related accept"},
    {"instruction": "Create an nftables set", "output": "nft add set inet filter allowed_hosts '{ type ipv4_addr; flags interval; }'"},
    {"instruction": "Add an element to an nftables set", "output": "nft add element inet filter allowed_hosts { 192.168.1.0/24 }"},
    {"instruction": "Create an nftables map", "output": "nft add map inet filter port_map '{ type inet_service: verdict; }'"},
    {"instruction": "Add an element to an nftables map", "output": "nft add element inet filter port_map { 22 : accept, 80 : accept }"},
    {"instruction": "Add an nftables rule using a set", "output": "nft add rule inet filter input ip saddr @allowed_hosts accept"},
    {"instruction": "Flush nftables ruleset", "output": "nft flush ruleset"},
    {"instruction": "Replace a rule in nftables", "output": "nft replace rule inet filter input handle 3 tcp dport 443 accept"},
    {"instruction": "Delete an nftables rule by handle", "output": "nft delete rule inet filter input handle 5"},
    {"instruction": "Add an nftables chain for forward", "output": "nft add chain inet filter forward '{ type filter hook forward priority 0; policy drop; }'"},
    {"instruction": "Add NAT masquerade with nftables", "output": "nft add rule nat postrouting masquerade"},
]
generate_batches(cat, "iptables-nftables", entries)
print(f"Category {cat} done ({len(entries)} total entries)")

# ============================================================
# 111 firewalld
# ============================================================
cat = 111
entries = [
    {"instruction": "Check firewalld status", "output": "firewall-cmd --state"},
    {"instruction": "Get default zone", "output": "firewall-cmd --get-default-zone"},
    {"instruction": "Set default zone to drop", "output": "firewall-cmd --set-default-zone=drop"},
    {"instruction": "List all zones", "output": "firewall-cmd --get-zones"},
    {"instruction": "List all rules in default zone", "output": "firewall-cmd --list-all"},
    {"instruction": "List all rules in a specific zone", "output": "firewall-cmd --zone=public --list-all"},
    {"instruction": "Add a service to the default zone", "output": "firewall-cmd --add-service=http"},
    {"instruction": "Add a service permanently", "output": "firewall-cmd --add-service=http --permanent"},
    {"instruction": "Remove a service from zone", "output": "firewall-cmd --zone=public --remove-service=ssh"},
    {"instruction": "Add a port to zone", "output": "firewall-cmd --zone=public --add-port=8080/tcp"},
    {"instruction": "Add a port range", "output": "firewall-cmd --zone=public --add-port=3000-4000/tcp"},
    {"instruction": "Add a port permanently", "output": "firewall-cmd --zone=public --add-port=8080/tcp --permanent"},
    {"instruction": "Remove a port from zone", "output": "firewall-cmd --zone=public --remove-port=8080/tcp"},
    {"instruction": "Add a source IP to zone", "output": "firewall-cmd --zone=trusted --add-source=192.168.1.0/24"},
    {"instruction": "Remove a source from zone", "output": "firewall-cmd --zone=trusted --remove-source=192.168.1.0/24"},
    {"instruction": "Add a rich rule to accept from IP", "output": 'firewall-cmd --add-rich-rule="rule family=\\"ipv4\\" source address=\\"10.0.0.1\\" accept"'},
    {"instruction": "Add a rich rule to reject a port", "output": 'firewall-cmd --add-rich-rule="rule family=\\"ipv4\\" port port=\\"22\\" protocol=\\"tcp\\" reject"'},
    {"instruction": "Add a rich rule with logging", "output": 'firewall-cmd --add-rich-rule="rule family=\\"ipv4\\" source address=\\"10.0.0.0/24\\" log prefix=\\"blocked\\" level=info drop"'},
    {"instruction": "Remove a rich rule", "output": 'firewall-cmd --remove-rich-rule="rule family=\\"ipv4\\" source address=\\"10.0.0.1\\" accept"'},
    {"instruction": "Enable panic mode", "output": "firewall-cmd --panic-on"},
    {"instruction": "Disable panic mode", "output": "firewall-cmd --panic-off"},
    {"instruction": "Check if panic mode is enabled", "output": "firewall-cmd --query-panic"},
    {"instruction": "Reload firewalld to apply permanent rules", "output": "firewall-cmd --reload"},
    {"instruction": "Reload firewalld completely", "output": "firewall-cmd --complete-reload"},
    {"instruction": "Add an interface to a zone", "output": "firewall-cmd --zone=internal --add-interface=eth1"},
    {"instruction": "Change zone of an interface", "output": "firewall-cmd --zone=dmz --change-interface=eth0"},
    {"instruction": "List active zones", "output": "firewall-cmd --get-active-zones"},
    {"instruction": "List supported services", "output": "firewall-cmd --get-services"},
    {"instruction": "Add a custom service via file", "output": 'echo \'<?xml version="1.0" encoding="utf-8"?>\n<service>\n  <short>myapp</short>\n  <port protocol="tcp" port="9000"/>\n</service>\' > /etc/firewalld/services/myapp.xml'},
    {"instruction": "Reload firewalld to pick up custom service", "output": "firewall-cmd --reload"},
    {"instruction": "Add a masquerade rule for NAT", "output": "firewall-cmd --zone=public --add-masquerade"},
    {"instruction": "Remove masquerade", "output": "firewall-cmd --zone=public --remove-masquerade"},
    {"instruction": "Add rich rule with limit", "output": 'firewall-cmd --add-rich-rule="rule family=\\"ipv4\\" source address=\\"10.0.0.0/24\\" limit value=\\"10/m\\" accept"'},
    {"instruction": "List all rich rules", "output": "firewall-cmd --list-rich-rules"},
]
generate_batches(cat, "firewalld", entries)
print(f"Category {cat} done ({len(entries)} total entries)")

# ============================================================
# 112 SELinux
# ============================================================
cat = 112
entries = [
    {"instruction": "Check SELinux enforcing mode", "output": "getenforce"},
    {"instruction": "Check SELinux status", "output": "sestatus"},
    {"instruction": "Set SELinux to enforcing mode", "output": "setenforce 1"},
    {"instruction": "Set SELinux to permissive mode", "output": "setenforce 0"},
    {"instruction": "Set SELinux to enforcing (by name)", "output": "setenforce enforcing"},
    {"instruction": "Set SELinux to permissive (by name)", "output": "setenforce permissive"},
    {"instruction": "List SELinux booleans", "output": "getsebool -a"},
    {"instruction": "Get a specific SELinux boolean", "output": "getsebool httpd_can_network_connect"},
    {"instruction": "Set an SELinux boolean permanently", "output": "setsebool -P httpd_can_network_connect on"},
    {"instruction": "Set an SELinux boolean temporarily", "output": "setsebool httpd_can_network_connect on"},
    {"instruction": "List file contexts for a path", "output": "ls -Z /var/www/html"},
    {"instruction": "Change file context with chcon", "output": "chcon -t httpd_sys_content_t /var/www/html/index.html"},
    {"instruction": "Restore default file context", "output": "restorecon -v /var/www/html/index.html"},
    {"instruction": "Restore contexts recursively", "output": "restorecon -Rv /var/www/html"},
    {"instruction": "Fix file contexts with fixfiles", "output": "fixfiles -R myapp restore"},
    {"instruction": "Fix all file contexts", "output": "fixfiles restore"},
    {"instruction": "Add a port to a SELinux type", "output": "semanage port -a -t http_port_t -p tcp 8080"},
    {"instruction": "Modify a port SELinux type", "output": "semanage port -m -t http_port_t -p tcp 8080"},
    {"instruction": "Delete a port from SELinux type", "output": "semanage port -d -p tcp 8080"},
    {"instruction": "List SELinux port mappings", "output": "semanage port -l"},
    {"instruction": "Add a file context mapping", "output": "semanage fcontext -a -t httpd_sys_content_t '/web(/.*)?'"},
    {"instruction": "Modify a file context mapping", "output": "semanage fcontext -m -t httpd_sys_content_t '/web(/.*)?'"},
    {"instruction": "Delete a file context mapping", "output": "semanage fcontext -d '/web(/.*)?'"},
    {"instruction": "List SELinux file context mappings", "output": "semanage fcontext -l"},
    {"instruction": "Add a new SELinux user", "output": "semanage user -a -R staff_r staff_u"},
    {"instruction": "List SELinux users", "output": "semanage user -l"},
    {"instruction": "Add a login mapping", "output": "semanage login -a -s staff_u jdoe"},
    {"instruction": "List SELinux login mappings", "output": "semanage login -l"},
    {"instruction": "List SELinux booleans with descriptions", "output": "semanage boolean -l"},
    {"instruction": "Search SELinux policy for a type", "output": "sesearch -t httpd_t"},
    {"instruction": "Search SELinux policy for allow rules", "output": "sesearch --allow -s httpd_t"},
    {"instruction": "Check SELinux policy with seinfo", "output": "seinfo --type=httpd_t"},
    {"instruction": "View SELinux alert details", "output": "sealert -l abc-def-123"},
    {"instruction": "List recent SELinux denials", "output": "sealert -b /var/log/audit/audit.log"},
    {"instruction": "Generate SELinux policy module from log", "output": "audit2allow -w -a"},
    {"instruction": "Generate SELinux module to allow denials", "output": "audit2allow -a -M mypolicy"},
    {"instruction": "Load an SELinux policy module", "output": "semodule -i mypolicy.pp"},
    {"instruction": "Remove an SELinux policy module", "output": "semodule -r mypolicy"},
    {"instruction": "List SELinux policy modules", "output": "semodule -l"},
    {"instruction": "Check whether a path matches its context", "output": "matchpathcon /var/www/html/index.html"},
]
generate_batches(cat, "selinux", entries)
print(f"Category {cat} done ({len(entries)} total entries)")

# ============================================================
# 113 AppArmor
# ============================================================
cat = 113
entries = [
    {"instruction": "Check AppArmor status", "output": "apparmor_status"},
    {"instruction": "Check AppArmor status (short)", "output": "aa-status"},
    {"instruction": "List all loaded AppArmor profiles", "output": "aa-status --profiles"},
    {"instruction": "Enforce a specific AppArmor profile", "output": "aa-enforce /usr/sbin/nginx"},
    {"instruction": "Set profile to complain mode", "output": "aa-complain /usr/sbin/nginx"},
    {"instruction": "Disable a specific AppArmor profile", "output": "aa-disable /usr/sbin/nginx"},
    {"instruction": "Generate a new AppArmor profile automatically", "output": "aa-autodep /usr/sbin/nginx"},
    {"instruction": "Generate a profile with learning mode", "output": "aa-genprof /usr/sbin/nginx"},
    {"instruction": "Run log profiler to update profile", "output": "aa-logprof"},
    {"instruction": "Parse and load an AppArmor profile", "output": "apparmor_parser -r /etc/apparmor.d/usr.sbin.nginx"},
    {"instruction": "Load a profile with kernel cache", "output": "apparmor_parser -r -W /etc/apparmor.d/usr.sbin.nginx"},
    {"instruction": "Skip cache and force reload profile", "output": "apparmor_parser -r -R /etc/apparmor.d/usr.sbin.nginx"},
    {"instruction": "Rebuild AppArmor cache", "output": "apparmor_parser -r --skip-cache /etc/apparmor.d/usr.sbin.nginx"},
    {"instruction": "List profiles in enforce mode", "output": "aa-status --enforced"},
    {"instruction": "List profiles in complain mode", "output": "aa-status --complaining"},
    {"instruction": "Check AppArmor kernel module status", "output": "cat /sys/module/apparmor/parameters/enabled"},
    {"instruction": "View AppArmor profile file for nginx", "output": "cat /etc/apparmor.d/usr.sbin.nginx"},
    {"instruction": "Create a basic AppArmor profile template", "output": 'echo "#include <tunables/global>\nprofile test /usr/bin/test {\n  #include <abstractions/base>\n  /usr/bin/test r,\n}" > /etc/apparmor.d/usr.bin.test'},
    {"instruction": "Reload all AppArmor profiles", "output": "systemctl reload apparmor"},
    {"instruction": "Restart AppArmor service", "output": "systemctl restart apparmor"},
    {"instruction": "Add a capability to an AppArmor profile", "output": 'echo "  capability net_bind_service," >> /etc/apparmor.d/usr.sbin.nginx'},
    {"instruction": "Add a file read rule to AppArmor profile", "output": 'echo "  /var/log/nginx/*.log r," >> /etc/apparmor.d/usr.sbin.nginx'},
    {"instruction": "Add a file write rule to AppArmor profile", "output": 'echo "  /var/run/nginx.pid rw," >> /etc/apparmor.d/usr.sbin.nginx'},
    {"instruction": "Add a network rule to AppArmor profile", "output": 'echo "  network tcp," >> /etc/apparmor.d/usr.sbin.nginx'},
    {"instruction": "Add a deny rule to AppArmor profile", "output": 'echo "  deny /etc/shadow r," >> /etc/apparmor.d/usr.sbin.nginx'},
    {"instruction": "Check if a process is confined by AppArmor", "output": "cat /proc/1/attr/current"},
    {"instruction": "Set a process profile at runtime", "output": "aa-exec -p /usr/sbin/nginx -- /bin/bash"},
    {"instruction": "Change profile for a running process", "output": "echo /usr/sbin/nginx > /proc/$(pidof nginx)/attr/current"},
    {"instruction": "List AppArmor profiles for binaries", "output": "find /etc/apparmor.d -type f -name '*.*' 2>/dev/null"},
]
generate_batches(cat, "apparmor", entries)
print(f"Category {cat} done ({len(entries)} total entries)")

# ============================================================
# 114 auditd / auditing
# ============================================================
cat = 114
entries = [
    {"instruction": "Check auditd service status", "output": "systemctl status auditd"},
    {"instruction": "Start auditd service", "output": "systemctl start auditd"},
    {"instruction": "Restart auditd service", "output": "systemctl restart auditd"},
    {"instruction": "List current audit rules", "output": "auditctl -l"},
    {"instruction": "Add a file watch for write and attribute changes", "output": "auditctl -w /etc/passwd -p wa -k passwd_changes"},
    {"instruction": "Add a file watch for all access", "output": "auditctl -w /etc/shadow -p rwxa -k shadow_access"},
    {"instruction": "Remove a file watch", "output": "auditctl -W /etc/passwd -p wa -k passwd_changes"},
    {"instruction": "Add a syscall audit rule", "output": "auditctl -a always,exit -S openat -F key=open_log"},
    {"instruction": "Add a syscall rule with UID filter", "output": "auditctl -a always,exit -S open -F uid=1000 -F key=user_access"},
    {"instruction": "Add a syscall audit rule for execve", "output": "auditctl -a always,exit -S execve -k process_exec"},
    {"instruction": "Add a network audit rule for connect", "output": "auditctl -a always,exit -S connect -k network_connect"},
    {"instruction": "Add a rule to monitor a directory recursively", "output": "auditctl -w /etc/nginx/ -p wa -k nginx_config"},
    {"instruction": "Delete all audit rules", "output": "auditctl -D"},
    {"instruction": "Set buffer size for audit", "output": "auditctl -b 8192"},
    {"instruction": "Set failure mode for auditd", "output": "auditctl -f 1"},
    {"instruction": "Set rate limit for audit messages", "output": "auditctl -r 1000"},
    {"instruction": "Search audit logs for a key", "output": "ausearch -k passwd_changes"},
    {"instruction": "Search audit logs for an executable", "output": "ausearch -x /usr/bin/sshd"},
    {"instruction": "Search audit logs for a user ID", "output": "ausearch -ui 1000"},
    {"instruction": "Search audit logs by time range", "output": "ausearch -ts 09:00:00 -te 17:00:00"},
    {"instruction": "Search audit logs for today", "output": "ausearch --start today"},
    {"instruction": "Search audit logs for failed syscalls", "output": "ausearch -sv no"},
    {"instruction": "Search audit logs by process ID", "output": "ausearch -p 1234"},
    {"instruction": "Search audit logs for SELinux AVCS", "output": "ausearch -m avc"},
    {"instruction": "Generate audit report by executable", "output": "aureport -x"},
    {"instruction": "Generate audit report summary", "output": "aureport --summary"},
    {"instruction": "Generate audit report by user", "output": "aureport -u"},
    {"instruction": "Generate audit report by time", "output": "aureport -t"},
    {"instruction": "Generate audit report about file changes", "output": "aureport -f"},
    {"instruction": "Generate audit login report", "output": "aureport -l"},
    {"instruction": "Add a persistent audit rule file", "output": 'echo "-w /etc/passwd -p wa -k passwd_changes" >> /etc/audit/rules.d/audit.rules'},
    {"instruction": "Add integration check for audit file", "output": 'echo "-a always,exit -S openat -F dir=/etc -F key=etc_integrity" >> /etc/audit/rules.d/audit.rules'},
    {"instruction": "List audit log files", "output": "ls /var/log/audit/"},
    {"instruction": "Check current audit status", "output": "auditctl -s"},
]
generate_batches(cat, "auditd", entries)
print(f"Category {cat} done ({len(entries)} total entries)")

# ============================================================
# 115 WireGuard deep
# ============================================================
cat = 115
entries = [
    {"instruction": "Show all WireGuard interfaces", "output": "wg show"},
    {"instruction": "Show a specific WireGuard interface", "output": "wg show wg0"},
    {"instruction": "Show WireGuard interface configuration", "output": "wg showconf wg0"},
    {"instruction": "Generate a new WireGuard private key", "output": "wg genkey"},
    {"instruction": "Generate a WireGuard public key from private key", "output": "wg pubkey < privatekey"},
    {"instruction": "Generate a pre-shared key", "output": "wg genpsk"},
    {"instruction": "Generate a key pair and save to files", "output": "wg genkey | tee privatekey | wg pubkey > publickey"},
    {"instruction": "Bring up a WireGuard interface", "output": "wg-quick up wg0"},
    {"instruction": "Bring down a WireGuard interface", "output": "wg-quick down wg0"},
    {"instruction": "Restart a WireGuard interface", "output": "wg-quick down wg0 && wg-quick up wg0"},
    {"instruction": "Add a peer to WireGuard interface", "output": 'wg set wg0 peer abc123def456... allowed-ips 10.0.0.2/32'},
    {"instruction": "Add a peer with endpoint and keepalive", "output": 'wg set wg0 peer abc123def456... allowed-ips 10.0.0.2/32 endpoint 203.0.113.5:51820 persistent-keepalive 25'},
    {"instruction": "Remove a peer from WireGuard interface", "output": 'wg set wg0 peer abc123def456... remove'},
    {"instruction": "Set WireGuard interface private key", "output": 'wg set wg0 private-key /etc/wireguard/privatekey'},
    {"instruction": "Set WireGuard interface listen port", "output": 'wg set wg0 listen-port 51820'},
    {"instruction": "Set WireGuard interface MTU", "output": 'wg set wg0 mtu 1420'},
    {"instruction": "Set WireGuard interface fwmark", "output": 'wg set wg0 fwmark 0xca6c'},
    {"instruction": "Set WireGuard interface table for routing", "output": 'wg set wg0 table 51820'},
    {"instruction": "Create a WireGuard config file for a server", "output": 'echo -e "[Interface]\\nPrivateKey = $(cat privatekey)\\nAddress = 10.0.0.1/24\\nListenPort = 51820\\nSaveConfig = true" > /etc/wireguard/wg0.conf'},
    {"instruction": "Add a peer to WireGuard config file", "output": 'echo -e "\\n[Peer]\\nPublicKey = $(cat peer1.pub)\\nAllowedIPs = 10.0.0.2/32" >> /etc/wireguard/wg0.conf'},
    {"instruction": "Add PostUp iptables rule in WireGuard config", "output": 'echo "PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE" >> /etc/wireguard/wg0.conf'},
    {"instruction": "Add PreDown iptables rule in WireGuard config", "output": 'echo "PreDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -D FORWARD -o wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE" >> /etc/wireguard/wg0.conf'},
    {"instruction": "Create a WireGuard config for a client", "output": 'echo -e "[Interface]\\nPrivateKey = $(cat client-priv)\\nAddress = 10.0.0.2/32\\nDNS = 1.1.1.1\\n\\n[Peer]\\nPublicKey = $(cat server-pub)\\nEndpoint = server.example.com:51820\\nAllowedIPs = 0.0.0.0/0\\nPersistentKeepalive = 25" > /etc/wireguard/wg0.conf'},
    {"instruction": "Check WireGuard interface transfer stats", "output": "wg show wg0 transfer"},
    {"instruction": "Check WireGuard interface latest handshake", "output": "wg show wg0 latest-handshakes"},
    {"instruction": "Check WireGuard interface allowed IPs", "output": "wg show wg0 allowed-ips"},
    {"instruction": "Enable IP forwarding for WireGuard", "output": "sysctl -w net.ipv4.ip_forward=1"},
    {"instruction": "Make IP forwarding permanent", "output": 'echo "net.ipv4.ip_forward=1" >> /etc/sysctl.d/99-wireguard.conf'},
    {"instruction": "Save current WireGuard config from running interface", "output": "wg-quick save wg0"},
    {"instruction": "Show all WireGuard peers in JSON format", "output": "wg show all dump"},
]
generate_batches(cat, "wireguard", entries)
print(f"Category {cat} done ({len(entries)} total entries)")

# ============================================================
# 116 Dockerfile & Build
# ============================================================
cat = 116
entries = [
    {"instruction": "Build a Docker image from Dockerfile", "output": "docker build -t myapp:latest ."},
    {"instruction": "Build a Docker image with no cache", "output": "docker build --no-cache -t myapp:latest ."},
    {"instruction": "Build a Docker image with a specific Dockerfile", "output": "docker build -f docker/Dockerfile.prod -t myapp:latest ."},
    {"instruction": "Build a Docker image with build args", "output": "docker build --build-arg VERSION=1.0.0 -t myapp:latest ."},
    {"instruction": "Build a Docker image with a target stage", "output": "docker build --target production -t myapp:latest ."},
    {"instruction": "Build a multi-platform image with buildx", "output": "docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest ."},
    {"instruction": "Build and push multi-platform image", "output": "docker buildx build --platform linux/amd64,linux/arm64 -t myuser/myapp:latest --push ."},
    {"instruction": "Create a new buildx builder", "output": "docker buildx create --name mybuilder --use"},
    {"instruction": "Create a buildx builder with driver docker-container", "output": "docker buildx create --driver docker-container --name multiarch --use"},
    {"instruction": "List all buildx builders", "output": "docker buildx ls"},
    {"instruction": "Use a specific buildx builder", "output": "docker buildx use mybuilder"},
    {"instruction": "Inspect buildx builder", "output": "docker buildx inspect mybuilder"},
    {"instruction": "List buildx build cache", "output": "docker buildx du"},
    {"instruction": "Prune buildx build cache", "output": "docker builder prune"},
    {"instruction": "Prune buildx cache with force", "output": "docker builder prune -f"},
    {"instruction": "Prune build cache keeping recent", "output": "docker builder prune --keep-storage 10GB"},
    {"instruction": "Build with BuildKit cache mount for apt", "output": "docker build --no-cache --mount type=cache,target=/var/cache/apt ."},
    {"instruction": "Build with BuildKit bind mount", "output": "docker build --mount type=bind,from=alpine,source=/etc/passwd,target=/tmp/passwd ."},
    {"instruction": "Use a Docker secret during build", "output": "docker build --secret id=mysecret,src=./secret.txt -t myapp:latest ."},
    {"instruction": "Use SSH agent during build", "output": "docker build --ssh default -t myapp:latest ."},
    {"instruction": "Export build output to a directory", "output": "docker build -o outdir ."},
    {"instruction": "Export build output as tar archive", "output": "docker build -o type=tar,dest=out.tar ."},
    {"instruction": "Build with squash flag", "output": "docker build --squash -t myapp:latest ."},
    {"instruction": "Build a Docker image with a tag alias", "output": "docker build -t myapp:latest -t myapp:1.0.0 ."},
    {"instruction": "Create a multi-stage Dockerfile with Alpine", "output": "echo -e 'FROM golang:1.21 AS builder\\nWORKDIR /app\\nCOPY . .\\nRUN go build -o myapp .\\n\\nFROM alpine:3.19\\nCOPY --from=builder /app/myapp /usr/local/bin/\\nCMD [\"myapp\"]' > Dockerfile"},
    {"instruction": "Create a Dockerfile with BuildKit cache mount for go modules", "output": "echo -e 'FROM golang:1.21 AS builder\\nWORKDIR /app\\nCOPY go.mod go.sum .\\nRUN --mount=type=cache,target=/go/pkg/mod go mod download\\nCOPY . .\\nRUN go build -o myapp .\\n\\nFROM alpine:3.19\\nCOPY --from=builder /app/myapp /usr/local/bin/\\nCMD [\"myapp\"]' > Dockerfile"},
    {"instruction": "Build with --output type=docker", "output": "docker buildx build --output type=docker,name=myapp:latest ."},
    {"instruction": "Build with --output type=image,push=true", "output": "docker buildx build --output type=image,name=myapp:latest,push=true ."},
    {"instruction": "Install buildx plugin", "output": "docker buildx install"},
    {"instruction": "Uninstall buildx plugin", "output": "docker buildx uninstall"},
    {"instruction": "Create a Dockerfile using heredoc", "output": "cat <<'EOF' > Dockerfile\nFROM debian:12\nRUN apt-get update && apt-get install -y nginx\nEXPOSE 80\nCMD [\"nginx\", \"-g\", \"daemon off;\"]\nEOF"},
    {"instruction": "Build with CPU platform constraint", "output": "docker build --platform linux/amd64 -t myapp:amd64 ."},
    {"instruction": "Build with dockerfile inline syntax", "output": "cat Dockerfile | docker build -t myapp:latest -f- ."},
]
generate_batches(cat, "dockerfile-build", entries)
print(f"Category {cat} done ({len(entries)} total entries)")

print("\n=== ALL CATEGORIES GENERATED ===")
