./copy_to_baby.sh
echo ===============================================
ssh pi@babyberry.duckdns.org "cd MusiQ/Backend && sudo ./reload_fastapi_container.sh"