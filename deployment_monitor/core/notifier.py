import threading
import winsound
import logging
import tkinter as tk

logger = logging.getLogger("deployment_monitor.notifier")


class Notifier:
    """
    Shows popup window and plays sound until acknowledged.
    """

    def __init__(self):
        self.stop_sound = False

    def _play_sound(self):
        while not self.stop_sound:
            winsound.Beep(1000, 700)
            winsound.Beep(1500, 700)

    def notify(self, message: str):
        """
        Show popup and play sound until user clicks OK.
        
        Args:
            message: Message to display
        """
        try:
            logger.info(f"Sending notification to user")
            self.stop_sound = False

            sound_thread = threading.Thread(target=self._play_sound)
            sound_thread.daemon = True
            sound_thread.start()
            logger.debug("Sound thread started")

            root = tk.Tk()
            root.title("Deployment Log Alert")
            root.geometry("400x150")

            label = tk.Label(root, text=message, wraplength=350)
            label.pack(pady=20)

            def acknowledge():
                logger.debug("User acknowledged notification")
                self.stop_sound = True
                root.destroy()

            button = tk.Button(root, text="Acknowledge", command=acknowledge)
            button.pack(pady=10)

            root.mainloop()
            logger.info("Notification dismissed")
        
        except Exception as e:
            logger.error(f"Error displaying notification: {e}", exc_info=True)
