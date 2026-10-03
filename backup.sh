#!/bin/bash

dir=$(dirname $(realpath $0))
source $dir/.env

keep=${KEEP:-7}
stamp=$(date +%Y%m%d-%H%M%S)
dump=forgejo-dump-$stamp.zip
repos=$FORGE_DATA/forgejo-data/git/repositories

mkdir -p $dir/archives $dir/bundles

docker exec -u git forgejo forgejo dump --type zip --file /tmp/$dump -c /data/gitea/conf/app.ini
docker cp forgejo:/tmp/$dump $dir/archives/
docker exec -u git forgejo rm -f /tmp/$dump

for repo in $repos/*/*.git; do
    [ -d "$repo" ] || continue
    owner=$(basename $(dirname $repo))
    name=$(basename $repo .git)
    [ -n "$(git -c safe.directory='*' -C $repo for-each-ref --count=1)" ] || continue

    mkdir -p $dir/bundles/$owner
    git -c safe.directory='*' -C $repo bundle create $dir/bundles/$owner/.$name.tmp --all
    git -c safe.directory='*' bundle verify $dir/bundles/$owner/.$name.tmp > /dev/null &&
        mv $dir/bundles/$owner/.$name.tmp $dir/bundles/$owner/$name.bundle
done

ls -1t $dir/archives/forgejo-dump-*.zip | tail -n +$((keep + 1)) | xargs -r rm -f
