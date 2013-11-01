.PHONY: devbuild db distbuild

export PYTHONPATH=${COMMON_SCRIPTS_HOME}/lib/python2.7/site-packages

devbuild db:
	# Builds the devbuild aggregate target
	${COMMON_SCRIPTS_HOME}/DevBuild.py --target=${TARGET} --configuration=${CONFIG}	

distbuild:
	#Builds the Distribution build target
	${COMMON_SCRIPTS_HOME}/bin/python ${COMMON_SCRIPTS_HOME}/DistributionBuild.py
	.${COMMON_SCRIPTS_HOME}/EnterprisePackageApplication.sh

travisdist:
	/usr/bin/env
	${COMMON_SCRIPTS_HOME}/bin/python ${COMMON_SCRIPTS_HOME}/setup_site_packages.py
	${COMMON_SCRIPTS_HOME}/bin/python ${COMMON_SCRIPTS_HOME}/install_ios_sdk.py --sdk ${DIST_SDK}
	${COMMON_SCRIPTS_HOME}/bin/python ${COMMON_SCRIPTS_HOME}/DistributionBuild.py
	${COMMON_SCRIPTS_HOME}/bin/python ${COMMON_SCRIPTS_HOME}/package_and_upload_app.py



testflightdist:
	python ${COMMON_SCRIPTS_HOME}/DistributionBuild.py
	. ${COMMON_SCRIPTS_HOME}/TestFlightDistribute.sh

alldist:
	python ${COMMON_SCRIPTS_HOME}/DistributionBuild.py
	. ${COMMON_SCRIPTS_HOME}/EnterprisePackageApplication.sh
	. ${COMMON_SCRIPTS_HOME}/TestFlightDistribute.sh

utest:
	${COMMON_SCRIPTS_HOME}/RunUnitTests.py --target=${TARGET} --configuration=${CONFIG}	

uitest:
	${COMMON_SCRIPTS_HOME}/RunUIAutomationTests.py \
		--configuration=${CONFIGURATION} \
	   	--target=${TARGET} \
	   	--preprocessor-definitions=${PREPROCESSOR_DEFINITIONS} \
		--project-path=${PROJECT_PATH} \
	   	--test-script=${TEST_SCRIPT} \
	   	--template-path=${TEMPLATE_PATH}

clean:
	xcodebuild clean
