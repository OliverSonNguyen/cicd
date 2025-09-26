import os, sys, time, json, argparse, requests

# https://docs.stripe.com/terminal/features/apps-on-devices/submit?dashboard-or-api=api

STRIPE_KEY = os.getenv("STRIPE_API_KEY")  # sk_live_... or sk_test_...
API_VER   = "2017-04-06; terminal_deploy_api_beta=v1"

BASE_API  = "https://api.stripe.com/v1"
FILES_API = "https://files.stripe.com/v1"

PACKAGE_NAME = 'com.hit_pay.hitpay'
APP_NAME = 'Hitpay App'

DEVICE_LIST = {}


PRODUCTION_CONFIG = {
    "device_asset": "tmda_5300mBBiU0006LHxTl711AMHowMCIhZ",
    "compatible_devices": [
        "stripe_s700", 
        "stripe_s710", 
        "bbpos_wisepos_e"
    ],
    "review_instructions": "raymondvictorioh@gmail.com / Hitpay123! > HitPay Store",
    "review_emails": [
        "raymond@hit-pay.com", 
        "aditya@hit-pay.com", 
        "nitin@hit-pay.com",
        "son@hit-pay.com",
    ]
}

STAGING_CONFIG = {
    "device_asset": "tmda_53009IWCl0005TijGb311AMHowMCIhZ",
    "compatible_devices": [
        "stripe_s700", "stripe_s700_devkit",
        "stripe_s710", "stripe_s710_devkit", 
        "bbpos_wisepos_e", "bbpos_wisepos_e_devkit"
    ],
    "review_instructions": "hitpaydemotest@yopmail.com\n / Hitpay123!",
    "review_emails": ["raymond@hit-pay.com, son@hit-pay.com"]
}

# Map environment names to their configs
ENV_CONFIGS = {
    "production": PRODUCTION_CONFIG,
    "prd": PRODUCTION_CONFIG,
    "staging": STAGING_CONFIG,
    "stg": STAGING_CONFIG
}
ENV_ALIASES = {
    "prd": "production",
    "production": "production",
    "stg": "staging",
    "staging": "staging",
}

class StripeUploadManager:
    def __init__(self, apkPath, env: str):
        self.apkPath = apkPath
        self.env = ENV_ALIASES[env]
        self.config = ENV_CONFIGS[self.env]
        self.showConfig()

    def showConfig(self):
        print(f"apkPath:{self.apkPath}")  
        print(f"env:{self.getEnv()}")    
        print(f"header:{self.getheader()}")
        print(f"getStripeInstructions:{self.getStripeInstructions()}")
        print(f"auth:{self.getAuth()}")
        

    def getEnv(self) -> str:
        return self.env    

    def getAuth(self) -> str:
        if not STRIPE_KEY:
            print(f"Missing STRIPE_SECRET_KEY env.")
            return ""

        return (STRIPE_KEY, "")
    
    def getheader(self) -> str:
        h = {"Stripe-Version": API_VER}
        return h
    
    def getOrCreateDeviceAsset(self) -> str:
        # assetId = self.config.get("device_asset")
        # if assetId:
        #     return assetId
        
        exsitAsset = self.findExstingDeviceAsset()
        if exsitAsset:
            print(f"Find exsitAsset {exsitAsset['id']}")
            return exsitAsset
        
        print(f"Can not find exsitAsset")
        return None
        
        #if not create a new
        # data = {
        #     'name': APP_NAME,
        #     'type': 'android_apk',
        #     'android_apk[package_name]': PACKAGE_NAME,
        #     'livemode':'false'
        # }

        # print(f"Creating device asset for package: {PACKAGE_NAME}")


        # response = requests.post(
        #     f"{BASE_API}/terminal/device_assets",
        #     auth= self.getAuth(),
        #     headers=self.getheader(),
        #     data=data
        # )

        # if response.status_code == 200:
        #     deviceAsset = response.json()
        #     print(f"Created device asset: {deviceAsset['id']}")
        #     return deviceAsset
        # else:
        #     print(f"Failed to create device asset: {response.status_code}")
        #     print(f"Response: {response.text}")
        #     return None
    
    def findExstingDeviceAsset(self):
        response = requests.get(
            f"{BASE_API}/terminal/device_assets",
            auth= self.getAuth(),
            headers=self.getheader()
        )
        if response.status_code == 200:
            assets = response.json().get('data', [])
            for asset in assets:
                if (asset.get('android_apk', {}).get('package_name') == PACKAGE_NAME):
                    return asset
        else:
            print(f"Failed to list device assets: {response.status_code}")
            return None

    def uploadApk(self, apkPath: str) -> str:
        print(f"Upload apk path:{apkPath}")
        if not os.path.exists(apkPath):
           sys.exit(f"APK not found: {apkPath}")

        file = {
            "file": (os.path.basename(apkPath), open(apkPath, "rb"), 
                     "application/vnd.android.package-archive"
                     ),                     
        }
        data = {"purpose": "terminal_android_apk"}   

        response = requests.post(
                f"{BASE_API}/files",
                auth=self.getAuth(),
                files=file,
                data=data,
        )

        if response.status_code == 200:
            file_obj = response.json()
            print(f"File uploaded successfully: {file_obj['id']}")
            return file_obj
        else:
            print(f"Failed to upload file: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        

    def getStripeInstructions(self)->str:
        return self.config["review_instructions"]
        
    def getStripeSupportDevice(self)->list:
        return self.config["compatible_devices"]


    def uploadReleaseToDashBoard(self, deviceAssetId : str, apkUploadedId: str):
        print(f"uploadReleaseToDashBoard deviceAssetId:{deviceAssetId} - apkUploadedId:{apkUploadedId}")

        form_data = []
        
        
        form_data.append(("device_asset", deviceAssetId))
        form_data.append(("file", apkUploadedId))
        
        # Add all compatible device types
        for device_type in self.config["compatible_devices"]:
            form_data.append(("compatible_device_types[]", device_type))
        
        # Add review instructions if they exist
        if self.config.get("review_instructions"):
            form_data.append(("app_review[instructions]", self.config["review_instructions"]))
        
        # Add review emails
        for email in self.config.get("review_emails", []):
            form_data.append(("app_review[email_addresses][]", email))
        
        # Make the API request
        # response = requests.post(
        #     f"{BASE_API}/terminal/device_asset_versions",
        #     auth=self.get_auth(),
        #     headers=self.get_headers(),
        #     data=form_data
        # )
       

       

        # if response.status_code == 200:
        #     assetVersion = response.json()
        #     print(f"uploadReleaseToDashBoard: {assetVersion['id']}")
        #     return assetVersion
        # else:
        #     print(f"Failed to uploadReleaseToDashBoard: {response.status_code}")
        #     print(f"Response: {response.text}")
        #     return None

    def push(self):
        assetId = self.getOrCreateDeviceAsset()

        # fileId = self.uploadApk(apkPath=self.apkPath)
        fileId = 'not yet'

        print(f"Push assetId:{assetId} - fileId:${fileId}")
       # self.uploadReleaseToDashBoard(assetId, fileId)





def main():
    if len(sys.argv) < 2:
        print("sys.argv) < 2")
        sys.exit(1)

    apkPath = sys.argv[1]
    env = sys.argv[2] if len(sys.argv) > 2 else 'stg'
    options = sys.argv[3] if len(sys.argv) > 3 else ""

    stripeUpload = StripeUploadManager(apkPath, env)    
    print(f"apkPath={apkPath}")
    print(f"env={env}")
    print(f"Options:{options}")

    if '--push' in options:
        stripeUpload.push()


# python3 scripts/stripe_uploader.py path --prd --push
if __name__ == "__main__":
    main()