import json
import os
import sys
from github import Github
import requests
import datetime
from urllib.parse import unquote

def flatten_name(name):
    return "".join([c for c in name if c.isalpha()]).lower()
    
def format_link(href, display):
    return f"[{display}]({href})"

def parse_name(url):
    return unquote(url.split('/')[-1].replace('.ipa', '').replace('.', ' '))

def fetch_version():
    # return os.environ["version"] maybe?
    # TODO: error handling / retries
    url = "https://raw.githubusercontent.com/FR-FFT/AgarioMods/refs/heads/main/version.txt"
    response = requests.get(url)
    return response.text.strip()

def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def construct_scarlet_repo_txt(asset_upload_urls, version):
    repo_name = "FR-FFT's Agar.io Mod collection"
    # repo_icon = "https://avatars.githubusercontent.com/u/136937878?v=4"
    repo_json = {
        "META": {
            "repoName": repo_name,
            # "repoIcon": repo_icon,
        },
        "Agar.io mods": [{
            "name": "Agar.io",
            "version": version,
            "down": asset_upload_url,
            "dev": "",
            "category": "Agar.io Mods",
            "description": f"Agar.io mods for version {version}",
            "bundleID": f"com.miniclip.agar.io.{flatten_name(parse_name(asset_upload_url))}",
            "appstore": "com.miniclip.agar.io",
            "contact": {
                "web": "",
                "PayPal": ""
            }
        } for asset_upload_url in asset_upload_urls]
    }
    return json.dumps(repo_json, indent=4)

def construct_esign_repo_txt(asset_upload_urls, version):

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
                "name": "Agar.io",
                "bundleIdentifier": f"com.miniclip.agar.io.{flatten_name(parse_name(asset_upload_url))}",
                "developerName": "",
                "version": version,
                "versionDate": get_current_date(),
                "downloadURL": asset_upload_url,
                "localizedDescription": f"Agar.io mod for version {version}",
                "iconURL": "https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/89/1b/8a/891b8aec-15e9-98b3-c9bd-8e1985729a91/AppIcon-0-0-1x_U007emarketing-0-7-0-0-85-220.png/434x0w.webp",
                "tintColor": "FF0000",
                "size": 40000000,
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

def upload_assets_and_update_files(repo_name, token, tag_name, release_name, body, folder):
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



    scarlet_repo_txt = construct_scarlet_repo_txt(asset_upload_urls, version)
    try:
        file = repo.get_contents("scarlet_repo.json", ref="main")
        repo.update_file("scarlet_repo.json", "Updated Scarlet repo", scarlet_repo_txt, file.sha, branch="main")
    except:
        repo.create_file("scarlet_repo.json", "Created Scarlet repo", scarlet_repo_txt, branch="main")

    esign_repo_txt = construct_esign_repo_txt(asset_upload_urls, version)
    try:
        file = repo.get_contents("esign_repo.json", ref="main")
        repo.update_file("esign_repo.json", "Updated eSign repo", esign_repo_txt, file.sha, branch="main")
    except:
        repo.create_file("esign_repo.json", "Created eSign repo", esign_repo_txt, branch="main")


    # Update README.md
    with open("README_template.md", "r") as f:
        readme_template = f.read()
    modlist="\n".join([f"| {parse_name(asset_upload_url)} | {format_link(asset_upload_url, 'Direct download')} / {format_link('https://fwuf.in/#/scarlet://install='+asset_upload_url, 'Scarlet')} / {format_link('https://fwuf.in/#/sideloadly:'+asset_upload_url, 'Sideloadly')} |" for asset_upload_url in asset_upload_urls])

    try:
        file = repo.get_contents("README.md", ref="main")
        repo.update_file("README.md", "Updated README", readme_template.format(version=version, update_date=get_current_date(), modlist=modlist), file.sha, branch="main")
    except:
        repo.create_file("README.md", "Created README", readme_template.format(version=version, update_date=get_current_date(), modlist=modlist), branch="main")


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Usage: python upload_mods.py <token> [<release_title> <release_body>]")
        sys.exit(1)
    version = fetch_version()
    repo_name = os.environ['GITHUB_REPOSITORY']
    token = sys.argv[1]
    tag_name = f"v{version}"
    release_name = sys.argv[2] if len(sys.argv) > 2 else f"Agar.io Mods v{version}"
    body = sys.argv[3] if len(sys.argv) > 3 else f"Mods for Agar.io version {version}"
    folder = "./ModifiedIPAs"

    upload_assets_and_update_files(repo_name, token, tag_name, release_name, body, folder)
