"""Command line tool that extracts individual PEM files from a single JSON datafile.

This is a companion tool for this Synology SSL workflow:
https://reddec.net/articles/how-to-get-ssl-on-synology/ Using the syno-cli
container/tool will result in JSON data files for each LetsEncrypt certificate
you request. Within those JSON files are the Base64-encoded data for each of the
three key PEM files that you need to configure SSL: the certificate, private
key, and issuer's cert. This utility will read a given JSON datafile, extract
the three PEM files, and write them to disk at a given output directory.
"""
import sys
import typer
import debugpy
from pathlib import Path
from syno_cert_decoder import __version__
from syno_cert_decoder.syno_cert_decoder import SynoCertDecoder
import typing as t

app = typer.Typer()


@app.callback()
def main(
    debugger: bool = typer.Option(False, envvar="DEBUGGER"),
    debugger_port: int = typer.Option(5678, envvar="DEBUGGER_PORT"),
):
    """Console script for syno_cert_decoder."""
    if debugger:
        typer.echo(f"Waiting for debugger client to attach to port {debugger_port}")
        debugpy.listen(debugger_port)
        debugpy.wait_for_client()
    return 0


@app.command()
def version():
    """Print the version and exit"""
    typer.echo(__version__)
    return 0


@app.command()
def write_pem_files(
    json_file: str = typer.Option(
        ...,
        envvar="SYNO_JSON_FILE",
        help="The path to the JSON file that includes the encoded certificate, key, and issuer cert.",
    ),
    output_path: str = typer.Option(
        default="./", help="The path to where the PEM files will be written."
    ),
):
    """Extract PEM file data from a JSON data file.

    This command extracts PEM data from a given JSON data file, and writes the
    individual PEM files to disk at the given output path.  For example:

    \b
    syno_cert_decoder write-pem-files --json-file /volume1/docker/syno-cli/myservice.mydomain.com.json --output-path /volume1/docker/certificates/

    That command results in the following PEM files:

    \b
    glarizza@ds920:~/syno-cert-decoder$ ls -lah /volume1/docker/certificates/
    total 16K
    drwxrwxrwx+ 1 glarizza users  204 May 15 15:03  .
    drwxrwxrwx+ 1 root     root   360 May 15 14:59  ..
    -rwxrwxrwx+ 1 glarizza users 5.5K May 15 15:06 'myservice.mydomain.com-certificate.pem'
    -rwxrwxrwx+ 1 glarizza users 3.7K May 15 15:06 'myservice.mydomain.com-issuer_certificate.pem'
    -rwxrwxrwx+ 1 glarizza users 1.7K May 15 15:06 'myservice.mydomain.com-privateKey.pem'
    """
    typer.echo(f"Parsing file at {json_file}")
    SynoCertDecoder(
        datafile_path=Path(json_file), output_path=Path(output_path)
    ).write_pem_files()


@app.command()
def pkcs12(
    json_file: str = typer.Option(
        ...,
        envvar="SYNO_JSON_FILE",
        help="The path to the JSON file that includes the encoded certificate, key, and issuer cert.",
    ),
    passphrase: t.Optional[str] = typer.Option(
        default=None,
        help="The passphrase to use for the private key (leave empty if not needed).",
    ),
    output_file: Path = typer.Option(
        ...,
        help="The path to the file that will be created (e.x. myservice.mydomain.com.pfx).",
    ),
):
    """Create a PKCS12 PFX file from a JSON data file.

    This command allows you to generate a PKCS12 PFX file from JSON certificate
    data file that contains the certificate and private key in PEM format. For
    example:

    \b
    syno_cert_decoder pkcs12  --json-file /volume1/docker/syno-cli/myservice.mydomain.com.json --passphrase "" --output-file /volume1/docker/certificates/myservice.mydomain.com.pfx
    """
    typer.echo(f"Parsing file at {json_file}")
    SynoCertDecoder(
        datafile_path=Path(json_file), output_path=output_file.parent
    ).pkcs12(passphrase=passphrase, filename=output_file.name)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
