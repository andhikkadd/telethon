import logging
from datetime import datetime
from database import db

logger = logging.getLogger("TemplateService")

class TemplateService:
    @staticmethod
    async def get_all_templates(is_override: int = 0) -> list:
        return await db.fetchall(
            "SELECT * FROM templates WHERE is_override = ? ORDER BY id ASC",
            (is_override,)
        )

    @staticmethod
    async def get_active_templates(include_override: bool = True) -> list:
        if include_override:
            from services.settings_service import settings_svc
            override_active = await settings_svc.get_setting("override_template_active", "0")
            if override_active == "1":
                override_until_str = await settings_svc.get_setting("override_template_until", "")
                if override_until_str:
                    try:
                        override_until = datetime.fromisoformat(override_until_str)
                        if datetime.now() < override_until:
                            # Return override templates strictly (can be empty if none created)
                            return await db.fetchall("SELECT * FROM templates WHERE is_override = 1 AND is_active = 1")
                    except Exception as e:
                        logger.warning(f"Error parsing global override_template_until: {e}")
                # If override is active but expired or invalid, we don't fall back if include_override is True.
                # However, the user wants override mode to strictly prevent fallback when turned ON.
                # So we return empty list if override is ON but has expired, OR we can let it fall back.
                # Wait, the user said: "mode override kunyalain buat promosiin event ini, misal ada event lagi tapi beda, tinggal ubah templates teks mode overridenya...".
                # If they set override_until, they want it active UNTIL that time. Once expired, it returns to regular.
                # So if it's expired, it should fall back to regular templates.
                # Thus, we fall through to regular templates if datetime.now() >= override_until!
        return await db.fetchall("SELECT * FROM templates WHERE (is_override = 0 OR is_override IS NULL) AND is_active = 1")

    @staticmethod
    async def add_template(text: str, is_override: int = 0) -> int:
        if not text:
            raise ValueError("Template content cannot be empty.")
        stripped = text.strip()
        if not stripped:
            raise ValueError("Template content cannot be empty.")
        if len(stripped) > 4096:
            raise ValueError("Template content exceeds Telegram's 4096 character limit.")
            
        now_str = datetime.now().isoformat()
        template_id = await db.execute(
            "INSERT INTO templates (text, is_override, is_active, created_at, updated_at) "
            "VALUES (?, ?, 1, ?, ?)",
            (stripped, is_override, now_str, now_str)
        )
        logger.info(f"Added template ID {template_id} (is_override={is_override})")
        return template_id

    @staticmethod
    async def delete_template(template_id: int):
        await db.execute("DELETE FROM templates WHERE id = ?", (template_id,))
        logger.info(f"Deleted template ID {template_id}")

template_svc = TemplateService()
