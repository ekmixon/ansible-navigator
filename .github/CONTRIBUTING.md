# Contributing to Ansible Navigator

Some background:

The ansible-navigator code base is not just for it's users but current and
future developers. Over time we have adopted a few tools that help us
maintain it and you contribute.

1. mypy (Helps with type checking)

2. pylint (lints all the things)

3. code-spell (prevents typos in code)

```{note}
In early development cycles, a decision was made to use black as a formatter
which is why current pull-requests are required to pass a
`black --diff` check of the source tree. The decision to use `black` is
left to individual developers as the formatting changes it makes can be
achieved without it.
```

Details can be found below on how to run these manually, our CI will also
check them for you.

In order to contribute, you'll need to:

1. Fork the repository.

2. Create a branch, push your changes there. Don't forget to
   {ref}`include news files for the changelog <_ansible_navigator_adding_changelog_fragments>`.

3. Send it to us as a PR.

4. Iterate on your PR, incorporating the requested improvements
   and participating in the discussions.

Prerequisites:

1. Have {doc}`tox <tox:index>`.

2. Use {doc}`tox <tox:index>` to run the tests.

3. Before sending a PR, make sure that `lint` passes:

   ```shell-session
   $ tox -e lint
   lint create: .tox/lint
   lint installdeps: -rrequirements.txt, -rtest-requirements.txt
   lint installed: ...
   lint run-test-pre: PYTHONHASHSEED='4242713142'
   lint run-test: commands[0] | pylint ansible_navigator tests ...
   ...
   _________________________________ summary __________________________________
   lint: commands succeeded
   congratulations :)
   ```

4. We also suggest you to _optionally_ run the following check that is
   not yet enforced (meaning you can skip it, especially since it's
   annoyingly slow):

   ```shell-session
   $ tox -e lint-vetting
   lint-vetting create: .tox/lint-vetting
   lint-vetting installdeps: pre-commit, pylint ~= 2.8.0, pylint-pytest < 1.1.0
   lint-vetting installed: ...
   lint-vetting run-test-pre: PYTHONHASHSEED='2351399476'
   lint-vetting run-test: commands[0] | python -m pre_commit run ...--all-files
   ...
   [INFO] Initializing environment for https://github.com/asottile/add-trail...
   ...
   [INFO] Installing environment for https://github.com/asottile/add-trailin...
   [INFO] Once installed this environment will be reused.
   [INFO] This may take a few minutes...
   ...
   Add trailing commas...............................(no files to check)Skipped
   - hook id: add-trailing-comma
   ...
   _________________________________ summary __________________________________
   ERROR:   lint-vetting: commands failed
   ```
