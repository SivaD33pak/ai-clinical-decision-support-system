import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.database.supabase import get_supabase_client
from app.core.config import settings
from app.core.logging import logger

# In-memory store for fallback mode
_local_uploads_store: Dict[str, Dict[str, Any]] = {}
_local_predictions_store: List[Dict[str, Any]] = []

class StorageRepository:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.upload_dir = Path(settings.UPLOAD_DIRECTORY)

    async def save_uploaded_file(self, filename: str, content: bytes) -> Dict[str, Any]:
        upload_id = f"upl_{uuid.uuid4().hex[:12]}"
        ext = os.path.splitext(filename)[1].lower()
        saved_filename = f"{upload_id}{ext}"
        local_filepath = self.upload_dir / saved_filename

        # Save locally
        with open(local_filepath, "wb") as f:
            f.write(content)

        public_url = f"/static/uploads/{saved_filename}"

        # Upload to Supabase Storage if active
        if self.supabase is not None:
            try:
                self.supabase.storage.from_("xray-images").upload(
                    path=saved_filename,
                    file=content,
                    file_options={"content-type": f"image/{ext.replace('.', '')}"}
                )
                public_url = self.supabase.storage.from_("xray-images").get_public_url(saved_filename)
                logger.info(f"Uploaded {saved_filename} to Supabase xray-images storage.")
            except Exception as e:
                logger.warning(f"Supabase storage upload failed: {e}. Using local storage reference.")

        upload_record = {
            "upload_id": upload_id,
            "filename": filename,
            "file_path": str(local_filepath),
            "public_url": public_url,
            "file_size_bytes": len(content)
        }
        _local_uploads_store[upload_id] = upload_record
        return upload_record

    async def get_upload_record(self, upload_id: str) -> Optional[Dict[str, Any]]:
        return _local_uploads_store.get(upload_id)


class PredictionRepository:
    def __init__(self):
        self.supabase = get_supabase_client()

    async def save_prediction(self, prediction_data: Dict[str, Any]) -> Dict[str, Any]:
        prediction_id = f"pred_{uuid.uuid4().hex[:12]}"
        created_at = datetime.now(timezone.utc).isoformat()

        record = {
            "id": prediction_id,
            "user_id": prediction_data.get("user_id", "user_default_001"),
            "module": prediction_data.get("module", "XRAY"),
            "disease": prediction_data.get("disease", "Normal"),
            "confidence": prediction_data.get("confidence", 0.9500),
            "image_url": prediction_data.get("image_url", ""),
            "heatmap_url": prediction_data.get("heatmap_url", ""),
            "created_at": created_at
        }

        # Save to Supabase DB if active
        if self.supabase is not None:
            try:
                # Ensure valid UUID for user_id
                raw_user_id = record["user_id"]
                try:
                    uuid_obj = uuid.UUID(raw_user_id)
                    db_user_id = str(uuid_obj)
                except ValueError:
                    db_user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, raw_user_id))

                # Ensure user exists
                try:
                    self.supabase.table("users").upsert({
                        "id": db_user_id,
                        "email": f"{raw_user_id}@hospital.org" if "@" not in raw_user_id else raw_user_id,
                        "name": "Dr. Clinician"
                    }).execute()
                except Exception:
                    pass

                db_data = {
                    "user_id": db_user_id,
                    "module": record["module"],
                    "disease": record["disease"],
                    "confidence": record["confidence"],
                    "image_url": record["image_url"],
                    "heatmap_url": record["heatmap_url"]
                }
                res = self.supabase.table("predictions").insert(db_data).execute()
                if res.data and len(res.data) > 0:
                    inserted = res.data[0]
                    record["id"] = inserted.get("id", prediction_id)
                logger.info(f"Saved prediction record to Supabase DB.")
            except Exception as e:
                logger.warning(f"Supabase prediction insert failed: {e}. Using local store fallback.")

        _local_predictions_store.append(record)
        return record
