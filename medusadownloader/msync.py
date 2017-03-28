import getpass
import os
import sys
from pprint import pprint

import requests
import medusadownloader
import argparse


def get_args():
    parser = argparse.ArgumentParser(description="Medusa Downloader (msync)",)
    parser.add_argument("--destination", default=os.getcwd())
    parser.add_argument("--confirm", action="store_true")
    parser.add_argument("--key")
    parser.add_argument("bit_level_group")
    return parser.parse_args()


def verify(question):
    yes = ["yes", "y", ""]
    no = ["no", "n", "quit", "exit"]

    while True:
        answer = input("{} [yes]/no: ".format(question)).lower()
        if answer in yes:
            return True
        elif answer in no:
            return False
        print("Invalid answer")


def main():
    # Get the main command line arguments
    args = get_args()

    # Authenticate user and password. This is required to download with medusa
    if args.key:
        print("Using key")
        key = medusadownloader.read_key(args.key)
        user = key.username
        password = key.password
    else:
        # No key file is given
        user = input("Username: ")
        password = getpass.getpass()

    with medusadownloader.Medusa("https://medusa.library.illinois.edu", user, password) as m:
        try:

            if not args.confirm:
                bit_level_md = m.get_bit_level_file_group_json(args.bit_level_group)

                print("Collection:")
                pprint(m.get_collection_json(bit_level_md["collection_id"]))

                print("File Group:")
                pprint(bit_level_md)

                if not verify("Is this the correct file group?"):
                    print("Okay. Quitting.")
                    exit()

            files = list(m.get_file_binaries_url(args.bit_level_group))

            for i, f in enumerate(files):
                last_message_size = 0
                prefix = "{}/{}: ".format(str(i + 1).zfill(len(str(len(files)))), len(files))
                print("\r{}\r{}{}".format(" " * last_message_size, prefix, f.filename), flush=True)
                if os.path.exists(os.path.join(args.destination, f.filename)):
                    print("{}File already downloaded. Skipping.".format(prefix))
                    continue
                for it, progress in enumerate(m.download(f, args.destination)):
                    if it % 100 == 0:
                        msg = "\r{:0.2f}%".format(progress)
                        last_message_size = len(msg)
                        print("{}{}".format(" " * last_message_size, msg), end="", file=sys.stderr)
                else:
                    print("\r{}\r".format(" " * last_message_size), end="", flush=True)

        except ConnectionRefusedError as e:
            print("Medusa refused connection. Reason: {}".format(e), file=sys.stderr)
            exit(1)

        except requests.exceptions.ReadTimeout:
            print("Connection timed out.", file=sys.stderr)

        except ConnectionError as e:
            print("Connection Error. Reason: {}".format(e), file=sys.stderr)

            exit(1)


if __name__ == '__main__':
    main()
