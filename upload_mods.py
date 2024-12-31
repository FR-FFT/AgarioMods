import os
import sys
from github import Github

def upload_assets(repo_name, token, tag_name, release_name, body, folder):
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
    for file_name in os.listdir(folder):
        if file_name.endswith(".ipa"):
            file_path = os.path.join(folder, file_name)
            print(f"Uploading {file_name}...")
            try:
                release.upload_asset(
                    path=file_path,
                    name=file_name,
                    content_type="application/octet-stream",
                )
                print(f"Uploaded {file_name}.")
            except Exception as e:
                print(f"Failed to upload {file_name}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python upload_mods.py <repo_name> <token> <tag_name> <release_name> <body> <folder>")
        sys.exit(1)

    repo_name = sys.argv[1]
    token = sys.argv[2]
    tag_name = sys.argv[3]
    release_name = sys.argv[4]
    body = sys.argv[5]
    folder = sys.argv[6]

    upload_assets(repo_name, token, tag_name, release_name, body, folder)
