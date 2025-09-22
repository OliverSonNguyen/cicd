import re
import json
import sys
import os
import glob
class TagParse:
    def __init__(self, repoTag: str):
        """Init with a git tag"""
        print(f"Initializing with tag: '{repoTag}'")
        
        cleanTag = self.cleanTag(repoTag)
        self.tag = cleanTag
        self.parseTag()


    def cleanTag(self, repoTag: str)-> str:
        return repoTag[1:] if repoTag.startswith("v") else repoTag   

    def parseTag(self):
        print(f"do parseTag:{self.tag}")
        parts = self.tag.split("-")
        print(f"parts:{parts}")
        if (len(parts) < 2):
            print("Error wrong format")
        
        self.versionName = parts[0]
        self.versionCode = int(parts[1])
        self.flavor = parts[2] if len(parts) > 2 else 'full'
        self.buildType = parts[3] if len(parts) > 3 else 'prd'


    def getVersionName(self) -> str:
        return self.versionName
    
    def getVersionCode(self) -> int:
        return self.versionCode
    
    def getFlavor(self) -> str:
        return self.flavor
    
    def getBuildType(self) -> str:
        return self.buildType
    
    def _write_env(self, key: str, val: str):
        env_file = os.environ.get("GITHUB_ENV")
        if env_file:
            with open(env_file, "a") as f:
                f.write(f"{key}={val}\n")
    
    def setGitHubEnv(self):
        print("setGitHubEnv called")
        
        # Access instance variables using self
        print(f"Setting GitHub env for version: {self.versionName}")
        
        github_env_file = os.environ.get('GITHUB_ENV')
        if github_env_file:
            with open(github_env_file, 'a') as f:
                f.write(f"CI_VERSION_NAME={self.versionName}\n")
                f.write(f"CI_VERSION_CODE={self.versionCode}\n")
                f.write(f"CI_FLAVOR={self.flavor}\n")
                f.write(f"CI_BUILD_TYPE={self.buildType}\n")
            print("GitHub environment variables set")
        else:
            print(" Not in GitHub Actions environment")
            print(f"Would set CI_VERSION_NAME={self.versionName}")
            print(f"Would set CI_VERSION_CODE={self.versionCode}")

    def findApkPaths(self, basePath = "app/build/outputs/apk"):
        print(f"Find apk path basePath:{basePath}")
      
        # --- Full (universal) ---
        print("--------------Full-------------------")
        fullPattern = f"{basePath}/full/release/*universal*.apk"
        print(f"Find apk path fullPattern:{fullPattern}")
        fullMatches = glob.glob(fullPattern)
        if fullMatches:
            fullApkPath = fullMatches[0]
            fullApkName = os.path.basename(fullApkPath)
            print(f"Found full universal apk on tag:{self.tag} apk: {fullApkPath} - name:{fullApkName}")
            self._write_env("RELEASE_FULL_UNIVERSAL_PATH", fullApkPath)
            self._write_env("RELEASE_FULL_UNIVERSAL", fullApkName)
        else:
            print(f"Not found full universal apk on tag:{self.tag}")

        # --- Stripe (armeabi-v7a) ---
        print("--------------Stripe-------------------")
        stripePattern = f"{basePath}/apps_on_device/release/*armeabi-v7a*.apk"
        print(f"Find apk path stripePattern:{stripePattern}")
        stripeMatches = glob.glob(stripePattern)
        if stripeMatches:
            stripeApkPath = stripeMatches[0]
            stripeApkName = os.path.basename(stripeApkPath)
            print(f"Found Stripe armeabi apk on tag:{self.tag} apk: {stripeApkPath} - name:{stripeApkName}")
            self._write_env("RELEASE_STRIPE_ARMEABI_PATH", stripeApkPath)
            self._write_env("RELEASE_STRIPE_ARMEABI", stripeApkName)
        else:
            print(f"Not found Stripe armeabi apk on tag:{self.tag}")

        # --- Adyen (universal) ---
        print("--------------Adyen-------------------")
        adyenPattern = f"{basePath}/apps_on_device_adyen/release/*universal*.apk"
        print(f"Find apk path adyenPattern:{adyenPattern}")
        adyenMatches = glob.glob(adyenPattern)
        if adyenMatches:
            adyenApkPath = adyenMatches[0]
            adyenApkName = os.path.basename(adyenApkPath)
            print(f"Found Adyen universal apk on tag:{self.tag} apk: {adyenApkPath} - name:{adyenApkName}")
            self._write_env("RELEASE_ADYEN_UNIVERSAL_PATH", adyenApkPath)
            self._write_env("RELEASE_ADYEN_UNIVERSAL", adyenApkName)
        else:
            print(f"Not found Adyen universal apk on tag:{self.tag}")

        # --- Ingenico (armeabi-v7a) ---
        print("--------------Ingenico-------------------")
        ingenicoPattern = f"{basePath}/apps_on_device_ingenico/release/*armeabi-v7a*.apk"
        print(f"Find apk path ingenicoPattern:{ingenicoPattern}")
        ingenicoMatches = glob.glob(ingenicoPattern)
        if ingenicoMatches:
            ingenicoApkPath = ingenicoMatches[0]
            ingenicoApkName = os.path.basename(ingenicoApkPath)
            print(f"Found Ingenico armeabi apk on tag:{self.tag} apk: {ingenicoApkPath} - name:{ingenicoApkName}")
            self._write_env("RELEASE_INGENICO_ARMEABI_PATH", ingenicoApkPath)
            self._write_env("RELEASE_INGENICO_ARMEABI", ingenicoApkName)
        else:
            print(f"Not found Ingenico armeabi apk on tag:{self.tag}")    
        


    
    def getGradleCommand(self) -> str: 
        print(f"Build apks tag:{self.tag}")
        self.parseTag()

        gradleCmd = ""
        print(f"Build apk flavor:{self.flavor} buildType:{self.buildType}")
        
        if self.flavor == "full":
            gradleCmd = "assembleFullRelease"
        elif self.flavor == "adyen":
            gradleCmd = "assembleApps_on_deviceAdyenRelease"
        elif self.flavor == "stripe":
            gradleCmd = "assembleApps_on_deviceRelease"
        elif self.flavor == "ingenico":
            gradleCmd = "assembleApps_on_deviceIngenicoRelease"
        elif self.flavor == "all":
            gradleCmd = "assembleFullRelease assembleApps_on_deviceAdyenRelease assembleApps_on_deviceRelease assembleApps_on_deviceIngenicoRelease"
        else:
            print(f"Unknown build type: {self.buildType}, defaulting to full")
            gradleCmd = "assembleFullRelease"
        
        print(f"Gradle command: {gradleCmd}")
        return gradleCmd
    
    def buildApks(self): 
        cmd = self.getGradleCommand()
        print(f"buildApks gradleComand :{cmd}")

        finalGradlew = f"./gradlew {cmd} -PversionName={self.versionName} -PversionCode={self.versionCode}"
        print(f"buildApks finalGradlew :{finalGradlew}")

    def generateGradleCmd(self): 

        self.findApkPaths() 

        cmd = self.getGradleCommand()
        finalGradlew = f"./gradlew --no-daemon --stacktrace --console=plain {cmd} -PversionName={self.versionName} -PversionCode={self.versionCode}"
        print(f"generateGradleCmd finalGradlew :{finalGradlew}") 
         
        self._write_env("CI_GRADLE_COMMAND", finalGradlew)


            

    

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 cicd.py <tag>")
        print("Example: python3 cicd.py 1.0.0-100-adyen")
        sys.exit(1)

    tag = sys.argv[1]
    options = sys.argv[2] if len(sys.argv) > 2 else ""
    parser = TagParse(tag)    
    print(f"versionName={parser.getVersionName()}")
    print(f"versionCode={parser.getVersionCode()}")     
    print(f"flavor={parser.getFlavor()}")     
    print(f"buildType={parser.getBuildType()}")
    print(f"Options:{options}")

    if '--github-action' in options:
        parser.setGitHubEnv()

    if '--apk-paths' in options:
        parser.findApkPaths()    

    if '--apk-build' in options:
        parser.buildApks()   

    if '--apk-cmd' in options:
        parser.generateGradleCmd()

    


if __name__ == "__main__":
    main()