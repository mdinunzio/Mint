import config as cfg
import os


if not os.path.isdir(cfg.DATA_DIR):
    os.mkdir(cfg.DATA_DIR)
