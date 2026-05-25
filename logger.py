import logging
import pathlib
from datetime import datetime

log_dir = pathlib.Path("logs")
log_dir.mkdir(exist_ok=True)

log_filename = log_dir / f"harness_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("asset-harness")
