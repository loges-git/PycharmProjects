from pathlib import Path
import extract_msg


class MsgProcessor:
    """
    Processes .msg files and extracts ZIP attachments.
    """

    def __init__(self, msg_path: str | Path, incoming_folder: str | Path):
        self.msg_path = Path(msg_path)
        self.incoming_folder = Path(incoming_folder)

        if not self.msg_path.exists():
            raise FileNotFoundError(f"MSG file not found: {self.msg_path}")

        if not self.incoming_folder.exists():
            raise FileNotFoundError(
                f"Incoming folder not found: {self.incoming_folder}"
            )

    def extract_zip_attachments(self) -> list[Path]:
        """
        Extracts ZIP attachments from .msg file.
        Returns list of extracted ZIP paths.
        """
        extracted_files = []

        msg = extract_msg.Message(str(self.msg_path))
        msg_attachments = msg.attachments

        for attachment in msg_attachments:
            filename = attachment.longFilename or attachment.shortFilename

            if filename and filename.lower().endswith(".zip"):
                save_path = self.incoming_folder / filename

                with open(save_path, "wb") as f:
                    f.write(attachment.data)

                extracted_files.append(save_path)

        return extracted_files
