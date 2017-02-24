1. Requirements:
a. VE_Tests from git
b. python 2.7
c. pip (for latest version: “sudo pip install --upgrade pip”)
d. install appium from appium.io
e. ios only:
    1. install homebrew by:
        ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    2. ideviceinstaller
        brew install libimobiledevice  
        brew install --HEAD ideviceinstaller
    3. ios-deploy
    	brew install node
	npm install -g ios-deploy

2. Installation (terminal)
a. setup environment: (console in VE-Tests)

sudo pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt

b. Copy appium.ini to VE-Tests/tests

Running tests:
a. if not in virtual env: source venv/bin/activate
a. cd tests
b. py.test KD/iOS/e2e_tests/test_zaplist.py -s


c. github wiki
https://wiki.cisco.com/display/VIDEOSCAPE/github+setup#Githubsetup-Dailywork

