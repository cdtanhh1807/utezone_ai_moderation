import uuid
import io
import asyncio
from datetime import timedelta
from fastapi import UploadFile
from core.minio import minio_client, MINIO_BUCKET
from minio.error import S3Error

class FileService:

    @staticmethod
    async def upload_file(file: UploadFile) -> str:
        """
        Upload file lên MinIO, trả về file_id.
        """
        file_id = f"{uuid.uuid4()}_{file.filename}"
        content = await file.read()
        content_stream = io.BytesIO(content)
        content_stream.seek(0)

        # Kiểm tra và tạo bucket nếu chưa tồn tại
        try:
            if not minio_client.bucket_exists(MINIO_BUCKET):
                minio_client.make_bucket(MINIO_BUCKET)
        except S3Error as e:
            print("Lỗi khi kiểm tra/ tạo bucket:", e)
            raise

        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: minio_client.put_object(
                MINIO_BUCKET,
                object_name=file_id,
                data=content_stream,
                length=len(content),
                content_type=file.content_type
            )
        )

        return file_id

    @staticmethod
    def get_file_url(file_id: str, expires_seconds: int = 3600) -> str:
        """
        Trả về URL truy cập file tạm thời (mặc định 1 giờ).
        """
        return minio_client.presigned_get_object(
            MINIO_BUCKET,
            file_id,
            expires=timedelta(seconds=expires_seconds)
        )
