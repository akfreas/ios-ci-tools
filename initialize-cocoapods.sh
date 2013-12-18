#!/usr/bin/env sh

gem install cocoapods
pod install
xctool -project Pods/Pods.xcodeproj -scheme $1
cd ../
