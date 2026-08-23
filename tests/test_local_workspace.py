import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from local_workspace import (
    FORMAT_NAME,
    FORMAT_VERSION,
    LocalWorkspaceError,
    LocalWorkspaceService,
    atomic_save,
    canonical_json,
    empty_document,
    init_workspace,
    load_workspace,
    validate_document,
)


def artifact(artifact_id="artifact-1", title="Title", content="Content"):
    return {
        "artifact_id": artifact_id,
        "title": title,
        "content": content,
    }


class LocalWorkspaceModelStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.path = self.root / "workspace.json"

    def assert_error_code(self, expected, callable_object, *args, **kwargs):
        with self.assertRaises(LocalWorkspaceError) as caught:
            callable_object(*args, **kwargs)
        self.assertEqual(expected, caught.exception.error_code)
        return caught.exception

    def test_empty_workspace_validates(self):
        self.assertEqual(empty_document(), validate_document(empty_document()))

    def test_canonical_serialization_is_stable_sorted_and_has_one_final_newline(self):
        document = empty_document()
        document["artifacts"] = [artifact("z", "Zulu", "last"), artifact("a", "Alpha", "first")]

        first = canonical_json(document)
        second = canonical_json(document)

        self.assertEqual(first, second)
        self.assertTrue(first.endswith("\n"))
        self.assertFalse(first.endswith("\n\n"))
        parsed = json.loads(first)
        self.assertEqual(["a", "z"], [item["artifact_id"] for item in parsed["artifacts"]])
        self.assertEqual(["format", "version", "artifacts"], list(parsed))
        self.assertEqual(
            ["artifact_id", "title", "content"],
            list(parsed["artifacts"][0]),
        )

    def test_unicode_content_round_trips_unchanged(self):
        content = "  Привет, мир 🌍\n第二行\n  "
        document = empty_document()
        document["artifacts"] = [artifact("unicode", "Знание", content)]

        atomic_save(document, self.path)

        self.assertEqual(content, load_workspace(self.path)["artifacts"][0]["content"])
        self.assertIn("Привет, мир 🌍", self.path.read_text(encoding="utf-8"))

    def test_invalid_format_and_version_are_separate_errors(self):
        wrong_format = empty_document()
        wrong_format["format"] = "other.workspace"
        wrong_version = empty_document()
        wrong_version["version"] = 2

        self.assert_error_code("UNSUPPORTED_WORKSPACE_FORMAT", validate_document, wrong_format)
        self.assert_error_code("UNSUPPORTED_WORKSPACE_VERSION", validate_document, wrong_version)

    def test_boolean_version_is_rejected_as_invalid_content(self):
        document = empty_document()
        document["version"] = True

        self.assert_error_code("INVALID_WORKSPACE", validate_document, document)

    def test_malformed_json_is_reported_separately(self):
        self.path.write_text('{"format":', encoding="utf-8")

        self.assert_error_code("INVALID_JSON", load_workspace, self.path)

    def test_unknown_and_missing_keys_are_rejected(self):
        unknown_top = empty_document()
        unknown_top["extra"] = 1
        missing_top = empty_document()
        del missing_top["artifacts"]
        unknown_artifact = empty_document()
        unknown_artifact["artifacts"] = [{**artifact(), "extra": "no"}]
        missing_artifact = empty_document()
        missing_artifact["artifacts"] = [{"artifact_id": "a", "title": "A"}]

        for document in (unknown_top, missing_top, unknown_artifact, missing_artifact):
            with self.subTest(document=document):
                self.assert_error_code("INVALID_WORKSPACE", validate_document, document)

    def test_duplicate_artifact_ids_are_rejected_after_id_canonicalization(self):
        document = empty_document()
        document["artifacts"] = [artifact("same"), artifact(" same ", "Other", "Other")]

        self.assert_error_code("DUPLICATE_ARTIFACT_ID", validate_document, document)

    def test_failed_validation_never_rewrites_original(self):
        init_workspace(self.path)
        before = self.path.read_bytes()
        invalid = empty_document()
        invalid["unknown"] = True

        self.assert_error_code("INVALID_WORKSPACE", atomic_save, invalid, self.path)

        self.assertEqual(before, self.path.read_bytes())

    def test_init_refuses_overwrite(self):
        init_workspace(self.path)
        before = self.path.read_bytes()

        self.assert_error_code("WORKSPACE_ALREADY_EXISTS", init_workspace, self.path)

        self.assertEqual(before, self.path.read_bytes())

    def test_add_rejects_duplicate_and_invalid_values_without_rewrite(self):
        service = LocalWorkspaceService()
        service.init(self.path)
        service.add(self.path, "id-1", "Title", "Content")
        before = self.path.read_bytes()

        self.assert_error_code(
            "DUPLICATE_ARTIFACT_ID",
            service.add,
            self.path,
            " id-1 ",
            "Other",
            "Other",
        )
        self.assertEqual(before, self.path.read_bytes())

        for artifact_id, title, content in (
            (" ", "Title", "Content"),
            ("id-2", " ", "Content"),
            ("id-2", "Title", ""),
        ):
            with self.subTest(artifact_id=artifact_id, title=title, content=content):
                self.assert_error_code(
                    "INVALID_ARGUMENT",
                    service.add,
                    self.path,
                    artifact_id,
                    title,
                    content,
                )
                self.assertEqual(before, self.path.read_bytes())

    def test_atomic_replacement_path_is_used_for_init_and_add(self):
        from local_workspace import storage

        real_replace = os.replace
        with mock.patch.object(storage.os, "replace", wraps=real_replace) as replace_mock:
            init_workspace(self.path)
        self.assertEqual(1, replace_mock.call_count)
        source, target = replace_mock.call_args.args
        self.assertEqual(self.path, Path(target))
        self.assertEqual(self.path.parent, Path(source).parent)

        service = LocalWorkspaceService()
        with mock.patch.object(storage.os, "replace", wraps=real_replace) as replace_mock:
            service.add(self.path, "id", "Title", "Content")
        self.assertEqual(1, replace_mock.call_count)
        self.assertEqual(self.path, Path(replace_mock.call_args.args[1]))

    def test_failed_pre_replace_write_cleans_owned_temp_only(self):
        from local_workspace import storage

        service = LocalWorkspaceService()
        service.init(self.path)
        unrelated = self.root / "unrelated.keep"
        unrelated.write_text("preserve", encoding="utf-8")
        before_workspace = self.path.read_bytes()
        before_names = {item.name for item in self.root.iterdir()}

        with mock.patch.object(storage.os, "replace", side_effect=OSError("simulated")):
            self.assert_error_code(
                "WRITE_FAILED",
                service.add,
                self.path,
                "id",
                "Title",
                "Content",
            )

        self.assertEqual(before_workspace, self.path.read_bytes())
        self.assertEqual("preserve", unrelated.read_text(encoding="utf-8"))
        self.assertEqual(before_names, {item.name for item in self.root.iterdir()})

    def test_missing_workspace_and_nonexistent_parent_are_distinct_user_errors(self):
        self.assert_error_code("WORKSPACE_NOT_FOUND", load_workspace, self.path)
        self.assert_error_code(
            "INVALID_ARGUMENT",
            init_workspace,
            self.root / "missing-parent" / "workspace.json",
        )

    def test_url_and_network_paths_are_rejected(self):
        self.assert_error_code("INVALID_ARGUMENT", load_workspace, "https://example.test/a.json")
        self.assert_error_code("INVALID_ARGUMENT", load_workspace, "\\\\server\\share\\a.json")


class LocalWorkspaceServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.path = Path(self.temp_dir.name) / "workspace.json"
        self.service = LocalWorkspaceService()
        self.service.init(self.path)

    def test_add_persists_across_new_service_instance_and_list_is_sorted(self):
        self.service.add(self.path, "zeta", "Last", "Z")
        self.service.add(self.path, "alpha", "First", "A")

        reopened = LocalWorkspaceService().list_artifacts(self.path)

        self.assertEqual(["alpha", "zeta"], [item["artifact_id"] for item in reopened])

    def test_unicode_casefold_search_matches_id_title_and_content(self):
        self.service.add(
            self.path,
            "Straße-ID",
            "Заголовок",
            "Καλημέρα, мир 🌍",
        )

        for query in ("STRASSE", "ЗАГОЛОВОК", "МИР"):
            with self.subTest(query=query):
                results = LocalWorkspaceService().search(self.path, query)
                self.assertEqual(["Straße-ID"], [item["artifact_id"] for item in results])

    def test_empty_query_is_rejected(self):
        for query in ("", "  \t"):
            with self.subTest(query=query):
                with self.assertRaises(LocalWorkspaceError) as caught:
                    self.service.search(self.path, query)
                self.assertEqual("INVALID_ARGUMENT", caught.exception.error_code)

    def test_list_search_and_validate_do_not_change_bytes(self):
        self.service.add(self.path, "id", "Знание", "Содержимое")
        before = self.path.read_bytes()

        self.service.list_artifacts(self.path)
        self.service.search(self.path, "знание")
        self.service.validate(self.path)

        self.assertEqual(before, self.path.read_bytes())

    def test_format_constants_are_exact(self):
        self.assertEqual("semantic-ai-os.local-workspace", FORMAT_NAME)
        self.assertEqual(1, FORMAT_VERSION)


if __name__ == "__main__":
    unittest.main()
