build_news_service_chart:
	cat VERSION | xargs -I {} helm package -u --version {} helm/news-service

build_monitor_chart:
	@read -p "Enter monitor chart version:" version; \
	helm package -u --version $$version helm/monitor
