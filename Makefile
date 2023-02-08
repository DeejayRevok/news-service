build_chart:
	helm package -u --version $$version helm/news-service

build_monitor_chart:
	@read -p "Enter monitor chart version:" version; \
	helm package -u --version $$version helm/monitor
