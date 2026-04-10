from arkive.retrieval.vector.main import VectorDBBase
from arkive.retrieval.vector.type import VectorType
from arkive.config import (
    VECTOR_DB,
    ENABLE_QDRANT_MULTITENANCY_MODE,
    ENABLE_MILVUS_MULTITENANCY_MODE,
)


class Vector:
    @staticmethod
    def get_vector(vector_type: str) -> VectorDBBase:
        """
        get vector db instance by vector type
        """
        match vector_type:
            case VectorType.MILVUS:
                if ENABLE_MILVUS_MULTITENANCY_MODE:
                    from arkive.retrieval.vector.dbs.milvus_multitenancy import (
                        MilvusClient,
                    )

                    return MilvusClient()
                else:
                    from arkive.retrieval.vector.dbs.milvus import MilvusClient

                    return MilvusClient()
            case VectorType.QDRANT:
                if ENABLE_QDRANT_MULTITENANCY_MODE:
                    from arkive.retrieval.vector.dbs.qdrant_multitenancy import (
                        QdrantClient,
                    )

                    return QdrantClient()
                else:
                    from arkive.retrieval.vector.dbs.qdrant import QdrantClient

                    return QdrantClient()
            case VectorType.PINECONE:
                from arkive.retrieval.vector.dbs.pinecone import PineconeClient

                return PineconeClient()
            case VectorType.S3VECTOR:
                from arkive.retrieval.vector.dbs.s3vector import S3VectorClient

                return S3VectorClient()
            case VectorType.OPENSEARCH:
                from arkive.retrieval.vector.dbs.opensearch import OpenSearchClient

                return OpenSearchClient()
            case VectorType.PGVECTOR:
                from arkive.retrieval.vector.dbs.pgvector import PgvectorClient

                return PgvectorClient()
            case VectorType.OPENGAUSS:
                from arkive.retrieval.vector.dbs.opengauss import OpenGaussClient

                return OpenGaussClient()
            case VectorType.MARIADB_VECTOR:
                from arkive.retrieval.vector.dbs.mariadb_vector import (
                    MariaDBVectorClient,
                )

                return MariaDBVectorClient()
            case VectorType.ELASTICSEARCH:
                from arkive.retrieval.vector.dbs.elasticsearch import (
                    ElasticsearchClient,
                )

                return ElasticsearchClient()
            case VectorType.CHROMA:
                from arkive.retrieval.vector.dbs.chroma import ChromaClient

                return ChromaClient()
            case VectorType.ORACLE23AI:
                from arkive.retrieval.vector.dbs.oracle23ai import Oracle23aiClient

                return Oracle23aiClient()
            case VectorType.WEAVIATE:
                from arkive.retrieval.vector.dbs.weaviate import WeaviateClient

                return WeaviateClient()
            case _:
                raise ValueError(f'Unsupported vector type: {vector_type}')


VECTOR_DB_CLIENT = Vector.get_vector(VECTOR_DB)
