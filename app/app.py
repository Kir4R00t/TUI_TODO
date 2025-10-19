import logging
import tui # app front-end

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(
        filename='logs/logs.log', 
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
        )
    logger.info(f'Logging started ...')

    tui.TasksTUI().run()
