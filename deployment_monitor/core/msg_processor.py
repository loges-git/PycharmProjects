import logging
from pathlib import Path
import extract_msg

logger = logging.getLogger("deployment_monitor.msg_processor")


class MsgProcessor:
    """
    Processes .msg files and extracts ZIP attachments.
    """

    def __init__(self, msg_path: str | Path, incoming_folder: str | Path):
        try:
            self.msg_path = Path(msg_path)
            self.incoming_folder = Path(incoming_folder)
            
            logger.debug(f"Initializing MsgProcessor - msg: {self.msg_path}, folder: {self.incoming_folder}")

            if not self.msg_path.exists():
                raise FileNotFoundError(f"MSG file not found: {self.msg_path}")

            if not self.incoming_folder.exists():
                raise FileNotFoundError(
                    f"Incoming folder not found: {self.incoming_folder}"
                )
            
            logger.info(f"MsgProcessor initialized successfully")
        
        except FileNotFoundError as e:
            logger.error(f"Initialization failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during MsgProcessor initialization: {e}")
            raise

    def extract_zip_attachments(self) -> list[Path]:
        """
        Extracts ZIP attachments from .msg file.
        Returns list of extracted ZIP paths.
        
        Returns:
            List of Path objects for extracted ZIPs
            
        Raises:
            IOError: If MSG file reading fails
            OSError: If file writing fails
        """
        try:
            logger.info(f"Starting ZIP extraction from MSG: {self.msg_path.name}")
            extracted_files = []

            msg = extract_msg.Message(str(self.msg_path))
            msg_attachments = msg.attachments
            
            logger.debug(f"Found {len(msg_attachments)} attachments in message")

            for attachment in msg_attachments:
                filename = attachment.longFilename or attachment.shortFilename

                if filename and filename.lower().endswith(".zip"):
                    save_path = self.incoming_folder / filename
                    
                    logger.debug(f"Extracting ZIP attachment: {filename}")

                    with open(save_path, "wb") as f:
                        f.write(attachment.data)

                    extracted_files.append(save_path)
                    logger.info(f"Successfully extracted: {filename}")

            logger.info(f"ZIP extraction complete: {len(extracted_files)} files extracted")
            return extracted_files
        
        except IOError as e:
            logger.error(f"Error reading MSG file: {e}")
            raise
        except OSError as e:
            logger.error(f"Error writing extracted files: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error extracting ZIP attachments: {e}", exc_info=True)
            raise
