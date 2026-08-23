# LOCAL_SMOKE_WRAPPER_REPORT.md

- Generated: `2026-06-06T20:03:12.862379Z`
- Project root: `D:\GPTMEAi-SEMASCRIPT`
- Status: `FAIL`
- Report path: `D:\GPTMEAi-SEMASCRIPT\reports\codex\LOCAL_SMOKE_WRAPPER_REPORT.md`

## Commands

### 1. `python -B tools\check_root_cleanliness.py`

- Exit code: `0`
- Duration seconds: `0.075`

#### stdout

```text
ROOT_CLEANLINESS=OK
ROOT=D:\GPTMEAi-SEMASCRIPT
```

#### stderr

```text

```

### 2. `python -B tools\check_schema_consistency.py`

- Exit code: `0`
- Duration seconds: `0.083`

#### stdout

```text
SCHEMA_CONSISTENCY=OK
ROOT=D:\GPTMEAi-SEMASCRIPT
```

#### stderr

```text

```

### 3. `python -B -m unittest discover -s tests`

- Exit code: `1`
- Duration seconds: `0.878`

#### stdout

```text

```

#### stderr

```text
...................................................................................EEE...EException ignored while calling weakref callback <finalize object at 0x19e0df4fc60; dead>:
Traceback (most recent call last):
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\weakref.py", line 490, in __call__
    return info.func(*info.args, **(info.kwargs or {}))
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 960, in _cleanup
    cls._rmtree(name, ignore_errors=ignore_errors)
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 955, in _rmtree
    _shutil.rmtree(name, onexc=onexc)
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 852, in rmtree
    _rmtree_impl(path, dir_fd, onexc)
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 689, in _rmtree_unsafe
    for dirpath, dirnames, filenames in results:
  File "<frozen os>", line 413, in walk
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 687, in onerror
    onexc(os.scandir, err.filename, err)
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 927, in onexc
    _resetperms(path)
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 287, in _resetperms
    _dont_follow_symlinks(_os.chmod, path, 0o700)
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 276, in _dont_follow_symlinks
    func(path, *args, follow_symlinks=False)
PermissionError: [WinError 5] Отказано в доступе: 'D:\\GPTMEAi-SEMASCRIPT\\tests\\tmpnrb_cprb'
EException ignored while calling weakref callback <finalize object at 0x19e0df4fd40; dead>:
Traceback (most recent call last):
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\weakref.py", line 490, in __call__
    return info.func(*info.args, **(info.kwargs or {}))
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 960, in _cleanup
    cls._rmtree(name, ignore_errors=ignore_errors)
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 955, in _rmtree
    _shutil.rmtree(name, onexc=onexc)
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 852, in rmtree
    _rmtree_impl(path, dir_fd, onexc)
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 689, in _rmtree_unsafe
    for dirpath, dirnames, filenames in results:
  File "<frozen os>", line 413, in walk
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 687, in onerror
    onexc(os.scandir, err.filename, err)
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 927, in onexc
    _resetperms(path)
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 287, in _resetperms
    _dont_follow_symlinks(_os.chmod, path, 0o700)
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 276, in _dont_follow_symlinks
    func(path, *args, follow_symlinks=False)
PermissionError: [WinError 5] Отказано в доступе: 'D:\\GPTMEAi-SEMASCRIPT\\tests\\tmpfbimb9xe'
...............................................E...................E.E
======================================================================
ERROR: test_forbidden_root_folder_fails (test_root_cleanliness.RootCleanlinessTests.test_forbidden_root_folder_fails)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\GPTMEAi-SEMASCRIPT\tests\test_root_cleanliness.py", line 44, in test_forbidden_root_folder_fails
    (root / "node_modules").mkdir()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\pathlib\__init__.py", line 1011, in mkdir
    os.mkdir(self, mode)
    ~~~~~~~~^^^^^^^^^^^^
PermissionError: [WinError 5] Отказано в доступе: 'D:\\GPTMEAi-SEMASCRIPT\\tests\\tmp65np5heu\\node_modules'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<frozen os>", line 377, in walk
PermissionError: [WinError 5] Отказано в доступе: 'D:\\GPTMEAi-SEMASCRIPT\\tests\\tmp65np5heu'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "D:\GPTMEAi-SEMASCRIPT\tests\test_root_cleanliness.py", line 42, in test_forbidden_root_folder_fails
    with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temp_dir:
         ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 971, in __exit__
    self.cleanup()
    ~~~~~~~~~~~~^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 975, in cleanup
    self._rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 955, in _rmtree
    _shutil.rmtree(name, onexc=onexc)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 852, in rmtree
    _rmtree_impl(path, dir_fd, onexc)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 689, in _rmtree_unsafe
    for dirpath, dirnames, filenames in results:
                                        ^^^^^^^
  File "<frozen os>", line 413, in walk
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 687, in onerror
    onexc(os.scandir, err.filename, err)
    ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 927, in onexc
    _resetperms(path)
    ~~~~~~~~~~~^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 287, in _resetperms
    _dont_follow_symlinks(_os.chmod, path, 0o700)
    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 276, in _dont_follow_symlinks
    func(path, *args, follow_symlinks=False)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PermissionError: [WinError 5] Отказано в доступе: 'D:\\GPTMEAi-SEMASCRIPT\\tests\\tmp65np5heu'

======================================================================
ERROR: test_report_under_reports_codex_passes (test_root_cleanliness.RootCleanlinessTests.test_report_under_reports_codex_passes)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\pathlib\__init__.py", line 1011, in mkdir
    os.mkdir(self, mode)
    ~~~~~~~~^^^^^^^^^^^^
FileNotFoundError: [WinError 3] Системе не удается найти указанный путь: 'D:\\GPTMEAi-SEMASCRIPT\\tests\\tmp8w35hz2e\\reports\\codex'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "D:\GPTMEAi-SEMASCRIPT\tests\test_root_cleanliness.py", line 33, in test_report_under_reports_codex_passes
    report_dir.mkdir(parents=True)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\pathlib\__init__.py", line 1015, in mkdir
    self.parent.mkdir(parents=True, exist_ok=True)
    ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\pathlib\__init__.py", line 1011, in mkdir
    os.mkdir(self, mode)
    ~~~~~~~~^^^^^^^^^^^^
PermissionError: [WinError 5] Отказано в доступе: 'D:\\GPTMEAi-SEMASCRIPT\\tests\\tmp8w35hz2e\\reports'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<frozen os>", line 377, in walk
PermissionError: [WinError 5] Отказано в доступе: 'D:\\GPTMEAi-SEMASCRIPT\\tests\\tmp8w35hz2e'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "D:\GPTMEAi-SEMASCRIPT\tests\test_root_cleanliness.py", line 30, in test_report_under_reports_codex_passes
    with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temp_dir:
         ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 971, in __exit__
    self.cleanup()
    ~~~~~~~~~~~~^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 975, in cleanup
    self._rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 955, in _rmtree
    _shutil.rmtree(name, onexc=onexc)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 852, in rmtree
    _rmtree_impl(path, dir_fd, onexc)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 689, in _rmtree_unsafe
    for dirpath, dirnames, filenames in results:
                                        ^^^^^^^
  File "<frozen os>", line 413, in walk
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 687, in onerror
    onexc(os.scandir, err.filename, err)
    ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 927, in onexc
    _resetperms(path)
    ~~~~~~~~~~~^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 287, in _resetperms
    _dont_follow_symlinks(_os.chmod, path, 0o700)
    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 276, in _dont_follow_symlinks
    func(path, *args, follow_symlinks=False)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PermissionError: [WinError 5] Отказано в доступе: 'D:\\GPTMEAi-SEMASCRIPT\\tests\\tmp8w35hz2e'

======================================================================
ERROR: test_root_report_file_fails (test_root_cleanliness.RootCleanlinessTests.test_root_report_file_fails)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\GPTMEAi-SEMASCRIPT\tests\test_root_cleanliness.py", line 22, in test_root_report_file_fails
    (root / "SOME_REPORT.md").write_text("# report\n", encoding="utf-8")
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\pathlib\__init__.py", line 809, in write_text
    with self.open(mode='w', encoding=encoding, errors=errors, newline=newline) as f:
         ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\pathlib\__init__.py", line 771, in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PermissionError: [Errno 13] Permission denied: 'D:\\GPTMEAi-SEMASCRIPT\\tests\\tmp0wwmbbyh\\SOME_REPORT.md'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<frozen os>", line 377, in walk
PermissionError: [WinError 5] Отказано в доступе: 'D:\\GPTMEAi-SEMASCRIPT\\tests\\tmp0wwmbbyh'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "D:\GPTMEAi-SEMASCRIPT\tests\test_root_cleanliness.py", line 20, in test_root_report_file_fails
    with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temp_dir:
         ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 971, in __exit__
    self.cleanup()
    ~~~~~~~~~~~~^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 975, in cleanup
    self._rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 955, in _rmtree
    _shutil.rmtree(name, onexc=onexc)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 852, in rmtree
    _rmtree_impl(path, dir_fd, onexc)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 689, in _rmtree_unsafe
    for dirpath, dirnames, filenames in results:
                                        ^^^^^^^
  File "<frozen os>", line 413, in walk
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 687, in onerror
    onexc(os.scandir, err.filename, err)
    ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 927, in onexc
    _resetperms(path)
    ~~~~~~~~~~~^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 287, in _resetperms
    _dont_follow_symlinks(_os.chmod, path, 0o700)
    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 276, in _dont_follow_symlinks
    func(path, *args, follow_symlinks=False)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PermissionError: [WinError 5] Отказано в доступе: 'D:\\GPTMEAi-SEMASCRIPT\\tests\\tmp0wwmbbyh'

======================================================================
ERROR: test_fake_matrix_marking_execution_supported_fails (test_schema_consistency_guard.SchemaConsistencyGuardTests.test_fake_matrix_marking_execution_supported_fails)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\GPTMEAi-SEMASCRIPT\tests\test_schema_consistency_guard.py", line 142, in test_fake_matrix_marking_execution_supported_fails
    temp_dir, fake_root = make_fake_project_root(matrix)
                          ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^
  File "D:\GPTMEAi-SEMASCRIPT\tests\test_schema_consistency_guard.py", line 42, in make_fake_project_root
    contracts.mkdir()
    ~~~~~~~~~~~~~~~^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\pathlib\__init__.py", line 1011, in mkdir
    os.mkdir(self, mode)
    ~~~~~~~~^^^^^^^^^^^^
PermissionError: [WinError 5] Отказано в доступе: 'D:\\GPTMEAi-SEMASCRIPT\\tests\\tmpnrb_cprb\\contracts'

======================================================================
ERROR: test_fake_matrix_missing_required_action_field_fails (test_schema_consistency_guard.SchemaConsistencyGuardTests.test_fake_matrix_missing_required_action_field_fails)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\GPTMEAi-SEMASCRIPT\tests\test_schema_consistency_guard.py", line 127, in test_fake_matrix_missing_required_action_field_fails
    temp_dir, fake_root = make_fake_project_root(matrix)
                          ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^
  File "D:\GPTMEAi-SEMASCRIPT\tests\test_schema_consistency_guard.py", line 42, in make_fake_project_root
    contracts.mkdir()
    ~~~~~~~~~~~~~~~^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\pathlib\__init__.py", line 1011, in mkdir
    os.mkdir(self, mode)
    ~~~~~~~~^^^^^^^^^^^^
PermissionError: [WinError 5] Отказано в доступе: 'D:\\GPTMEAi-SEMASCRIPT\\tests\\tmpfbimb9xe\\contracts'

======================================================================
ERROR: test_explicit_path_loads_temp_contract_without_writing (test_stage4_preview_handoff_contract_loader.Stage4PreviewHandoffContractLoaderTests.test_explicit_path_loads_temp_contract_without_writing)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\GPTMEAi-SEMASCRIPT\tests\test_stage4_preview_handoff_contract_loader.py", line 108, in test_explicit_path_loads_temp_contract_without_writing
    temp_contract.write_text(original, encoding="utf-8")
    ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\pathlib\__init__.py", line 809, in write_text
    with self.open(mode='w', encoding=encoding, errors=errors, newline=newline) as f:
         ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\pathlib\__init__.py", line 771, in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PermissionError: [Errno 13] Permission denied: 'D:\\GPTMEAi-SEMASCRIPT\\tests\\tmp321hoajp\\contract.json'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<frozen os>", line 377, in walk
PermissionError: [WinError 5] Отказано в доступе: 'D:\\GPTMEAi-SEMASCRIPT\\tests\\tmp321hoajp'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "D:\GPTMEAi-SEMASCRIPT\tests\test_stage4_preview_handoff_contract_loader.py", line 105, in test_explicit_path_loads_temp_contract_without_writing
    with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temp_dir:
         ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 971, in __exit__
    self.cleanup()
    ~~~~~~~~~~~~^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 975, in cleanup
    self._rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 955, in _rmtree
    _shutil.rmtree(name, onexc=onexc)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 852, in rmtree
    _rmtree_impl(path, dir_fd, onexc)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 689, in _rmtree_unsafe
    for dirpath, dirnames, filenames in results:
                                        ^^^^^^^
  File "<frozen os>", line 413, in walk
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 687, in onerror
    onexc(os.scandir, err.filename, err)
    ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 927, in onexc
    _resetperms(path)
    ~~~~~~~~~~~^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 287, in _resetperms
    _dont_follow_symlinks(_os.chmod, path, 0o700)
    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 276, in _dont_follow_symlinks
    func(path, *args, follow_symlinks=False)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PermissionError: [WinError 5] Отказано в доступе: 'D:\\GPTMEAi-SEMASCRIPT\\tests\\tmp321hoajp'

======================================================================
ERROR: test_main_writes_snapshot_and_returns_success (test_write_gptmeai_readonly_snapshot_from_report.WriteGPTMEAiReadonlySnapshotFromReportTests.test_main_writes_snapshot_and_returns_success)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\GPTMEAi-SEMASCRIPT\tests\test_write_gptmeai_readonly_snapshot_from_report.py", line 65, in test_main_writes_snapshot_and_returns_success
    exit_code = main(
        [
    ...<6 lines>...
        ]
    )
  File "D:\GPTMEAi-SEMASCRIPT\tools\write_gptmeai_readonly_snapshot_from_report.py", line 72, in main
    output = write_snapshot_from_report(
        report_path=args.report,
        output_path=args.output,
        captured_at=args.captured_at,
    )
  File "D:\GPTMEAi-SEMASCRIPT\tools\write_gptmeai_readonly_snapshot_from_report.py", line 43, in write_snapshot_from_report
    destination.write_text(
    ~~~~~~~~~~~~~~~~~~~~~~^
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n",
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        encoding="utf-8",
        ^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\pathlib\__init__.py", line 809, in write_text
    with self.open(mode='w', encoding=encoding, errors=errors, newline=newline) as f:
         ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\pathlib\__init__.py", line 771, in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PermissionError: [Errno 13] Permission denied: 'C:\\Users\\CROWN-~1\\AppData\\Local\\Temp\\tmpglbpcrfg\\snapshot.json'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<frozen os>", line 377, in walk
PermissionError: [WinError 5] Отказано в доступе: 'C:\\Users\\CROWN-~1\\AppData\\Local\\Temp\\tmpglbpcrfg'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "D:\GPTMEAi-SEMASCRIPT\tests\test_write_gptmeai_readonly_snapshot_from_report.py", line 63, in test_main_writes_snapshot_and_returns_success
    with tempfile.TemporaryDirectory() as temp_dir:
         ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 971, in __exit__
    self.cleanup()
    ~~~~~~~~~~~~^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 975, in cleanup
    self._rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 955, in _rmtree
    _shutil.rmtree(name, onexc=onexc)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 852, in rmtree
    _rmtree_impl(path, dir_fd, onexc)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 689, in _rmtree_unsafe
    for dirpath, dirnames, filenames in results:
                                        ^^^^^^^
  File "<frozen os>", line 413, in walk
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 687, in onerror
    onexc(os.scandir, err.filename, err)
    ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 927, in onexc
    _resetperms(path)
    ~~~~~~~~~~~^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 287, in _resetperms
    _dont_follow_symlinks(_os.chmod, path, 0o700)
    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 276, in _dont_follow_symlinks
    func(path, *args, follow_symlinks=False)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PermissionError: [WinError 5] Отказано в доступе: 'C:\\Users\\CROWN-~1\\AppData\\Local\\Temp\\tmpglbpcrfg'

======================================================================
ERROR: test_write_snapshot_from_report_creates_expected_json (test_write_gptmeai_readonly_snapshot_from_report.WriteGPTMEAiReadonlySnapshotFromReportTests.test_write_snapshot_from_report_creates_expected_json)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\GPTMEAi-SEMASCRIPT\tests\test_write_gptmeai_readonly_snapshot_from_report.py", line 50, in test_write_snapshot_from_report_creates_expected_json
    written_path = write_snapshot_from_report(
        report_path=REPORT_FIXTURE,
        output_path=output_path,
        captured_at="2026-05-03T00:00:00Z",
    )
  File "D:\GPTMEAi-SEMASCRIPT\tools\write_gptmeai_readonly_snapshot_from_report.py", line 43, in write_snapshot_from_report
    destination.write_text(
    ~~~~~~~~~~~~~~~~~~~~~~^
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n",
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        encoding="utf-8",
        ^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\pathlib\__init__.py", line 809, in write_text
    with self.open(mode='w', encoding=encoding, errors=errors, newline=newline) as f:
         ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\pathlib\__init__.py", line 771, in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PermissionError: [Errno 13] Permission denied: 'C:\\Users\\CROWN-~1\\AppData\\Local\\Temp\\tmpgrbfm820\\snapshot.json'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<frozen os>", line 377, in walk
PermissionError: [WinError 5] Отказано в доступе: 'C:\\Users\\CROWN-~1\\AppData\\Local\\Temp\\tmpgrbfm820'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "D:\GPTMEAi-SEMASCRIPT\tests\test_write_gptmeai_readonly_snapshot_from_report.py", line 47, in test_write_snapshot_from_report_creates_expected_json
    with tempfile.TemporaryDirectory() as temp_dir:
         ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 971, in __exit__
    self.cleanup()
    ~~~~~~~~~~~~^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 975, in cleanup
    self._rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 955, in _rmtree
    _shutil.rmtree(name, onexc=onexc)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 852, in rmtree
    _rmtree_impl(path, dir_fd, onexc)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 689, in _rmtree_unsafe
    for dirpath, dirnames, filenames in results:
                                        ^^^^^^^
  File "<frozen os>", line 413, in walk
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\shutil.py", line 687, in onerror
    onexc(os.scandir, err.filename, err)
    ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 927, in onexc
    _resetperms(path)
    ~~~~~~~~~~~^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 287, in _resetperms
    _dont_follow_symlinks(_os.chmod, path, 0o700)
    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Crown-Aliy\AppData\Local\Programs\Python\Python314\Lib\tempfile.py", line 276, in _dont_follow_symlinks
    func(path, *args, follow_symlinks=False)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PermissionError: [WinError 5] Отказано в доступе: 'C:\\Users\\CROWN-~1\\AppData\\Local\\Temp\\tmpgrbfm820'

----------------------------------------------------------------------
Ran 161 tests in 0.503s

FAILED (errors=8)
```

### 4. `python -B tools\verify_bridge.py`

- Exit code: `0`
- Duration seconds: `1.327`

#### stdout

```text
LOCAL_VALIDATION=OK
DRY_RUN=OK
APPROVAL_GATE=OK
GPTMEAI_HEALTH=UNAVAILABLE error=<urlopen error timed out>
VERIFY_BRIDGE=OK
```

#### stderr

```text

```

### 5. `python -B tools\collect_source_references.py`

- Exit code: `0`
- Duration seconds: `0.169`

#### stdout

```text
WROTE=D:\GPTMEAi-SEMASCRIPT\source_references\GPTMEAi_SELECTED_FILES.md
WROTE=D:\GPTMEAi-SEMASCRIPT\source_references\SEMASCRIPT_SELECTED_FILES.md
WROTE=D:\GPTMEAi-SEMASCRIPT\source_references\MANIFEST.md
MISSING_COUNT=0
```

#### stderr

```text

```

## Safety

- No dependencies were installed by this wrapper.
- No live runtime startup is required by this wrapper.
- Reports are written under `reports/codex/`, not the project root.
- Source projects are referenced only by existing read-only source reference tooling.
