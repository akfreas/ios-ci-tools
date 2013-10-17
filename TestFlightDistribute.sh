source $COMMON_SCRIPTS_HOME/Common.sh



for APP_FILENAME in build/Release-iphoneos/*.app; do

    APP_DIR=$(echo "$APP_FILENAME" | cut -d\. -f1)
    APP_NAME=$(echo $(basename $APP_FILENAME) | cut -d\. -f1)
    IPA_FILENAME="$APP_NAME.ipa"
    DSYM_FILENAME="$APP_NAME.app.dSYM.zip"

    xcrun -sdk iphoneos PackageApplication -v "$APP_FILENAME" -o "$PWD/$IPA_FILENAME" 

    zip -r "$DSYM_FILENAME" "build/Release-iphoneos/$APP_NAME.app.dSYM"
    build_msg=`git show --oneline | grep '^[a-z0-9]\{7\}.*$'`;
    curl http://testflightapp.com/api/builds.json \
    -F file=@$IPA_FILENAME \
    -F dsym=@$DSYM_FILENAME \
    -F api_token='2727f6c23c2c19d8e023942f55964adb_MzIxNTQyMjAxMi0wMi0xNyAwNDozNToxMi4xODMzMTU'  \
    -F team_token='236a691740532ae7f942686a5f800f09_MjAzNzExMjAxMy0wMy0yNSAxNDowNzo1NC4zMTM2NjA' \
    -F notes="$BUILD_NUMBER - $build_msg" \
    -F notify=True \
    -F distribution_lists='Beta Testers'
    
    
done
