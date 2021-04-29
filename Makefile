build_chart:
	helm package -u --version $$version helm/news-service

build_monitor_chart:
	@read -p "Enter monitor chart version:" version; \
	helm package -u --version $$version helm/news-service-monitor

build_redis_chart:
	@read -p "Enter Redis chart version:" version; \
	helm package -u --version $$version helm/redis

build_rabbit_chart:
	@read -p "Enter Rabbit chart version:" version; \
	helm package -u --version $$version helm/rabbit