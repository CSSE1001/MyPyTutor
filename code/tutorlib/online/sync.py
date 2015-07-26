from concurrent.futures import ThreadPoolExecutor, as_completed
import os


class SyncClient():
    def __init__(self, web_api):
        self.web_api = web_api

    def download_answer(self, tutorial, tutorial_package):
        """
        Download the answer for the given tutorial from the server.

        The tutorial must be part of the current tutorial package.

        Args:
          tutorial (Tutorial): The tutorial to download the answer for.
          tutorial_package (TutorialPackage): The tutorial package that the
            tutorial belongs to.

        Returns:
          Whether the download was successful.

        """
        problem_set = tutorial_package.problem_set_containing(tutorial)
        assert problem_set is not None, \
            'Tutorial {} not found in current package'.format(tutorial)

        response = self.web_api.download_answer(
            tutorial, problem_set, tutorial_package
        )
        if response is None:
            return False  # no tutorial to download, or download error

        # write it to disk
        with open(tutorial.answer_path, 'w') as f:
            f.write(response)

        return True

    def upload_answer(self, tutorial, tutorial_package):
        """
        Upload the answer for the given tutorial to the server.

        The tutorial must be part of the current tutorial package.

        Args:
          tutorial (Tutorial): The tutorial to upload the answer for.
          tutorial_package (TutorialPackage): The tutorial package that the
            tutorial belongs to.

        Returns:
          Whether the upload was successful.

        """
        if not os.path.exists(tutorial.answer_path):
            return False

        with open(tutorial.answer_path) as f:
            code = f.read()

        problem_set = tutorial_package.problem_set_containing(tutorial)
        assert problem_set is not None, \
            'Tutorial {} not found in current package'.format(tutorial)

        return self.web_api.upload_answer(
            tutorial, problem_set, tutorial_package, code
        )

    def get_answer_info(self, tutorial, tutorial_package):
        """
        Get the hash and modification time of the student's answer to the
        given tutorial on the server.

        This information can be compared to local data in order to determine
        whether the latest version of the tutorial is on the server or is
        available locally.

        The tutorial must be part of the current tutorial package.

        Args:
          tutorial (Tutorial): The tutorial to query the server about.
          tutorial_package (TutorialPackage): The tutorial package that the
            tutorial belongs to.

        Returns:
          A tuple of the answer information.
          The first element of the tuple is the hash of the answer file.
          The second element of the tuple is the file's modification time.

        """
        problem_set = tutorial_package.problem_set_containing(tutorial)
        assert problem_set is not None, \
            'Tutorial {} not found in current package'.format(tutorial)

        return self.web_api.answer_info(
            tutorial, problem_set, tutorial_package
        )

    def _do_sync(self, tutorial, tutorial_package):
        def f():
            remote_hash, remote_mtime = self.get_answer_info(
                tutorial, tutorial_package
            )

            if not tutorial.has_answer:
                if remote_hash is not None:  # there exists a remote copy
                    self.download_answer(tutorial, tutorial_package)
                return True

            local_hash, local_mtime = tutorial.answer_info

            if local_hash == remote_hash:  # no changes
                return True

            if remote_hash is None or local_mtime >= remote_mtime:
                success = self.upload_answer(tutorial, tutorial_package)
            else:
                success = self.download_answer(tutorial, tutorial_package)

            if not success:
                return False

        def try_repeatedly(f, n=3):
            def fn():
                for _ in range(n):
                    result = f()
                    if result:
                        return result
                return result
            return fn

        return try_repeatedly(f)

    def synchronise(self, tutorial_package):
        """
        Synchronise the tutorial answers.

        A tutorial will be downloaded from the server iff:
          * there is no local answer, but there is one on the server; or
          * the local and remote answers differ, but the remote one was
            modified after the local one.

        A tutorial will be uploaded to the server iff:
          * there is no answer on the server, but there is a local one; or
          * the local and remote answers differ, but the local one was modified
            at the same time as or before the one on the server.

        This method performs the actual synchronisation.  It does not handle
        any exceptions which may be thrown by the underlying code (ie, it may
        raise WebAPIError).

        Args:
          tutorial_package (TutorialPackage): The tutorial package to sync.

        """
        max_workers = len(tutorial_package.problem_sets)
        with ThreadPoolExecutor(max_workers) as executor:
            futures = []

            for problem_set in tutorial_package.problem_sets:
                for tutorial in problem_set:
                    executor.submit(self._do_sync(tutorial, tutorial_package))

            success = True
            for future in as_completed(futures):
                if not future.result():
                    success = False
                    # atm, not breaking out early

        return success
