for APP_FILENAME in build/Release-iphoneos/*.app; do

    APP_DIR=$(echo "$APP_FILENAME" | cut -d\. -f1)
    APP_NAME=$(echo $(basename $APP_FILENAME) | cut -d\. -f1)
    IPA_FILENAME="$APP_NAME.ipa"
    DSYM_FILENAME="$APP_NAME.app.dSYM.zip"

    xcrun -sdk iphoneos PackageApplication -v "$APP_FILENAME" -o "$PWD/$IPA_FILENAME" 

    zip -r "$DSYM_FILENAME" "build/Release-iphoneos/$APP_NAME.app.dSYM"
    build_msg=`git show --oneline | grep '^[a-z0-9]\{7\}.*$'`;
    curl $UPLOAD_URL \
    -F app_package=@$IPA_FILENAME \
    -F dsym_file=@$DSYM_FILENAME \
    -F note="$build_msg" \
    -F version="$BUILD_NUMBER" \
    -F product="$DIST_PRODUCT" \
    -F file_type="IOS" \
    -F tag="$GIT_BRANCH" # > ~/Desktop/error.html; open ~/Desktop/error.html
    
    
done
