from shutil import copyfile
import os

from ingest_tarball import IngestTarball

class IngestTarballTest:
    """
    tests the python class itself. 
    Note that we might not really use this from the cmd line, so it's helpful to test when initiating just the python code, whether or not the arg parsing works well

    TODOs
    - test with system log tarball also
    - write a shell script to test arg parsing (if we decide we want to be able to run ingest_tarball from the cli)
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
    # TODO reformat the example tarball to match our new format (ie has multiple nodes per tarball, so has a parent directory that has ip addrs of nodes, and then logs can be buried in there)
    # currently does not work until this gets fixed
    ingestTarball = IngestTarball(tarball_filename="example-logs.tar.gz", client_name="test-client", debug_mode=True)

    ingestTarball.run()
    print("Success.")


