import io
import threading
import time

from PIL import Image
from picamera2 import Picamera2


class Camera:

    def __init__(
        self,
        width: int = 640,
        height: int = 480,
        jpeg_quality: int = 85,
    ):
        self.width = width
        self.height = height
        self.jpeg_quality = jpeg_quality

        self.camera = Picamera2()

        self.config = self.camera.create_video_configuration(
            main={
                "size": (self.width, self.height),
                "format": "BGR888",
            }
        )

        self.camera.configure(self.config)

        self.lock = threading.Lock()
        self.started = False

    def start(self):
        if not self.started:
            self.camera.start()
            self.started = True

            # Give the camera a moment to stabilize.
            time.sleep(0.5)

    def stop(self):
        if self.started:
            self.camera.stop()
            self.started = False

    def capture_image(self) -> Image.Image:
        if not self.started:
            self.start()

        with self.lock:
            frame = self.camera.capture_array()

        return Image.fromarray(frame)

    def capture_frame(self) -> bytes:
        image = self.capture_image()

        buffer = io.BytesIO()

        image.save(
            buffer,
            format="JPEG",
            quality=self.jpeg_quality,
        )

        return buffer.getvalue()

