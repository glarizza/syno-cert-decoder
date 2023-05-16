import base64
import json
from dataclasses import dataclass
from pathlib import Path
import typer
import typing as t
import OpenSSL


@dataclass
class SynoCertDecoder:
    datafile_path: Path
    output_path: Path

    def read_data_file(self) -> t.ByteString:
        """Convenience method for reading a file.

        Returns:
            t.ByteString: The file's contents in bytes.
        """
        with open(self.datafile_path, "rb") as f:
            return f.read()

    def prepare_pem_data(self) -> t.Dict:
        """Assemble a dictionary of PEM file data.

        This method extracts PEM data from the three files that have been
        serialized within a JSON data file: the certificate, the private key,
        and the issuer's certificate. Each file is represented by a key within
        the dictionary whose corresponding value is the string data of the PEM
        file.

        Returns:
            t.Dict: A dictionary containing the string data of three PEM files:
                    the certificate, private key, and issuer's certificate.
        """
        pemdata = {}
        jsondata = json.loads(self.read_data_file())
        for item in ["privateKey", "certificate", "issuer_certificate"]:
            pemdata[item] = base64.b64decode(jsondata[item])
        return pemdata

    def write_file(self, file_path: Path, data: t.ByteString):
        """Convenience method for writing a file.

        Args:
            file_path (Path): The path to where the file will be written.
            data (str): The contents of the file to be written.
        """
        with open(file_path, "wb") as outfile:
            outfile.write(data)

    def write_pem_files(self):
        """Extract and write PEM files from encoded JSON data files.

        This method reads a JSON file containing three Base64-encoded PEM files
        - a certificate, a private key, and an issuer's certificate - and writes
        those three separate PEM files to disk at a given output path.
        """
        for certitem, certdata in self.prepare_pem_data().items():
            output_file = self.output_path / f"{self.datafile_path.stem}-{certitem}.pem"
            typer.echo(f"Writing {output_file} data now...")
            self.write_file(file_path=output_file, data=certdata)

    def pkcs12(self, passphrase: t.Optional[str], filename: str):
        """Create a PKCS12 PFX file from a JSON data file.

        This method reads a JSON file containing Base64-encoded PEM files and
        creates a new PKCS12 PFX file from the encoded data. A passphrase
        can be provided if the private key requires one.
        """
        certdata = self.prepare_pem_data()
        pkcs = OpenSSL.crypto.PKCS12()
        pkcs.set_privatekey(
            OpenSSL.crypto.load_privatekey(
                OpenSSL.crypto.FILETYPE_PEM, certdata["privateKey"], passphrase
            )
        )
        pkcs.set_certificate(
            OpenSSL.crypto.load_certificate(
                OpenSSL.crypto.FILETYPE_PEM, certdata["certificate"]
            )
        )
        output_file = self.output_path / filename
        typer.echo(f"Writing {output_file} now...")
        self.write_file(file_path=output_file, data=pkcs.export(passphrase=passphrase))
