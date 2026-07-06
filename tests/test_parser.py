from app.services.parser import RepositoryParser


def test_parser_extracts_python_symbols(tmp_path):
    source = tmp_path / "sample.py"
    source.write_text(
        "import os\n\nclass Service:\n    def run(self):\n        return os.getcwd()\n",
        encoding="utf-8",
    )

    chunks, symbols, languages = RepositoryParser().scan("repo-1", tmp_path)

    assert languages == {"python": 1}
    assert len(chunks) == 1
    assert {symbol.name for symbol in symbols} >= {"os", "Service", "run"}
