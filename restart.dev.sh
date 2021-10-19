# sh build.dev.sh

# these commands build/rebuild the dev docker environment
# be careful when running and make sure your data/ and logs/ folders are empty! and make sure the sample pg_vol is not present.
# otherwise build size will be too large
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart

echo "Dev build down"
