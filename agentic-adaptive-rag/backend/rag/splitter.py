from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config.settings import Settings


class DocumentSplitter:

    def __init__(self) -> None:

        self.chunking_config = Settings().CHUNKING_CONFIG

        self._chunkers = {
            "pdf": self._create_recursive_splitter(
                self.chunking_config["pdf"]
            ),
            "docx": self._create_recursive_splitter(
                self.chunking_config["docx"]
            ),
            "web": self._create_recursive_splitter(
                self.chunking_config["web"]
            ),
        }

        self._strategy_map = {
            "pdf": self._split_pdf,
            "docx": self._split_docx,
            "csv": self._split_csv,
            "web": self._split_web,
        }

    def _create_recursive_splitter(
        self,
        config: dict,
    ) -> RecursiveCharacterTextSplitter:

        return RecursiveCharacterTextSplitter(
            chunk_size=config["chunk_size"],
            chunk_overlap=config["chunk_overlap"],
            separators=config["separators"],
        )

    def _split_pdf(
        self,
        document: Document,
    ) -> list[Document]:

        return self._chunkers["pdf"].split_documents([document])

    def _split_docx(
        self,
        document: Document,
    ) -> list[Document]:

        return self._chunkers["docx"].split_documents([document])

    def _split_web(
        self,
        document: Document,
    ) -> list[Document]:

        return self._chunkers["web"].split_documents([document])

    def _split_csv(
        self,
        document: Document,
    ) -> list[Document]:

        rows = document.page_content.splitlines()

        return [
            Document(
                page_content=row,
                metadata=document.metadata.copy(),
            )
            for row in rows
        ]

    def split(
        self,
        documents: list[Document],
    ) -> list[Document]:

        if not documents:
            return []

        chunks = []

        for document in documents:

            document_type = document.metadata.get("document_type")

            if not document_type:
                raise ValueError(
                    "Missing 'document_type' in document metadata."
                )

            split_method = self._strategy_map.get(document_type)

            if split_method is None:
                raise ValueError(
                    f"Unsupported document type: {document_type}"
                )

            chunks.extend(split_method(document))

        return self._enrich_metadata(chunks)

    def _enrich_metadata(
        self,
        chunks: list[Document],
    ) -> list[Document]:

        for index, chunk in enumerate(chunks):

            metadata = chunk.metadata

            source = metadata.get("source", "unknown")
            page = metadata.get("page", 0)

            source_name = Path(source).stem

            metadata["chunk_index"] = index

            metadata["chunk_id"] = (
                f"{source_name}_p{page}_c{index}"
            )

            metadata["chunk_size"] = len(chunk.page_content)

        return chunks