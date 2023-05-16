# Synology Cert Decoder

This is a quick and dirty Python tool that I use to extract SSL certificate PEM
files from Base64-encoded values within a JSON data file.

NOTE: See this article on automatically generating and installing SSL certs from
LetsEncrypt using the DNS validation method that requires no open ports and a
Synology NAS: https://reddec.net/articles/how-to-get-ssl-on-synology/  This tool
is meant to read from the JSON data files that are created by the workflow in
that article.

## How does this all fit together?

There are three main needs that are satisfied by the workflow above and this
companion tooling:

1. I needed to automatically generate LetsEncrypt SSL certs without exposing any open ports to my NAS.
2. I wanted those SSL certs to be installed directly into the Synology NAS so I could use them with the built-in reverse proxy.
3. I also wanted individual PEM files for each LetsEncrypt cert generated so I could attach them to running Docker containers and configure SSL down to the service level (if I wanted to go beyond the reverse proxy....which I do).

The article linked above walks you through setting up a Docker container and
your DNS provider of choice (Cloudflare) to automatically request SSL
certificates from LetsEncrypt for the purpose of securing your Synology NAS
and any services that it provides. It's a cool automated workflow that goes
the full mile and installs the SSL certs onto your NAS by way of its API. I
wanted to re-use these certificates for other Dockerized services on my NAS,
but I needed the individual cert/key/CA-cert files to be able to do that. Those
files can be extracted from the individual JSON file that's written to disk
for each LetsEncrypt cert, but I needed an automated workflow to do that (because the certs expire every `<TIMEPERIOD>`).

The linked article covers the first 2 needs, and this little Python tool satisfies
the last need.

## Installing this Python tool on a Synology NAS

You're going to need to get Python installed and install a couple of libraries
to allow us to create a virtual environment directly on the NAS. This article
does a good job of walking you through that:
https://synoguide.com/2023/01/21/install-and-use-python-3-9-in-your-synology/
Follow that article all the way through to creating a virtual environment within
a directory in your home directory. I created `$HOME/syno-cert-decoder` on my NAS.

NOTE: Python 3.9 is the most recent Python package available to my NAS as of the time
of this writing, so that's the version I'll be using.

Once you've got a virtual environment setup on your NAS, the next thing you need
to do is ensure that the required Python packages are installed in your virtual
environment. Normally we could do this via `make` targets I've exposed via the
`Makefile` in the repo, but `make` is not available on the NAS (and I really
don't wanna go down that route). The easiest way for me to do this has been to
copy the `requirements.txt` file over to the virtual environment, and use the `pip`
binary in the virtual environment to install the package dependencies. Execute
the following from within your virtual environment folder:

```bash
./.venv/bin/pip install -r /path/to/requirements.txt
```

Now we need to generate a wheel file for this tool - the cert decoder. I have a
make task dedicated for this action that can be run from your laptop:

```bash
make dist
```

Running that command from the root of the repository will create two files
within the `dist/` directory: a tarball, and a wheel file. First copy the wheel
file over to the Synology NAS is whatever way is easiest from you. Next, you'll
need to change to the directory containing your virtual environment (mine is
`$HOME/syno-cert-decoder`) and then use the `pip` binary in the virtual
environment to install the wheel file:

```bash
glarizza@ds920:~/syno-cert-decoder$ ./.venv/bin/pip install /volume1/data/syno_cert_decoder-0.1.3-py3-none-any.whl

Processing /volume1/data/syno_cert_decoder-0.1.3-py3-none-any.whl
Requirement already satisfied: typer>=0.4.0 in ./.venv/lib/python3.9/site-packages (from syno-cert-decoder==0.1.3) (0.9.0)
Requirement already satisfied: pendulum in ./.venv/lib/python3.9/site-packages (from syno-cert-decoder==0.1.3) (2.1.2)
Requirement already satisfied: debugpy>=1.5.1 in ./.venv/lib/python3.9/site-packages (from syno-cert-decoder==0.1.3) (1.6.7)
Requirement already satisfied: typing-extensions>=3.7.4.3 in ./.venv/lib/python3.9/site-packages (from typer>=0.4.0->syno-cert-decoder==0.1.3) (4.5.0)
Requirement already satisfied: click<9.0.0,>=7.1.1 in ./.venv/lib/python3.9/site-packages (from typer>=0.4.0->syno-cert-decoder==0.1.3) (8.1.3)
Requirement already satisfied: python-dateutil<3.0,>=2.6 in ./.venv/lib/python3.9/site-packages (from pendulum->syno-cert-decoder==0.1.3) (2.8.2)
Requirement already satisfied: pytzdata>=2020.1 in ./.venv/lib/python3.9/site-packages (from pendulum->syno-cert-decoder==0.1.3) (2020.1)
Requirement already satisfied: six>=1.5 in ./.venv/lib/python3.9/site-packages (from python-dateutil<3.0,>=2.6->pendulum->syno-cert-decoder==0.1.3) (1.16.0)
Installing collected packages: syno-cert-decoder
  Attempting uninstall: syno-cert-decoder
    Found existing installation: syno-cert-decoder 0.1.2
    Uninstalling syno-cert-decoder-0.1.2:
      Successfully uninstalled syno-cert-decoder-0.1.2
Successfully installed syno-cert-decoder-0.1.3
```

Once the wheel file is successfully installed, you'll be able to run the tool
from the virtual environment's `bin` directory:

```bash
glarizza@ds920:~/syno-cert-decoder$ ./.venv/bin/syno_cert_decoder --help
Usage: syno_cert_decoder [OPTIONS] COMMAND [ARGS]...

  Console script for syno_cert_decoder.

Options:
  --debugger / --no-debugger      [env var: DEBUGGER; default: no-debugger]
  --debugger-port INTEGER         [env var: DEBUGGER_PORT; default: 5678]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  version          Print the version and exit
  write-pem-files  Extract PEM file data from a JSON data file.
```

From here you can setup a scheduled task to run the tool on a given interval,
extract the cert data, and drop the PEM files into wherever you store your
certificates (I drop them into a directory that I bind-mount as read-only to the
containers that require them).
