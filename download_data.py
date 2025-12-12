import requests
import os
import sys

# --- Configuration (Based on the repository) ---
GITHUB_USER = "numan-developer-2"
GITHUB_REPO = "RAG-"
GITHUB_BRANCH = "main"
LOCAL_DATA_DIR = "data"

# List of specific documents to download
DOCUMENT_FILENAMES = [
    "Client_Case_Studies.pdf",
    "Client_Onboarding_Guide.pdf",
    "Company_Overview_Detailed.pdf",
    "Data_Privacy_GDPR_Policy.pdf",
    "Diversity_Inclusion_Policy.pdf",
    "Employee_Handbook_Detailed.pdf",
    "HR_Policy_Detailed.pdf",
    "IT_Security_Policy.pdf",
    "Sales_Playbook_Detailed.pdf",
    "Team_Structure_Roles.pdf",
    "Training_Development_Programs.pdf",
]
# -----------------------------------------------------------

def download_documents():
    """
    Downloads the specified documents from the GitHub raw content URL 
    and saves them to the local data directory.
    """
    try:
        # Create the data directory if it doesn't exist
        os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
    except OSError as e:
        print(f"Error: Could not create directory {LOCAL_DATA_DIR}. {e}")
        sys.exit(1)

    print(f"Starting document download into '{LOCAL_DATA_DIR}'...")

    for filename in DOCUMENT_FILENAMES:
        raw_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{filename}"
        local_path = os.path.join(LOCAL_DATA_DIR, filename)

        print(f"  [INFO] Attempting to download: {filename}")
        
        try:
            # Send a GET request to the raw file URL
            response = requests.get(raw_url, stream=True)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

            # Write the content to the local file
            with open(local_path, 'wb') as f:
                # Use iter_content for memory-efficient handling of large files
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"  [SUCCESS] Saved to {local_path}")
            
        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Failed to download {filename}. Reason: {e}")
            print("  (Check file name, path, and repository details.)")

    print("\n[INFO] Data download process complete.")

if __name__ == "__main__":
    download_documents()