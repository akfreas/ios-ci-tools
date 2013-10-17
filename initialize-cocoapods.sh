#!/usr/bin/env sh

gem install cocoapods
pod install
cd ./Pods
xcodebuild
cd ../
