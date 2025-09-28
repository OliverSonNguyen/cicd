from datetime import datetime
from cicd import TagParse
import os, sys, time, json, argparse, requests
from datetime import datetime

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
class SlackReleaseNotify:
    def __init__(self, tag:str):
    
        # if not self.slackWebhook:
        #     self.slackWebhook = SLACK_WEBHOOK

        self.tag = tag
        self.releaseUrl = 'https://github.com/OliverSonNguyen/cicd/actions/runs/18038621235/artifacts/4115189904'
        self.buildUrl = 'https://github.com/OliverSonNguyen/cicd/actions/runs/18038621235'
        self.tag_parser = TagParse(self.tag)

        self.versionName = self.tag_parser.versionName
        self.versionCode = self.tag_parser.versionCode
        self.flavor = self.tag_parser.flavor
        self.environment = self.tag_parser.environment
        self.shouldSubmit = self.tag_parser.shouldSubmit
        self.displayVersion = f"v{self.versionCode}-{self.versionCode}"

        self.changelog = "n/a"
        self.full = ''
        self.stripe = ''
        self.slackWebhook = ''

        

        print(f"Parsed tag info:")
        print(f"  Version Name: {self.versionName}")
        print(f"  Version Code: {self.versionCode}")
        print(f"  Flavor: {self.flavor}")
        print(f"  Environment: {self.environment}")
        print(f"  Should Submit: {self.shouldSubmit}")
       

        #parse tag again here
        # if not self.slackWebhook:
        #     print(f"no slackWebhook ")
        #     #self.slackWebhook = "https://hooks.slack.com/services/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"


    def sendSlackWebhook(self, jsonMessage: str):

        print(f"slackWebhook:{self.slackWebhook}")
        print(f"jsonMessage:{jsonMessage}")

        if not self.slackWebhook:
            print(f"no params for slackWebhook - default SLACK_WEBHOOK ")
            self.slackWebhook = SLACK_WEBHOOK
        response = requests.post(self.slackWebhook, json=jsonMessage)
        if response.status_code != 200:
            print(f"Failed to send Slack message: {response.text}")
            return False
        
        print(f"✅ Slack notification sent successfully!")
        return True   
    
    def sendToSlack(self):
        if self.environment == 'prd' or self.environment == 'production':
            self.sendPrdBuildToSlack()
        else:
            self.sendStgBuildToSlack()    

    def get_built_apks_from_environment(self):
        """Get list of actually built APKs from environment variables"""
        
       
        
        # Check environment variables set by your cicd.py script
        apk_paths = {
            "full": os.getenv("DOWNLOAD_RELEASE_FULL_UNIVERSAL_PATH") or self.full or 'n/a',
            "stripe": os.getenv("DOWNLOAD_RELEASE_STRIPE_PATH") or self.stripe or 'n/a', 
            "adyen": os.getenv("DOWNLOAD_RELEASE_ADYEN_UNIVERSAL_PATH"),
            "ingenico": os.getenv("DOWNLOAD_RELEASE_INGENICO_PATH")
        }
        
        valid_apks = {}

       
        # Loop through each APK type and path
        for apk_type, path in apk_paths.items():
            # Check if path exists and is not empty
            if path and path.strip():
                # Add to our valid APKs dictionary
                valid_apks[apk_type] = path

        return valid_apks



    

    def sendStgBuildToSlack(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        # print(f"webhook:{self.slackWebhook}")
        # print(f"full:{self.full}")
        # print(f"stripe:{self.stripe}")
        available_apks = self.get_built_apks_from_environment()
        message = {
        "text": f"🚀 HitPay Android {self.displayVersion} on {self.environment} is ready!",
        "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚀 HitPay Android {self.displayVersion} Ready!"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Environment:* {self.environment}"},
                        {"type": "mrkdwn", "text": f"*Version:* {self.displayVersion}"},
                        {"type": "mrkdwn", "text": f"*Submit:* {self.shouldSubmit}"}
                    ]
                }, 
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📱 QA Team - APKs are ready for download and testing!*\n\n" +
                                f"*Change logs {self.displayVersion}*\n" +
                                f"{self.changelog}:\n\n"
                                f"*Available builds:*\n"
                               
                    }
                },
            ]
        }
         # APK display names mapping
        apk_display_names = {
            "full": "📦 Normal Android",
            "stripe": "🔷 Stripe Terminal",
            "adyen": "🟢 Adyen", 
            "ingenico": "🔶 Ingenico"
        }
        

        if available_apks:
            download_elements = []
            
            # Loop through the dictionary (apk_type: url)
            for apk_type, url in available_apks.items():
                display_name = apk_display_names.get(apk_type, apk_type.title())
                
                download_elements.append({
                    "type": "button",
                    "text": {"type": "plain_text", "text": display_name},
                    "url": url,
                    # "style": "primary" if apk_type == "full" else None
                })
            
            # Add the download buttons to the message
            message["blocks"].append({
                "type": "actions",
                "elements": download_elements
            })


        self.sendSlackWebhook(message)




    def sendPrdBuildToSlack(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        print(f"webhook:{self.slackWebhook}")
        print(f"full:{self.full}")
        print(f"stripe:{self.stripe}")
        available_apks = self.get_built_apks_from_environment()
        message = {
        "text": f"🚀 HitPay Android Release {selfdisplayVersion} on {self.environment} is ready!",
        "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚀 HitPay Android Release {selfdisplayVersion} on {self.environment} is ready!"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Environment:* {self.environment}"},
                        {"type": "mrkdwn", "text": f"*Version:* {self.displayVersion}"},
                        {"type": "mrkdwn", "text": f"*Submit:* {self.shouldSubmit}"}
                    ]
                }, 
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📱 QA Team - APKs are ready for download and testing!*\n\n" +
                                f"*Change logs {self.displayVersion}*\n" +
                                f"{self.changelog}:\n\n"
                                f"*Available builds:*\n"
                               
                    }
                },
            ]
        }
         # APK display names mapping
        apk_display_names = {
            "full": "📦 Normal Android",
            "stripe": "🔷 Stripe Terminal",
            "adyen": "🟢 Adyen", 
            "ingenico": "🔶 Ingenico"
        }
        

        if available_apks:
            download_elements = []
            
            # Loop through the dictionary (apk_type: url)
            for apk_type, url in available_apks.items():
                display_name = apk_display_names.get(apk_type, apk_type.title())
                
                download_elements.append({
                    "type": "button",
                    "text": {"type": "plain_text", "text": display_name},
                    "url": url,
                    # "style": "primary" if apk_type == "full" else None
                })
            
            # Add the download buttons to the message
            message["blocks"].append({
                "type": "actions",
                "elements": download_elements
            })


        self.sendSlackWebhook(message)


    def sendDownloadTest(self, full:str, stripe:str):
        self.full = full,
        self.stripe = stripe


    
def main():
    parser = argparse.ArgumentParser(description='Send Slack notification for Android release')
    parser.add_argument('tag', help='Git tag (e.g., v6.6.6-666-stripe-stg-submit=true)')
    parser.add_argument('--changelog',help='Change log')
    parser.add_argument('--send', action='store_true', help='Actually send the notification')
    parser.add_argument('--webhook', help='Slack webhook URL')
    parser.add_argument('--full', help='Full APK download URL')
    parser.add_argument('--stripe', help='Stripe APK download URL') 

    args = parser.parse_args()


    # tag = sys.argv[1]
    # options = sys.argv[2]
    # webHook = sys.argv[3]
    # full = sys.argv[4]
    # stripe = sys.argv[5]
    
    print(f"slackReleaseNotify tag:{args.tag}")
    print(f"slackReleaseNotify webHook:{args.webhook}")
    print(f"slackReleaseNotify full:{args.full}")
    print(f"slackReleaseNotify stripe:{args.stripe}")
    print(f"slackReleaseNotify changelog:{args.changelog}")
    

    slackReleaseNotify = SlackReleaseNotify(tag=args.tag)
    if args.webhook:
        slackReleaseNotify.slackWebhook = args.webhook
    if args.changelog:
        slackReleaseNotify.changelog = args.changelog
    if args.full:
        slackReleaseNotify.full = args.full
    if args.stripe:
        slackReleaseNotify.stripe = args.stripe
    
    if args.send:
        print("📤 Sending Slack notification...")
        slackReleaseNotify.sendStgBuildToSlack()
    
# python3 scripts/slack_release_notify.py v6.6.6-666-stripe-stg-submit=true \
#           --send \
#           --webhook "https://hooks.slack.com/services/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" \
#           --full "https://github.com/OliverSonNguyen/cicd/actions/runs/18038621235/artifacts/4115189904" \
#           --stripe "https://github.com/OliverSonNguyen/cicd/actions/runs/18038621235/artifacts/4115189904" \
#           --changelog "Improve loading time \n New HomePage"


# python3 scripts/slack_release_notify.py v6.6.6-666-stripe-stg-submit=true \
#           --send
        #   --changelog "Improve loading time \n New HomePage"
if __name__ == "__main__":
    main()            