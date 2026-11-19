import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from download_claim_audit.audit import audit, claims, evidence, GENERIC
from download_claim_audit.phrases import DOWNLOAD, NODOWNLOAD
from download_claim_audit.__main__ import main

EXPECTED_YES = ('downloads files', 'download files', 'downloads a file', 'download a file', 'downloads file', 'download file', 'file download support', 'file downloads support', 'downloads files from the cloud', 'download files from the cloud', 'downloads files from s3', 'download files from s3', 'downloads files from storage', 'download files from storage', 'downloads files from the server', 'download files from the server', 'downloads files from a server', 'download files from a server', 'downloads files from a bucket', 'download files from a bucket', 'downloads files from cloud storage', 'download files from cloud storage', 'downloads files from remote storage', 'download files from remote storage', 'supports file download', 'supports file downloads', 'supports downloading files', 'supports downloading a file', 'file download feature', 'file downloads feature', 'file download functionality', 'file download capability', 'file download capabilities', 'file download', 'file downloads', 'downloads files from aws', 'download files from aws', 'downloads files from azure', 'download files from azure', 'downloads files from google cloud', 'download files from google cloud', 'downloads files from gcs', 'download files from gcs', 'downloads files from a url', 'download files from a url', 'downloads files from the internet', 'download files from the internet', 'downloads files to disk', 'download files to disk', 'fetch files from the server')
EXPECTED_NO = ('does not download files', 'never downloads files', 'does not download a file', 'never downloads a file', 'does not download file', 'never downloads file', 'no file download support', 'no file downloads support', 'does not support file download', 'never supports file download', 'does not support file downloads', 'never supports file downloads', 'no file download feature', 'no file download functionality', 'no file download capability', 'does not download files from the cloud', 'never downloads files from the cloud', 'does not download files from s3', 'never downloads files from s3', 'does not download files from the server', 'never downloads files from the server', 'no file download', 'no file downloads', 'does not fetch files from the server')

class AuditTests(unittest.TestCase):
    def test_phrase_oracle(self):
        self.assertEqual(DOWNLOAD, EXPECTED_YES)
        self.assertEqual(NODOWNLOAD, EXPECTED_NO)
        for p in EXPECTED_YES: self.assertEqual(claims(p), (True, False))
        for p in EXPECTED_NO: self.assertEqual(claims(p), (False, True))

    def test_routes(self):
        cases = ["import boto3; boto3.client('s3'); x.download_file()", "import boto3; boto3.client('s3'); x.download_fileobj()", "import boto3; boto3.resource('s3'); x.download_file()", "from boto3 import client as c; c(service_name='s3'); x.download_file()", 'import google.cloud.storage; google.cloud.storage.Blob(); x.download_to_filename()', 'x.blob(); x.download_to_file()', 'from google.cloud.storage import Blob as B; B(); x.download_to_filename()', 'import azure.storage.blob; azure.storage.blob.BlobClient(); x.download_blob()', 'from azure.storage.blob import ContainerClient; ContainerClient(); x.download_blob()', 'x.get_blob_client(); x.download_blob()', 'from azure.storage.blob import BlobClient; BlobClient(); x.download_blob()', 'import requests; requests.get(x); open(x, "wb")', 'import requests; requests.get(x); x.iter_content()', 'import requests, shutil; requests.get(x); shutil.copyfileobj(a,b)', 'import requests; requests.get(x); x.write_bytes(b)', 'import requests; requests.Session(); x.get(); open(x,"wb")', 'import requests; requests.request("GET", x); open(x,"wb")', 'import urllib.request; urllib.request.urlopen(x); open(x,"wb")', 'from requests import get as g; g(x); open(x,"wb")', 'import httpx; httpx.get(x); open(x,"wb")', 'import httpx; httpx.Client(); x.get(); open(x,"wb")', 'import httpx; httpx.AsyncClient(); x.get(); open(x,"wb")', 'from httpx import get as g; g(x); open(x,"wb")', 'import urllib.request; urllib.request.urlretrieve(x)', 'from urllib.request import urlretrieve as u; u(x)', 'import wget; wget.download(x)', 'from wget import download as d; d(x)', 'from x import download_from_url as d; d()']
        cases += ['x.' + name + '()' for name in GENERIC]
        for code in cases:
            with self.subTest(code=code): self.assertTrue(evidence(code))
        for mode in ('wb','ab','xb','w+b','wb+','a+b','x+b'):
            self.assertTrue(evidence('import requests; requests.get(x); open(x, %r)' % mode))

    def test_non_evidence(self):
        cases = ['import boto3', "import boto3; boto3.client('s3')", 'from azure.storage.blob import BlobClient; BlobClient()', 'from azure.storage.blob import ContainerClient; ContainerClient()', 'x.download_file()', 'x.download_fileobj()', 'x.download_to_filename()', 'x.download_to_file()', 'x.download_blob()', 'x.download_as_bytes()', 'x.download_as_text()', 'x.download_as_string()', 'x.upload_file()', 'x.upload_from_filename()', 'x.upload_blob()', 'import requests; requests.get(x)', 'import requests; requests.post(x); open(x,"wb")', 'import requests; requests.Session(); x.get()', 'import httpx; httpx.get(x)', 'open(x,"wb")', 'x.iter_content()', 'import shutil; shutil.copyfileobj(a,b)', 'x.write_bytes(b)', 'import requests; requests.get(x); open(x,"rb")', 'import requests; requests.get(x); open(x,"r+b")', 'import requests; requests.get(x); open(x,"w")', 'import shutil; shutil.copy(a,b)', 'import shutil; shutil.move(a,b)', 'import os; os.rename(a,b)', 'x.generate_presigned_url()', 'x.generate_presigned_post()', 'def download_file(): pass\ndownload_file()', 'import subprocess; subprocess.run(["curl"])', 'import subprocess; subprocess.run(["wget"])', 'import subprocess; subprocess.run(["aws","s3","cp"])', '"download"', 'mindee.parse(InvoiceV4)', 'x.begin_analyze_document("prebuilt-layout")', 'veryfi.Client()', 'documentai.process_document()', 'textract.analyze_document()', 'eden.universal_ai()', 'llamaparse.parse()', 'nanonets.ocr(model_id="opaque")', 'docsumo.upload()', 'import requests; requests = x; requests.get(x); open(x,"wb")', 'from wget import download; download = x; download(x)', 'from wget import download; with x as download: pass\ndownload(x)', 'import botocore; botocore.client("s3"); x.download_file()', 'import urllib.request; urllib.request.urlopen(x)', 'invalid syntax !']
        for code in cases:
            with self.subTest(code=code): self.assertFalse(evidence(code))

    def test_findings_and_scope(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); readme=root/'README.md'; readme.write_text('downloads files')
            f=audit(root)['findings'][0]; self.assertEqual((f['id'],f['severity']), ('documented-file-download-claim-false','HIGH')); self.assertEqual(main(['audit',d]),2)
            (root/'tests').mkdir(); (root/'tests/test_x.py').write_text('x.fetch_file()')
            self.assertEqual(audit(root)['findings'][0]['severity'],'MEDIUM'); self.assertEqual(main(['audit',d]),0); self.assertEqual(main(['audit',d,'--fail-on','medium']),2)
            (root/'app.py').write_text('x.fetch_file()'); self.assertEqual(audit(root)['verdict'],'PASS')
            readme.write_text('does not download files'); self.assertEqual(audit(root)['findings'][0]['id'],'documented-no-file-download-claim-false'); self.assertEqual(main(['audit',d]),2)
            (root/'app.py').unlink(); self.assertEqual(audit(root)['verdict'],'PASS')
            readme.write_text('```\ndownloads files\n```'); self.assertEqual(audit(root)['verdict'],'PASS')
            readme.write_text('`downloads files`'); self.assertEqual(audit(root)['findings'][0]['severity'],'MEDIUM')
            (root/'a.py').write_text('import requests; requests.get(x)'); (root/'b.py').write_text('open(x,"wb")'); self.assertEqual(audit(root)['findings'][0]['severity'],'MEDIUM')
            (root/'b.py').write_text('x.fetch_file()'); self.assertEqual(audit(root)['verdict'],'PASS'); self.assertEqual(audit(root,['b.py'])['verdict'],'FAIL')
            readme.write_text('unrelated'); self.assertEqual(audit(root)['verdict'],'PASS')

    def test_symlinks_json_and_version(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as outside:
            root=Path(d); (root/'README.md').write_text('downloads files'); target=Path(outside)/'x.py'; target.write_text('x.fetch_file()'); (root/'link.py').symlink_to(target)
            env=dict(os.environ); env['PYTHONPATH']=str(Path(__file__).resolve().parents[1]/'src')
            r=subprocess.run([sys.executable,'-m','download_claim_audit','audit',d,'--json'],capture_output=True,text=True,env=env)
            self.assertEqual(r.returncode,2); result=json.loads(r.stdout); self.assertEqual(result['verdict'],'FAIL'); self.assertTrue(result['findings'][0]['message'])
            r=subprocess.run([sys.executable,'-m','download_claim_audit','--version'],capture_output=True,text=True,env=env); self.assertEqual(r.stdout.strip(),'0.1.0')

if __name__ == '__main__': unittest.main()
