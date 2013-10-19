.PHONY: devbuild db distbuild

export PYTHONPATH=/usr/local/lib/python2.7/site-packages

devbuild db:
	# Builds the devbuild aggregate target
	./DevBuild.py --target=${TARGET} --configuration=${CONFIG}	

distbuild:
	#Builds the Distribution build target
	python ./DistributionBuild.py
	. ./EnterprisePackageApplication.sh

testflightdist:
	python ./DistributionBuild.py
	. ./TestFlightDistribute.sh

alldist:
	python ./DistributionBuild.py
	. ./EnterprisePackageApplication.sh
	. ./TestFlightDistribute.sh

utest:
	./RunUnitTests.py --target=${TARGET} --configuration=${CONFIG}	

uitest:
	./RunUIAutomationTests.py \
		--configuration=${CONFIGURATION} \
	   	--target=${TARGET} \
	   	--preprocessor-definitions=${PREPROCESSOR_DEFINITIONS} \
		--project-path=${PROJECT_PATH} \
	   	--test-script=${TEST_SCRIPT} \
	   	--template-path=${TEMPLATE_PATH}

clean:
	xcodebuild clean
