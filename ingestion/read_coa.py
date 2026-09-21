import google.auth
from googleapiclient.discovery import build
from io import BytesIO
import os

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from pypdf import PdfReader


class ReadCoA:
    def __init__(self):
        self.scopes = ["https://www.googleapis.com/auth/drive.readonly"]
        # Get the directory where this script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.credentials_path = os.path.join(self.script_dir, "credentials.json")
        self.token_path = os.path.join(self.script_dir, "token.json")

    def get_drive_service(self):
        creds = None

        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(
                self.token_path,
                self.scopes,
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    self.scopes,
                )
                creds = flow.run_local_server(port=0)

        with open(self.token_path, "w") as token:
            token.write(creds.to_json())

        return build("drive", "v3", credentials=creds)

    def list_pdfs_in_folder(self, service, folder_id):
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

    def download_pdf(self, service, file_id):
        request = service.files().get_media(fileId=file_id)

        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False

        while not done:
            status, done = downloader.next_chunk()

        fh.seek(0)

        return fh


    def extract_pdf_text(self, pdf_file):
        reader = PdfReader(pdf_file)

        pages = []

        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)

        return "\n\n".join(pages)


    def read_pdfs_from_folder(self, folder_id):
        service = self.get_drive_service()
        pdfs = self.list_pdfs_in_folder(service, folder_id)
        documents = []
        for pdf in pdfs:
            print(f"Reading: {pdf['name']}")
            pdf_file = self.download_pdf(service, pdf["id"])
            text = self.extract_pdf_text(pdf_file)
            documents.append({
                "file_id": pdf["id"],
                "file_name": pdf["name"],
                "text": text,
            })

        return documents