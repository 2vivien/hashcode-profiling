from argparse import ArgumentParser
from pathlib import Path
from urllib.request import urlopen

def download(url: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(url, timeout=60) as response:
        output.write_bytes(response.read())

def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--esco-url")
    parser.add_argument("--esco-output", type=Path)
    parser.add_argument("--onet-url")
    parser.add_argument("--onet-output", type=Path)
    args = parser.parse_args()
    if bool(args.esco_url) != bool(args.esco_output):
        raise ValueError("ESCO URL and output must be supplied together")
    if bool(args.onet_url) != bool(args.onet_output):
        raise ValueError("O*NET URL and output must be supplied together")
    if args.esco_url:
        download(args.esco_url, args.esco_output)
    if args.onet_url:
        download(args.onet_url, args.onet_output)

if __name__ == "__main__":
    main()
