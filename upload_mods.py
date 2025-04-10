import json
import os
import sys
from github import Github
import requests
import datetime
from urllib.parse import unquote, quote_plus as uriencode

folder = "./ModifiedIPAs"


def flatten_name(name):
    return "".join([c for c in name if c.isalpha() or c.isdigit()]).lower()
    
def format_link(href, display):
    return f"[{display}]({href})"

def parse_name(url):
    return unquote(url.split('/')[-1].replace('.ipa', '').replace('.', ' '))

def get_config(mods_config, asset_upload_url, key):
    return mods_config[parse_name(asset_upload_url)][key] if parse_name(asset_upload_url) in mods_config and key in mods_config[parse_name(asset_upload_url)] else ""

def fetch_version():
    # return os.environ["version"] maybe?
    # TODO: error handling / retries
    url = "https://raw.githubusercontent.com/FR-FFT/AgarioMods/refs/heads/main/version.txt"
    response = requests.get(url)
    return response.text.strip()
    
def get_ymd_date():
    today = datetime.datetime.now()
    return today.strftime("%Y-%M-%d")

def get_current_date():
    today = datetime.datetime.now()
    # Get day with ordinal suffix (1st, 2nd, 3rd, 4th, etc.)
    day = today.strftime("%d").lstrip("0")  # Remove leading zero
    suffix = "th"  # Default suffix
    if day.endswith("1") and not day.endswith("11"):
        suffix = "st"
    elif day.endswith("2") and not day.endswith("12"):
        suffix = "nd"
    elif day.endswith("3") and not day.endswith("13"):
        suffix = "rd"
    return f"{day}{suffix} {today.strftime('%B %Y')}"

def construct_scarlet_repo_txt(asset_upload_urls, version, mods_config):
    repo_name = "FR-FFT's Agar.io Mod collection"
    # repo_icon = "https://avatars.githubusercontent.com/u/136937878?v=4"
    repo_json = {
        "META": {
            "repoName": repo_name,
            # "repoIcon": repo_icon,
        },
        "Agar.io mods": [{
            "name": get_config(mods_config, asset_upload_url, 'app_name'),
            "version": version,
            "icon": f"https://raw.githubusercontent.com/FR-FFT/AgarioMods/refs/heads/main/icons/{uriencode(parse_name(asset_upload_url)).replace('+%2B+', '%20%2B%20')}.png",
            "down": asset_upload_url,
            "dev": get_config(mods_config, asset_upload_url, 'developer'),
            "category": "Agar.io Mods",
            "description": get_config(mods_config, asset_upload_url, 'description'),
            "bundleID": f"com.miniclip.agar.io.{flatten_name(parse_name(asset_upload_url))}",
            "appstore": "com.miniclip.agar.io", # used to fetch screenshots
            "contact": {
                "web": "",
                "PayPal": ""
            }
        } for asset_upload_url in asset_upload_urls]
    }
    return json.dumps(repo_json, indent=4)

def construct_esign_repo_txt(asset_upload_urls, version, mods_config):

    repo_name = "FR-FFT's Agar.io Mod collection"
    # repo_icon = "https://avatars.githubusercontent.com/u/136937878?v=4"
    repo_json = {
        "name": repo_name,
        "identifier": "fr-fft.github.io",
        # "iconURL": repo_icon,
        "website": "https://github.com/FR-FFT/AgarioMods",
        "sourceURL": "https://raw.githubusercontent.com/FR-FFT/AgarioMods/refs/heads/main/esign_repo.json",
        "apps": [
            {
                "name": get_config(mods_config, asset_upload_url, 'app_name'),
                "bundleIdentifier": f"com.miniclip.agar.io.{flatten_name(parse_name(asset_upload_url))}",
                "developerName": get_config(mods_config, asset_upload_url, 'developer'),
                "version": version,
                "versionDate": get_ymd_date(),
                "downloadURL": asset_upload_url,
                "localizedDescription": get_config(mods_config, asset_upload_url, 'description'),
                "iconURL": f"https://raw.githubusercontent.com/FR-FFT/AgarioMods/refs/heads/main/icons/{uriencode(parse_name(asset_upload_url)).replace('+%2B+', '%20%2B%20')}.png",
                "tintColor": "FF0000",
                "size": os.path.getsize(f"{folder}/{parse_name(asset_upload_url)}.ipa"),
                "screenshotURLs": [
                    
                ],
                "appPermissions": {
                      "entitlements": [
                        "com.apple.developer.associated-domains",
                        "aps-environment",
                        "com.apple.developer.applesignin"
                      ],
                      "privacy": {
                        "NSUserTrackingUsage-Description": "App tracks the user."
                      }
                    }
                }
            for asset_upload_url in asset_upload_urls
        ]
    }
    return json.dumps(repo_json, indent=4)

def upload_assets_and_update_files(repo_name, token, tag_name, release_name, body, folder, mods_config):
    # Authenticate with GitHub
    g = Github(token)
    repo = g.get_repo(repo_name)

    # Check if the release already exists
    try:
        release = repo.get_release(tag_name)
        print(f"Release {tag_name} already exists.")
    except:
        # Create the release if it doesn't exist
        release = repo.create_git_release(
            tag=tag_name,
            name=release_name,
            message=body,
            draft=False,
            prerelease=False,
        )
        print(f"Created release {tag_name}.")

    # Upload assets

    # First upload agario.ipa
    print("Uploading Agario.ipa...")
    try:
        release.upload_asset(
            path="downloads/Agario.ipa",
            name="Agario.ipa",
            content_type="application/octet-stream",
        )
        print("Uploaded Agario.ipa.")
    except Exception as e:
        print(f"Failed to upload Agario.ipa: {e}")

    # now the mods
    asset_upload_urls = []
    existing_assets = {asset.name.replace('.ipa', '').replace('.', ' '): asset.browser_download_url for asset in release.get_assets()}
    for file_name in os.listdir(folder):
        if file_name.endswith(".ipa"):
            if file_name.replace('.ipa', '').replace('.', ' ') not in existing_assets:
                file_path = os.path.join(folder, file_name)
                print(f"Uploading {file_name}...")
                try:
                    asset =release.upload_asset(
                        path=file_path,
                        name=file_name,
                        content_type="application/octet-stream",
                    )
                    asset_upload_urls.append(asset.browser_download_url)
                    print(f"Uploaded {file_name}.")
                except Exception as e:
                    print(f"Failed to upload {file_name}: {e}")
            else:
                print(f"{file_name} already exists on the release, skipping.")
                asset_upload_urls.append(existing_assets[file_name.replace('.ipa', '').replace('.', ' ')])



    scarlet_repo_txt = construct_scarlet_repo_txt(asset_upload_urls, version, mods_config)
    try:
        file = repo.get_contents("scarlet_repo.json", ref="main")
        repo.update_file("scarlet_repo.json", "Updated scarlet repo", scarlet_repo_txt, file.sha, branch="main")
    except:
        repo.create_file("scarlet_repo.json", "Created scarlet repo", scarlet_repo_txt, branch="main")

    esign_repo_txt = construct_esign_repo_txt(asset_upload_urls, version, mods_config)
    try:
        file = repo.get_contents("esign_repo.json", ref="main")
        repo.update_file("esign_repo.json", "Updated esign repo", esign_repo_txt, file.sha, branch="main")
    except:
        repo.create_file("esign_repo.json", "Created esign repo", esign_repo_txt, branch="main")


    # Update README.md
    with open("README_template.md", "r") as f:
        readme_template = f.read()
    modlist="\n".join([f"| {parse_name(asset_upload_url)} | {format_link(asset_upload_url, 'Direct download')} / {format_link('https://fwuf.in/#/scarlet://install='+asset_upload_url, 'Scarlet')} / {format_link('https://fwuf.in/#/sideloadly:'+asset_upload_url, 'Sideloadly')} | {get_config(mods_config, asset_upload_url, 'description')} | {get_config(mods_config, asset_upload_url, 'developer')} |" for asset_upload_url in asset_upload_urls])

    try:
        file = repo.get_contents("README.md", ref="main")
        repo.update_file("README.md", "Updated README", readme_template.format(version=version, update_date=get_current_date(), modlist=modlist), file.sha, branch="main")
    except:
        repo.create_file("README.md", "Created README", readme_template.format(version=version, update_date=get_current_date(), modlist=modlist), branch="main")

    try:
        file = repo.get_contents("last_updated.txt", ref="main")
        repo.update_file("last_updated.txt", "Updated last_updated.txt", get_current_date(), file.sha, branch="main")
    except:
        repo.create_file("last_updated.txt", "Updated last_updated.txt", get_current_date(), branch="main")

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Usage: python upload_mods.py <token> [<release_title> <release_body> <release_tag>]")
        sys.exit(1)
    version = fetch_version()
    repo_name = os.environ['GITHUB_REPOSITORY']
    token = sys.argv[1]
    tag_name =  sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] else f"v{version}"
    release_name = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else f"Agar.io Mods v{version}"
    body = sys.argv[3] if len(sys.argv) > 3 else f"Mods for Agar.io version {version}"
    print("Tag name:", tag_name)
    print("Release name:", release_name)
    print("Body:", body)
    mods_config = json.load(open("config.json"))
    upload_assets_and_update_files(repo_name, token, tag_name, release_name, body, folder, mods_config)
