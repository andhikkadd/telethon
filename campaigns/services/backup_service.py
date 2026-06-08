import os
import shutil
import zipfile
import subprocess
import logging
from datetime import datetime
from pathlib import Path
import config

logger = logging.getLogger("BackupService")

class BackupService:
    @staticmethod
    def is_gpg_available() -> bool:
        """Check if gpg command line tool is available on the system."""
        try:
            subprocess.run(["gpg", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    @staticmethod
    async def create_backup() -> list[str]:
        """
        Creates backup archives for campaigns, assistant modules, and root system files separately.
        Returns a list of absolute paths to the generated backup files.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Define base directories relative to this file
        service_file_path = Path(__file__).resolve()
        campaigns_dir = service_file_path.parent.parent
        project_root = campaigns_dir.parent
        assistant_dir = project_root / "assistant"
        
        backups_dir = campaigns_dir / "backups"
        backups_dir.mkdir(parents=True, exist_ok=True)
        
        backup_files = []
        
        # 1. CREATE CAMPAIGNS BACKUP
        camp_zip_path = backups_dir / f"backup_campaigns_{timestamp}.zip"
        try:
            with zipfile.ZipFile(camp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add campaigns source files
                camp_files = [
                    "main.py", "config.py", "database.py", "telegram_client.py",
                    "commands.py", "scheduler.py", "web_panel.py",
                    "server_status.py", "utils.py", "requirements.txt", "README.md"
                ]
                for f_name in camp_files:
                    f_path = campaigns_dir / f_name
                    if f_path.exists():
                        zipf.write(str(f_path), arcname=f_name)
                
                # Add campaigns services
                services_dir = campaigns_dir / "services"
                if services_dir.is_dir():
                    for svc_file in services_dir.glob("*.py"):
                        zipf.write(str(svc_file), arcname=os.path.join("services", svc_file.name))
                        
                # Add templates
                templates_dir = campaigns_dir / "templates"
                if templates_dir.is_dir():
                    for t_file in templates_dir.rglob("*"):
                        if t_file.is_file():
                            zipf.write(str(t_file), arcname=os.path.join("templates", str(t_file.relative_to(templates_dir))))
                            
                # Add database
                db_path = project_root / "data" / "bot.db"
                if db_path.exists():
                    zipf.write(str(db_path), arcname="data/bot.db")
                elif os.path.exists(config.DATABASE_PATH):
                    zipf.write(config.DATABASE_PATH, arcname="data/bot.db")
                    
                # Add sessions
                sess_dir = campaigns_dir / "sessions"
                if sess_dir.is_dir():
                    for session_file in sess_dir.glob("*.session"):
                        zipf.write(str(session_file), arcname=os.path.join("sessions", session_file.name))
                    for journal_file in sess_dir.glob("*.session-journal"):
                        zipf.write(str(journal_file), arcname=os.path.join("sessions", journal_file.name))
                        
                # Add campaigns env
                camp_env = campaigns_dir / ".env"
                if camp_env.exists():
                    zipf.write(str(camp_env), arcname=".env")
                    
            logger.info(f"Campaigns backup created: {camp_zip_path}")
            backup_files.append(str(camp_zip_path.resolve()))
        except Exception as e:
            logger.error(f"Failed to create campaigns backup: {e}", exc_info=True)
            
        # 2. CREATE ASSISTANT BACKUP
        asst_zip_path = backups_dir / f"backup_assistant_{timestamp}.zip"
        try:
            if assistant_dir.is_dir():
                with zipfile.ZipFile(asst_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Add assistant source files
                    for f in assistant_dir.glob("*.py"):
                        zipf.write(str(f), arcname=os.path.join("assistant", f.name))
                    
                    # Add assistant services
                    asst_svc_dir = assistant_dir / "services"
                    if asst_svc_dir.is_dir():
                        for f in asst_svc_dir.glob("*.py"):
                            zipf.write(str(f), arcname=os.path.join("assistant", "services", f.name))
                            
                    # Add assistant templates
                    asst_temp_dir = assistant_dir / "templates"
                    if asst_temp_dir.is_dir():
                        for f in asst_temp_dir.rglob("*"):
                            if f.is_file():
                                zipf.write(str(f), arcname=os.path.join("assistant", "templates", str(f.relative_to(asst_temp_dir))))
                                
                    # Add assistant env
                    asst_env = assistant_dir / ".env"
                    if asst_env.exists():
                        zipf.write(str(asst_env), arcname="assistant/.env")
                        
                    # Add database
                    db_path = project_root / "data" / "bot.db"
                    if db_path.exists():
                        zipf.write(str(db_path), arcname="data/bot.db")
                        
                logger.info(f"Assistant backup created: {asst_zip_path}")
                backup_files.append(str(asst_zip_path.resolve()))
        except Exception as e:
            logger.error(f"Failed to create assistant backup: {e}", exc_info=True)
            
        # 3. CREATE ROOT BACKUP (portal, runner, global .env)
        root_zip_path = backups_dir / f"backup_system_root_{timestamp}.zip"
        try:
            with zipfile.ZipFile(root_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                root_files = ["portal.py", "runner.py", ".env", "requirements.txt"]
                for f_name in root_files:
                    path = project_root / f_name
                    if path.exists():
                        zipf.write(str(path), arcname=f_name)
            logger.info(f"System Root backup created: {root_zip_path}")
            backup_files.append(str(root_zip_path.resolve()))
        except Exception as e:
            logger.error(f"Failed to create system root backup: {e}", exc_info=True)
            
        # Encrypt with GPG if available and allowed
        gpg_ok = BackupService.is_gpg_available()
        from utils import sanitize_logs
        
        final_files = []
        for zip_p in backup_files:
            zip_path = Path(zip_p)
            if gpg_ok:
                if not config.BACKUP_PASSWORD:
                    if zip_path.exists():
                        zip_path.unlink()
                    raise ValueError("GPG is available but BACKUP_PASSWORD is not set in .env")
                
                gpg_path = zip_path.with_suffix(zip_path.suffix + ".gpg")
                try:
                    process = subprocess.Popen(
                        [
                            "gpg", "--symmetric", "--batch", "--yes",
                            "--passphrase-fd", "0", "--cipher-algo", "AES256",
                            "-o", str(gpg_path), str(zip_path)
                        ],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    stdout, stderr = process.communicate(input=config.BACKUP_PASSWORD)
                    if process.returncode != 0:
                        raise RuntimeError(f"GPG encryption failed: {sanitize_logs(stderr)}")
                    
                    if zip_path.exists():
                        zip_path.unlink()
                    final_files.append(str(gpg_path.resolve()))
                except Exception as e:
                    if gpg_path.exists():
                        gpg_path.unlink()
                    if zip_path.exists():
                        zip_path.unlink()
                    raise RuntimeError(f"GPG Encryption error: {sanitize_logs(str(e))}")
            else:
                if config.ALLOW_UNENCRYPTED_BACKUP:
                    final_files.append(str(zip_path.resolve()))
                else:
                    if zip_path.exists():
                        zip_path.unlink()
                    raise RuntimeError(
                        "GPG is not available and ALLOW_UNENCRYPTED_BACKUP=false. "
                        "Secure backup cannot be generated."
                    )
        return final_files

    @staticmethod
    def clean_backup_file(file_path: str):
        """Remove the backup file from the disk if DELETE_LOCAL_BACKUP_AFTER_SEND is enabled."""
        if not config.DELETE_LOCAL_BACKUP_AFTER_SEND:
            logger.info(f"Local backup deletion skipped as DELETE_LOCAL_BACKUP_AFTER_SEND is false: {file_path}")
            return
            
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Temporary backup file deleted from disk: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete backup file {file_path}: {e}")

backup_svc = BackupService()
