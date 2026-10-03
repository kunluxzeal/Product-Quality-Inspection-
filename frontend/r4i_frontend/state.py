import reflex as rx

from .api import (
    get_json,
    post_json,
    HEALTH_URL,
    CLASSES_URL,
    SYSTEM_URL,
    PREDICT_CAMERA_URL,
)


class AppState(rx.State):

    # ========================================================
    # UI STATE
    # ========================================================

    analyzing: bool = False
    backend_online: bool = False

    error_message: str = ""

    # ========================================================
    # ANALYSIS RESULT
    # ========================================================

    prediction: str = ""
    confidence_percent: float = 0.0
    status: str = ""
    inference_time_ms: float = 0.0

    # ========================================================
    # PROBABILITIES
    # ========================================================

    probability_good: float = 0.0
    probability_bad: float = 0.0
    probability_rotten: float = 0.0
    probability_damaged: float = 0.0

    # ========================================================
    # MODEL INFORMATION
    # ========================================================

    model_name: str = ""
    input_shape: str = ""
    input_dtype: str = ""
    output_shape: str = ""

    number_of_classes: int = 0
    confidence_threshold: float = 0.60

    # ========================================================
    # SYSTEM INFORMATION
    # ========================================================

    platform: str = ""
    architecture: str = ""
    python_version: str = ""
    processor: str = ""
    runtime: str = ""

    @rx.var
    def confidence_text(self) -> str:
        return f"{self.confidence_percent:.2f}%"

    @rx.var
    def inference_text(self) -> str:
        return f"{self.inference_time_ms:.2f} ms"

    @rx.var
    def threshold_text(self) -> str:
        return f"{self.confidence_threshold * 100:.0f}%"

    # ========================================================
    # RUN CAMERA ANALYSIS
    # ========================================================

    async def run_analysis(self):

        self.analyzing = True
        self.error_message = ""

        try:

            result = await post_json(
                PREDICT_CAMERA_URL
            )

            self.prediction = result.get(
                "prediction",
                "Unknown",
            )

            self.confidence_percent = result.get(
                "confidence_percent",
                0.0,
            )

            self.status = result.get(
                "status",
                "",
            )

            self.inference_time_ms = result.get(
                "inference_time_ms",
                0.0,
            )

            probabilities = result.get(
                "probabilities",
                {},
            )

            # ------------------------------------------------
            # Store probabilities
            # ------------------------------------------------

            values = list(
                probabilities.values()
            )

            self.probability_good = (
                values[0] * 100
                if len(values) > 0
                else 0.0
            )

            self.probability_bad = (
                values[1] * 100
                if len(values) > 1
                else 0.0
            )

            self.probability_rotten = (
                values[2] * 100
                if len(values) > 2
                else 0.0
            )

            self.probability_damaged = (
                values[3] * 100
                if len(values) > 3
                else 0.0
            )

        except Exception as e:

            self.error_message = (
                f"Analysis failed: {str(e)}"
            )

        finally:

            self.analyzing = False

    # ========================================================
    # CLEAR RESULT
    # ========================================================

    def clear_result(self):

        self.prediction = ""
        self.confidence_percent = 0.0
        self.status = ""
        self.inference_time_ms = 0.0

        self.probability_good = 0.0
        self.probability_bad = 0.0
        self.probability_rotten = 0.0
        self.probability_damaged = 0.0

        self.error_message = ""

    # ========================================================
    # LOAD SYSTEM INFORMATION
    # ========================================================

    async def load_system_info(self):

        try:

            health = await get_json(
                HEALTH_URL
            )

            system = await get_json(
                SYSTEM_URL
            )

            classes = await get_json(
                CLASSES_URL
            )

            # ------------------------------------------------
            # Health
            # ------------------------------------------------

            self.backend_online = (
                health.get("status")
                == "healthy"
            )

            self.model_name = health.get(
                "model",
                "",
            )

            self.input_shape = str(
                health.get(
                    "input_shape",
                    "",
                )
            )

            self.input_dtype = health.get(
                "input_dtype",
                "",
            )

            self.output_shape = str(
                health.get(
                    "output_shape",
                    "",
                )
            )

            self.number_of_classes = health.get(
                "classes",
                0,
            )

            # ------------------------------------------------
            # Classes
            # ------------------------------------------------

            self.confidence_threshold = classes.get(
                "confidence_threshold",
                0.60,
            )

            # ------------------------------------------------
            # System
            # ------------------------------------------------

            self.platform = system.get(
                "platform",
                "",
            )

            self.architecture = system.get(
                "architecture",
                "",
            )

            self.python_version = system.get(
                "python",
                "",
            )

            self.processor = system.get(
                "processor",
                "",
            )

            self.runtime = system.get(
                "runtime",
                "",
            )

        except Exception as e:

            self.backend_online = False

            self.error_message = (
                f"Backend connection failed: {str(e)}"
            )