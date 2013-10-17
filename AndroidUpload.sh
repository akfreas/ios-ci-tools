package_file=$1

if [ "$BUILD_NUMBER" != "" ]; then
    version_number=$BUILD_NUMBER;
else
    version_number=$2;
fi

if [ "$GIT_BRANCH" != "" ]; then
    tag=$GIT_BRANCH;
else
    tag=$3;
fi

echo $tag

if [ "$4" == "" ]; then
    spout_upload_url="http://spout.hq.rws/upload"
else
    spout_upload_url=$4
fi
build_msg=`git show --oneline | grep '^[a-z0-9]\{7\}.*$'`;
curl $spout_upload_url \
    -F app_package=@$package_file \
    -F note="$build_msg" \
    -F product="2" \
    -F file_type="ANDROID" \
    -F tag="$tag"
