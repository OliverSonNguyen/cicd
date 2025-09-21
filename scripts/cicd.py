import re
import json
import sys
class TagParse:
    def __init__(self, repoTag: str):
        """Init with a git tag"""
        print(f"Initializing with tag: '{repoTag}'")
        
        cleanTag = self.cleanTag(repoTag)
        self.tag = cleanTag
        self.parseTag()


    def cleanTag(self, repoTag: str)-> str:
        return tag[1:] if repoTag.startswith("v") else repoTag   

    def parseTag(self):
        print(f"do parseTag:{self.tag}")
        parts = self.tag.split("-")
        print(f"parts:{parts}")
        if (len(parts) < 2):
            print("Error wrong format")
        
        self.versionName = parts[0]
        self.versionCode = parts[1]
        self.flavor = parts[2]
        self.buildType = parts[3] if len(parts) > 3 else 'full'


    def getVersionName(self) -> str:
        return self.versionName
    
    def getVersionCode(self) -> int:
        return self.versionCode
    
    def getFlavor(self) -> str:
        return self.flavor
    
    def getBuildTye(self) -> str:
        return self.buildType
    


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 cicd.py <tag>")
        print("Example: python3 cicd.py 1.0.0-100-adyen")
        sys.exit(1)
    
    tag = sys.argv[1]
    parser = TagParse(tag)    
    print(f"versionName={parser.getVersionName()}")
    print(f"versionCode={parser.getVersionCode()}")     
    print(f"flavor={parser.getFlavor()}")     
    print(f"buildType={parser.getBuildTye()}")     
