from shutil import copyfile
import os

from ingest_tarball import IngestTarball

class IngestTarballTest:
    """
    TODOs
    - test multiple tarballs with multiple hostnames
    """

if __name__ == '__main__':
    """
    call like: python3 ingest_tarball_test.py
    """

    # get path to test tarball
    dir_path = os.path.dirname(os.path.realpath(__file__))
    tarballs_to_ingest_dir_path = f"{dir_path}/log-tarballs-to-ingest"
    tarball_dest_path = f"{tarballs_to_ingest_dir_path}/example-logs.tar.gz"

    # copy test file into our tarball "landing" dir
    copyfile(f"{dir_path}/test-tarballs/example-logs.tar.gz", tarball_dest_path)

    # run the ingester with example company_name and hostname
    ingestTarball = IngestTarball(tarball_filename="example-logs.tar.gz", client_name="test-client", hostname="123.456.789.101")

    ingestTarball.run()
    print("Success.")


