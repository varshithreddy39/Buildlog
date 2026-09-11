from pathlib import Path
from urllib.parse import urlparse

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    CSVLoader,
    Docx2txtLoader,
    PyPDFLoader,
    WebBaseLoader,
)


class DocumentLoader:
    """
    Loads documents from supported file types and web URLs.

    Supported Sources:
        - PDF
        - DOCX
        - CSV
        - URL

    Returns:
        List[Document]
    """

    def __init__(self) -> None:
        self._loader_map = {
            ".pdf": self._load_pdf,
            ".docx": self._load_docx,
            ".csv": self._load_csv,
        }

    def load(self, source: str) -> list[Document]:
        """
        Public entry point for loading documents.

        Args:
            source: Local file path or URL.

        Returns:
            List[Document]
        """
        if self._is_url(source):
            return self._load_url(source)

        return self._load_file(source)

    def _load_file(self, file_path: str) -> list[Document]:
        """
        Loads a supported local file.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        extension = path.suffix.lower()

        loader_method = self._loader_map.get(extension)

        if loader_method is None:
            supported = ", ".join(self._loader_map.keys())
            raise ValueError(
                f"Unsupported file type: '{extension}'. "
                f"Supported types: {supported}"
            )

        return loader_method(str(path))

    def _load_pdf(self, file_path: str) -> list[Document]:
        """
        Load a PDF document.
        """
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        return self._add_document_type(
            documents,
            "pdf",
        )

    def _load_docx(self, file_path: str) -> list[Document]:
        """
        Load a DOCX document.
        """
        loader = Docx2txtLoader(file_path)
        documents = loader.load()

        return self._add_document_type(
            documents,
            "docx",
        )

    def _load_csv(self, file_path: str) -> list[Document]:
        """
        Load a CSV document.
        """
        loader = CSVLoader(file_path)
        documents = loader.load()

        return self._add_document_type(
            documents,
            "csv",
        )

    def _load_url(self, url: str) -> list[Document]:
        """
        Load a webpage.
        """
        loader = WebBaseLoader(url)
        documents = loader.load()

        return self._add_document_type(
            documents,
            "web",
        )

    def _add_document_type(
        self,
        documents: list[Document],
        document_type: str,
    ) -> list[Document]:
        """
        Add document type to each document's metadata.
        """
        for document in documents:
            document.metadata["document_type"] = document_type

        return documents

    @staticmethod
    def _is_url(source: str) -> bool:
        """
        Check whether the provided source is a valid URL.
        """
        parsed = urlparse(source)
        return bool(parsed.scheme and parsed.netloc)