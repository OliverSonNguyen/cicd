import re
import json
import sys
import os
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
        self.flavor = parts[2]
        self.buildType = parts[3] if len(parts) > 3 else 'full'


    def getVersionName(self) -> str:
        return self.versionName
    
    def getVersionCode(self) -> int:
        return self.versionCode
    
    def getFlavor(self) -> str:
        return self.flavor
    
    def getBuildType(self) -> str:
        return self.buildType
    
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

    


if __name__ == "__main__":
    main()