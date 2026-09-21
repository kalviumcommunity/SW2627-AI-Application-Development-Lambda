from io import BytesIO
import os

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from pypdf import PdfReader


load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_drive_service():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES,
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def list_pdfs_in_folder(service, folder_id):
    query = (
        f"'{folder_id}' in parents "
        "and mimeType = 'application/pdf' "
        "and trashed = false"
    )

    files = []
    page_token = None

    while True:
        response = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token,
            pageSize=100,
        ).execute()

        files.extend(response.get("files", []))

        page_token = response.get("nextPageToken")

        if not page_token:
            break

    return files


def download_pdf(service, file_id):
    request = service.files().get_media(fileId=file_id)

    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False

    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)

    return fh


def extract_pdf_text(pdf_file):
    reader = PdfReader(pdf_file)

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return "\n\n".join(pages)


def read_pdfs_from_folder(folder_id):
    service = get_drive_service()

    pdfs = list_pdfs_in_folder(service, folder_id)

    documents = []

    for pdf in pdfs:
        print(f"Reading: {pdf['name']}")

        pdf_file = download_pdf(service, pdf["id"])
        text = extract_pdf_text(pdf_file)

        documents.append({
            "file_id": pdf["id"],
            "file_name": pdf["name"],
            "text": text,
        })

    return documents


if __name__ == "__main__":
    folder_id = os.environ.get("DRIVE_COD_FOLDER_ID")

    if not folder_id:
        raise ValueError("DRIVE_COD_FOLDER_ID is not set")

    documents = read_pdfs_from_folder(folder_id)

    for document in documents:
        print("=" * 80)
        print(document["file_name"])
        print("=" * 80)
        print(document["text"][:2000])