# сборка docker образа
docker build -t twc-dockerfile-flask-app:latest .

# запуск контейнера на порту 3478
docker run -d -p 3478:3478 twc-dockerfile-flask-app

# vitrina example url
http://localhost:3478/vitrina/oneprofit/484146b9-f61c-448d-bf4a-384a35825ae1/?flow_id=76406&site_id=%SITE_ID%&teaser_id=%AD_ID%&campaign_id=%CAMP_ID%&click_id=%CLICK_ID%&source_name=adwile&cpc=%TEASER_CPC%&block_id=%BLOCK_ID%

# nutra example url
https://localhost:3478/nutra/hypert/miasnikov-churikova?site_id=%SITE_ID%&teaser_id=%AD_ID%&campaign_id=%CAMP_ID%&click_id=%CLICK_ID%&source_name=adwile&cpc=%TEASER_CPC%&block_id=%BLOCK_ID%