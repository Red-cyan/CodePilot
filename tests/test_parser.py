from app.services.parser import RepositoryParser


def test_parser_extracts_python_symbols(tmp_path):
    source = tmp_path / "sample.py"
    source.write_text(
        "import os\n\nclass Service:\n    def run(self):\n        return os.getcwd()\n",
        encoding="utf-8",
    )

    result = RepositoryParser().scan("repo-1", tmp_path)

    assert result.languages == {"python": 1}
    assert len(result.chunks) == 1
    assert {symbol.name for symbol in result.symbols} >= {"os", "Service", "run"}


def test_parser_reports_skipped_files(tmp_path):
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "ignored.py").write_text("print('skip')", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("not source", encoding="utf-8")
    (tmp_path / "empty.py").write_text("", encoding="utf-8")

    result = RepositoryParser().scan("repo-1", tmp_path)

    assert result.files_scanned == 3
    assert result.skipped_files == 3
    assert result.skip_reasons["ignored_directory"] == 1
    assert result.skip_reasons["unsupported_extension"] == 1
    assert result.skip_reasons["empty_file"] == 1
